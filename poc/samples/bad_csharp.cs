// MaterialService.cs
// Sample C# file with deliberate violations — used for Quality Gate demo
// Violations cover DAS/CDAS standards: async, HttpClient, DI, secrets, exceptions, logging

using System;
using System.Data.SqlClient;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading;
using System.Threading.Tasks;
using System.Transactions;
using System.Web;

public class materialService   // violation: should be PascalCase (CLARION)
{
    // violation: hardcoded connection string — must use Key Vault (CLARION)
    private string conn = "Server=prod-db;Database=AppDB;User Id=sa;Password=Admin@123;";

    // violation: hardcoded email override in production code path (CLARION)
    private string debugRecipient = "testuser@company.com";

    // violation: DbContext-style object held as instance field, not scoped (LUMEN)
    private AppDbContext _context = new AppDbContext();

    // -----------------------------------------------------------------------
    // ASYNC ANTI-PATTERNS
    // -----------------------------------------------------------------------

    // violation: .Result blocks the thread — deadlock risk in ASP.NET (CLARION + VECTOR)
    public string GetAccessToken()
    {
        return AzureAdHelper.GetTokenAsync().Result;
    }

    // violation: .Wait() — same deadlock risk (CLARION + VECTOR)
    public void DeleteBlob(string blobName)
    {
        _blobClient.DeleteAsync(blobName).Wait();
    }

    // violation: async void — exceptions cannot be caught by caller (CLARION)
    public async void SyncInventory()
    {
        await Task.Delay(1000);
        DoWork();
    }

    // violation: CancellationToken not accepted or propagated (CLARION)
    public async Task<int> SaveRecordAsync(RecordModel model)
    {
        _context.Records.Add(model);
        return await _context.SaveChangesAsync(); // should pass CancellationToken
    }

    // violation: TransactionScope without AsyncFlowOption.Enabled (LUMEN)
    public async Task<bool> CreateWithItemsAsync(RecordModel record, List<ItemModel> items)
    {
        using (var tx = new TransactionScope(TransactionScopeOption.Required,
            new TransactionOptions { IsolationLevel = IsolationLevel.ReadCommitted }))
        // violation: missing TransactionScopeAsyncFlowOption.Enabled
        {
            await SaveRecordAsync(record);
            tx.Complete();
            return true;
        }
    }

    // -----------------------------------------------------------------------
    // HTTPCLIENT ANTI-PATTERN
    // -----------------------------------------------------------------------

    // violation: new HttpClient() inside a method — socket exhaustion risk (CLARION + VECTOR)
    private HttpClient GetClient()
    {
        HttpClient client = new HttpClient();
        client.BaseAddress = new Uri("https://graph.microsoft.com/v1.0/");
        client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", GetAccessToken());
        client.DefaultRequestHeaders.Accept.Add(
            new MediaTypeWithQualityHeaderValue("application/json"));
        return client;
    }

    // -----------------------------------------------------------------------
    // EXCEPTION HANDLING VIOLATIONS
    // -----------------------------------------------------------------------

    // violation: returns raw e.Message to caller — information disclosure (CLARION)
    public IHttpActionResult GetItem(int id)
    {
        try
        {
            var item = _context.Items.Find(id);
            return Ok(item);
        }
        catch (Exception e)
        {
            return InternalServerError(new Exception(e.Message)); // exposes internals
        }
    }

    // violation: empty catch block — swallows exception silently (CLARION + LUMEN)
    public void LogActivity(string activity)
    {
        try
        {
            File.AppendAllText("C:\\logs\\activity.log", activity);
        }
        catch (IOException ex)
        {
            // empty — exception lost
        }
        catch (Exception ex)
        {
            // empty — exception lost
        }
    }

    // -----------------------------------------------------------------------
    // INPUT VALIDATION VIOLATION
    // -----------------------------------------------------------------------

