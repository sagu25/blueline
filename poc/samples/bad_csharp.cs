// PaymentService.cs
// This file contains multiple coding standard violations for demo purposes

using System;
using System.Data.SqlClient;
using System.IO;

public class paymentservice   // violation: should be PascalCase
{
    private string conn = "Server=prod-db;Database=Payments;User Id=sa;Password=Admin@123;";  // violation: hardcoded secret

    public void ProcessPayment(int id, string cardNumber, string cvv, decimal amount, string currency, string merchantId, string customerId, string orderId)  // violation: too many parameters
    {
        // violation: SQL injection - string concatenation
        string query = "SELECT * FROM Payments WHERE CustomerId = '" + customerId + "' AND Amount = " + amount;

        SqlConnection connection = new SqlConnection(conn);   // violation: not disposed with using
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
                        if (cvv.Length == 3)   // violation: deep nesting (5 levels)
                        {
                            Console.WriteLine("Processing: " + cardNumber);  // violation: logging sensitive data
                            DoCharge(amount, cardNumber);
                        }
                    }
                }
            }
        }

        // Dead code below
        // var backup = ProcessBackup(id);
        // SendEmail(customerId);

        int x = 1048576;  // violation: magic number
        System.Threading.Thread.Sleep(3000);  // violation: magic number
    }

    public void ProcessRefund(int id, string cardNumber, string cvv, decimal amount, string currency, string merchantId, string customerId, string orderId)
    {
        // violation: duplicate logic copied from ProcessPayment
        string query = "SELECT * FROM Payments WHERE CustomerId = '" + customerId + "' AND Amount = " + amount;

        SqlConnection connection = new SqlConnection(conn);
        SqlCommand cmd = new SqlCommand(query, connection);
        connection.Open();
        var reader = cmd.ExecuteReader();

        if (reader.HasRows)
        {
            DoRefund(amount, cardNumber);
        }
    }

    private void DoCharge(decimal amount, string card) { /* impl */ }
    private void DoRefund(decimal amount, string card) { /* impl */ }
}
