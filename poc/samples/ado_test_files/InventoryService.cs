using System;
using System.Collections.Generic;
using System.Data.SqlClient;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using System.Transactions;

namespace App.Business
{
    public class inventoryService   // should be PascalCase
    {
        private string _connectionString = "Server=prod-sql01;Database=InventoryDB;User Id=appuser;Password=P@ssw0rd!2024;";

        private AppDbContext _db = new AppDbContext();   // held as instance field — not scoped

        // ── Token fetch ──────────────────────────────────────────────────────
        // .Result blocks the thread — deadlock risk in ASP.NET sync context
        public string GetServiceToken()
        {
            return TokenProvider.FetchTokenAsync("inventory-api").Result;
        }

        // ── External API call ────────────────────────────────────────────────
        // new HttpClient() inside a method — socket exhaustion risk
        public async Task<string> CallWarehouseApi(string endpoint)
        {
            HttpClient client = new HttpClient();
            client.BaseAddress = new Uri("https://warehouse-api.internal/");
            client.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", GetServiceToken());

            var response = await client.GetAsync(endpoint);
            return await response.Content.ReadAsStringAsync();
        }

        // ── Stock lookup ─────────────────────────────────────────────────────
        // SQL injection — string concatenation in query
        public List<StockItem> SearchStock(string itemCode, string location)
        {
            var results = new List<StockItem>();

            string query = "SELECT * FROM Stock WHERE ItemCode = '" + itemCode +
                           "' AND Location = '" + location + "'";

            SqlConnection conn = new SqlConnection(_connectionString);
            SqlCommand cmd = new SqlCommand(query, conn);
            conn.Open();
            var reader = cmd.ExecuteReader();

            while (reader.Read())
            {
                results.Add(new StockItem
                {
                    Id       = (int)reader["Id"],
                    ItemCode = reader["ItemCode"].ToString(),
                    Quantity = (int)reader["Quantity"]
                });
            }

            return results;
        }

        // ── Bulk transfer ─────────────────────────────────────────────────────
        // TransactionScope in async method without AsyncFlowOption.Enabled
        // CancellationToken not accepted or propagated
        public async Task<bool> TransferStockAsync(int fromLocationId, int toLocationId, List<StockItem> items)
        {
            using (var tx = new TransactionScope(TransactionScopeOption.Required,
                new TransactionOptions { IsolationLevel = System.Transactions.IsolationLevel.ReadCommitted }))
            {
                foreach (var item in items)
                {
                    // N+1: separate DB query per item inside a loop
                    var existing = _db.StockItems
                        .Where(s => s.ItemCode == item.ItemCode && s.LocationId == toLocationId)
                        .FirstOrDefault();

                    if (existing != null)
                        existing.Quantity += item.Quantity;
                    else
                        _db.StockItems.Add(item);

                    await _db.SaveChangesAsync();   // transaction context lost here without AsyncFlowOption
                }

                tx.Complete();
                return true;
            }
        }

        // ── Report export ─────────────────────────────────────────────────────
        // No file size or type validation — memory exhaustion risk
        public string ImportStockFromFile(HttpPostedFileBase file)
        {
            var memory = new MemoryStream();
            file.InputStream.CopyTo(memory);    // no size limit
            var content = System.Text.Encoding.UTF8.GetString(memory.ToArray());
            return ParseCsv(content);
        }

        // ── Logging ──────────────────────────────────────────────────────────
        // Empty catch block — exception swallowed silently
        public void LogTransfer(int fromId, int toId, int quantity)
        {
            try
            {
                File.AppendAllText("C:\\logs\\transfers.log",
                    DateTime.Now + " | " + fromId + " -> " + toId + " | qty: " + quantity);
            }
            catch (IOException ex)
            {
                // swallowed
            }
        }

        // ── Error response ────────────────────────────────────────────────────
        // Raw exception message returned to caller — information disclosure
        public IHttpActionResult GetStockLevel(string itemCode)
        {
            try
            {
                var item = _db.StockItems.Find(itemCode);
                return Ok(item);
            }
            catch (Exception ex)
            {
                return InternalServerError(new Exception(ex.Message));
            }
        }

        // ── Read-only query without AsNoTracking ─────────────────────────────
        public List<StockItem> GetAllStock()
        {
            return _db.StockItems
                .OrderBy(s => s.ItemCode)
                .ToList();   // missing .AsNoTracking()
        }

        private string ParseCsv(string content) { return content; }
    }
}