    // violation: JObject parameter with no validation, no ModelState check (CLARION)
    public IHttpActionResult CreateItem([FromBody] Newtonsoft.Json.Linq.JObject jsonItem)
    {
        var model = jsonItem.ToObject<ItemModel>(); // no validation before processing
        _context.Items.Add(model);
        _context.SaveChanges();
        return Ok();
    }

    // -----------------------------------------------------------------------
    // FILE UPLOAD VIOLATION
    // -----------------------------------------------------------------------

    // violation: no file size or type validation — DoS / memory exhaustion risk (CLARION + VECTOR)
    public void ProcessUpload(HttpPostedFileBase file)
    {
        var memory = new MemoryStream();
        file.InputStream.CopyTo(memory); // no size limit
        var bytes = memory.ToArray();
        SaveAttachment(Convert.ToBase64String(bytes));
    }

    // -----------------------------------------------------------------------
    // EF / DATA ACCESS VIOLATIONS
    // -----------------------------------------------------------------------

    // violation: no .AsNoTracking() on read-only query (LUMEN)
    public List<ItemViewModel> GetAllItems()
    {
        return _context.Items
            .OrderByDescending(i => i.CreatedDate)
            .ToList(); // missing .AsNoTracking()
    }

    // violation: N+1 query pattern — separate query per record in loop (LUMEN)
    public List<RecordViewModel> GetRecordsWithItems(List<int> recordIds)
    {
        var result = new List<RecordViewModel>();
        foreach (var id in recordIds)
        {
            var items = _context.Items.Where(i => i.RecordId == id).ToList(); // N queries
            result.Add(new RecordViewModel { RecordId = id, Items = items });
        }
        return result;
    }

    // -----------------------------------------------------------------------
    // DI VIOLATION
    // -----------------------------------------------------------------------

    // violation: manual instantiation of dependency (CLARION)
    public void ProcessBatch()
    {
        var repo = new ItemRepository(new AppDbContext()); // tight coupling, untestable
        var items = repo.GetPending();
        foreach (var item in items)
        {
            repo.MarkProcessed(item);
        }
    }

    // -----------------------------------------------------------------------
    // LOGGING VIOLATION
    // -----------------------------------------------------------------------

    // violation: string concatenation logging, no structured template, no ILogger<T> (CLARION)
    public void LogEvent(string eventType, string user, string message)
    {
        var entry = "[" + DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "] "
                  + eventType + " | " + user + " | " + message;
        File.AppendAllText("C:\\logs\\app.log", entry + Environment.NewLine);
    }

    // -----------------------------------------------------------------------
    // NAMING + COMPLEXITY VIOLATIONS
    // -----------------------------------------------------------------------

    public void ProcessPayment(int id, string cardNumber, string cvv, decimal amount,
        string currency, string merchantId, string customerId, string orderId)
        // violation: too many parameters (LUMEN)
    {
        // violation: SQL injection — string concatenation (CLARION)
        string query = "SELECT * FROM Payments WHERE CustomerId = '"
                     + customerId + "' AND Amount = " + amount;

        SqlConnection connection = new SqlConnection(conn); // violation: not in using block
        SqlCommand cmd = new SqlCommand(query, connection);
        connection.Open();
        var reader = cmd.ExecuteReader();

        if (reader.HasRows)
        {
            if (amount > 0)
            {
                if (currency == "USD")
                {
                    if (cardNumber.Length == 16)
                    {
                        if (cvv.Length == 3) // violation: 5-level deep nesting (LUMEN)
                        {
                            Console.WriteLine("Card: " + cardNumber); // violation: logging sensitive data
                            DoCharge(amount, cardNumber);
                        }
                    }
                }
            }
        }

        int x = 1048576; // violation: magic number (CLARION)
        Thread.Sleep(3000); // violation: magic number + blocking sleep
    }

    private void DoCharge(decimal amount, string card) { }
    private void SaveAttachment(string data) { }
    private void DoWork() { }
}
