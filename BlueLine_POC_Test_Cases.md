# Project BlueLine POC — Test Cases
### Sample Inputs & Expected Outputs for Each Agent

**Version:** 1.0 | **Date:** 2026-04-15

> **How to use this document:**
> Each test case tells you exactly what to paste into the app and what the AI should flag.
> Use these to demonstrate the app confidently — you already know what's coming.

---

## Tab 1 — Quality Gate (CLARION + LUMEN)

---

### TC-QG-01 | SQL Injection + Hardcoded Secret (C#)

**What it demonstrates:** CLARION catching a security violation and a standards violation together.

**Language:** csharp

**Paste this code:**
```csharp
public class userService
{
    private string connectionString = "Server=prod-db;Password=Admin@123;";

    public User GetUser(string userId)
    {
        string query = "SELECT * FROM Users WHERE Id = '" + userId + "'";
        var conn = new SqlConnection(connectionString);
        conn.Open();
        return conn.ExecuteQuery(query);
    }
}
```

**What CLARION should flag:**

| # | Severity | Violation | Fix it should suggest |
|---|---|---|---|
| 1 | ERROR | Class name `userService` should be `UserService` (PascalCase) | Rename to `UserService` |
| 2 | ERROR | Hardcoded password in connection string | Move to Azure Key Vault or environment variable |
| 3 | ERROR | SQL string concatenation — SQL injection risk | Use parameterized query with `SqlParameter` |
| 4 | WARNING | `SqlConnection` not disposed | Wrap in `using` statement |

**What LUMEN should flag:**
- Method doing two things (building query + executing) — Single Responsibility violation

**Overall score expected:** 2–4 / 10

---

### TC-QG-02 | Deep Nesting + Magic Numbers (C#)

**What it demonstrates:** LUMEN catching complexity and maintainability issues.

**Language:** csharp

**Paste this code:**
```csharp
public class OrderProcessor
{
    public void Process(Order order)
    {
        if (order != null)
        {
            if (order.Items.Count > 0)
            {
                if (order.CustomerId > 0)
                {
                    if (order.TotalAmount > 500)
                    {
                        if (order.TotalAmount < 99999)
                        {
                            decimal tax = order.TotalAmount * 0.18m;
                            decimal discount = order.TotalAmount * 0.05m;
                            decimal shipping = 149;
                            decimal final = order.TotalAmount + tax - discount + shipping;
                            Console.WriteLine("Final: " + final);
                        }
                    }
                }
            }
        }
    }
}
```

**What CLARION should flag:**

| # | Severity | Violation |
|---|---|---|
| 1 | ERROR | Magic numbers: `0.18m`, `0.05m`, `149`, `500`, `99999` — use named constants |
| 2 | WARNING | `Console.WriteLine` in business logic — use proper logging |

**What LUMEN should flag:**

| # | Severity | Smell |
|---|---|---|
| 1 | MAJOR | Deep Nesting — 5 levels of if statements |
| 2 | MAJOR | Magic Numbers — tax rate, discount rate, shipping cost hardcoded |
| 3 | MINOR | Long method — multiple calculation responsibilities |

**Refactor it should suggest:** Extract guard clauses (early return pattern), extract constants, extract tax/discount/shipping into separate methods.

**Overall score expected:** 3–5 / 10

---

### TC-QG-03 | Clean C# Code (Negative Test)

**What it demonstrates:** Agents give a clean result when code is correct — proving no false positives.

**Language:** csharp

**Paste this code:**
```csharp
public class OrderService : IOrderService
{
    private const decimal TaxRate = 0.18m;
    private const decimal DiscountRate = 0.05m;
    private const decimal StandardShipping = 149m;

    private readonly IOrderRepository _repository;

    public OrderService(IOrderRepository repository)
    {
        _repository = repository;
    }

    public async Task<OrderResult> ProcessOrderAsync(int customerId, int orderId)
    {
        var order = await _repository.GetByIdAsync(orderId);
        if (order == null) return OrderResult.NotFound();

        var total = CalculateTotal(order.Amount);
        await _repository.UpdateAsync(order.Id, total);

        return OrderResult.Success(total);
    }

    private decimal CalculateTotal(decimal amount)
    {
        return amount + (amount * TaxRate) - (amount * DiscountRate) + StandardShipping;
    }
}
```

**What agents should flag:** Nothing (or at most 1–2 minor info-level suggestions)

**Overall score expected:** 8–10 / 10

**Why this test matters:** Shows the audience the agents don't cry wolf — clean code gets a clean result.

---

### TC-QG-04 | Angular/TypeScript Violations

**What it demonstrates:** CLARION works for TypeScript/Angular, not just C#.

**Language:** typescript

**Paste this code:**
```typescript
@Component({
  selector: 'app-dashboard',
  template: `<div [innerHTML]="welcomeMessage"></div>`
})
export class DashboardComponent implements OnInit {

  welcomeMessage: any;
  userData: any;
  private timer: any;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.timer = interval(3000).subscribe(() => {
      this.http.get('https://api.example.com/data').subscribe((res: any) => {
        this.userData = res;
        this.welcomeMessage = '<b>Welcome ' + res.name + '</b>';
        document.getElementById('header').innerHTML = res.title;
      });
    });
  }
}
```

**What CLARION should flag:**

| # | Severity | Violation |
|---|---|---|
| 1 | ERROR | `[innerHTML]` binding with unsanitized data — XSS risk |
| 2 | ERROR | Direct DOM manipulation via `document.getElementById` |
| 3 | ERROR | Hardcoded string concatenation into HTML — XSS risk |
| 4 | WARNING | `any` type used 3 times — specify explicit types |
| 5 | WARNING | Observable `timer` never unsubscribed — memory leak |
| 6 | WARNING | No `ChangeDetectionStrategy.OnPush` |

**What LUMEN should flag:**
- Nested subscriptions (subscribe inside subscribe) — anti-pattern, use `switchMap` instead
- Component doing data fetching on a timer — should be in a service

**Overall score expected:** 2–4 / 10

---

### TC-QG-05 | Duplicate Code + Long Parameter List (C#)

**What it demonstrates:** LUMEN's duplicate code and parameter smell detection.

**Language:** csharp

**Paste this code:**
```csharp
public class ReportService
{
    public void GenerateSalesReport(string title, string region, string currency,
        DateTime from, DateTime to, string format, bool includeChart, string recipient)
    {
        var data = _db.GetSales(region, from, to);
        var report = BuildReport(title, data, currency, format, includeChart);
        _emailService.Send(recipient, report);
        _logger.Log("Sales report sent to " + recipient);
    }

    public void GenerateRefundReport(string title, string region, string currency,
        DateTime from, DateTime to, string format, bool includeChart, string recipient)
    {
        var data = _db.GetRefunds(region, from, to);
        var report = BuildReport(title, data, currency, format, includeChart);
        _emailService.Send(recipient, report);
        _logger.Log("Refund report sent to " + recipient);
    }
}
```

**What CLARION should flag:**

| # | Severity | Violation |
|---|---|---|
| 1 | WARNING | String concatenation in logger — use structured logging |

**What LUMEN should flag:**

| # | Severity | Smell |
|---|---|---|
| 1 | MAJOR | Duplicate Code — `GenerateSalesReport` and `GenerateRefundReport` are identical except for the data source |
| 2 | MAJOR | Long Parameter List — 8 parameters, extract into a `ReportRequest` object |

**Refactor it should suggest:** Create a `ReportRequest` class, extract shared logic into a `GenerateReport(ReportRequest request, Func<...> dataSource)` method.

---

## Tab 2 — Security Loop (BULWARK)

---

### TC-SEC-01 | SQL Injection — CRITICAL

**What it demonstrates:** BULWARK classifying a confirmed critical vulnerability with attack scenario.

**Finding description:**
```
Category: SQL Injection
Severity: Critical
File: Repositories/CustomerRepository.cs
Line: 34

The GetCustomerByEmail method constructs a SQL query by directly
concatenating the email parameter from the HTTP request into the
query string. No input validation or parameterization is used.

Vulnerable code:
public Customer GetCustomerByEmail(string email)
{
    string sql = "SELECT * FROM Customers WHERE Email = '" + email + "'";
    return _db.ExecuteQuery<Customer>(sql).FirstOrDefault();
}

This method is called from the public login endpoint /api/auth/login.
```

**Expected BULWARK output:**

| Field | Expected Value |
|---|---|
| Classification | CRITICAL |
| Confidence | 90%+ |
| OWASP | A03:2021 — Injection |
| Attack scenario | Attacker can log in as any user, dump entire Customers table, or drop database |
| Fix | Parameterized query using `SqlCommand` with `SqlParameter` |

---

### TC-SEC-02 | XSS (Cross-Site Scripting) — CRITICAL

**What it demonstrates:** BULWARK catching a frontend XSS vulnerability.

**Finding description:**
```
Category: Cross-Site Scripting (XSS)
Severity: Critical
File: src/app/comments/comment-list.component.ts
Line: 28

The component renders user-submitted comment content directly
into the DOM using innerHTML without sanitization.

Vulnerable code:
displayComment(comment: Comment) {
    const el = document.getElementById('comment-' + comment.id);
    el.innerHTML = comment.body;
}

The comment.body value comes from the database and was originally
submitted by an end user through a public form.
```

**Expected BULWARK output:**

| Field | Expected Value |
|---|---|
| Classification | CRITICAL |
| OWASP | A03:2021 — Injection (XSS) |
| Attack scenario | Attacker submits a comment with `<script>` tag that runs in other users' browsers — steals session tokens, redirects to phishing site |
| Fix | Use Angular's `DomSanitizer.sanitizeHtml()` or Angular template binding `{{ comment.body }}` instead of `innerHTML` |

---

### TC-SEC-03 | Hardcoded Secret — HIGH

**What it demonstrates:** BULWARK catching a secrets management issue.

**Finding description:**
```
Category: Hardcoded Credentials
Severity: High
File: Services/PaymentGatewayService.cs
Line: 12

A third-party payment gateway API key is hardcoded directly
in the source code as a private field.

Vulnerable code:
public class PaymentGatewayService
{
    private readonly string _apiKey = "live_sk_abc123xyz789secretkey";

    public async Task<PaymentResult> ChargeAsync(decimal amount, string token)
    {
        // uses _apiKey to call payment gateway
    }
}
```

**Expected BULWARK output:**

| Field | Expected Value |
|---|---|
| Classification | HIGH |
| OWASP | A02:2021 — Cryptographic Failures |
| Attack scenario | If the repository is ever accessed by an unauthorized person (breach, ex-employee, accidental public repo), the live payment API key is exposed and can be used to make fraudulent charges |
| Fix | Store in Azure Key Vault, inject via `IConfiguration` or `ISecretClient` |

---

### TC-SEC-04 | False Positive Test

**What it demonstrates:** BULWARK correctly identifying a false positive — proving it doesn't over-flag.

**Finding description:**
```
Category: SQL Injection
Severity: Medium
File: Repositories/ProductRepository.cs
Line: 19

Fortify flagged potential SQL injection in the GetProductById method.

Code:
public async Task<Product> GetProductByIdAsync(int productId)
{
    const string sql = "SELECT * FROM Products WHERE Id = @productId";
    var parameters = new { productId };
    return await _connection.QuerySingleOrDefaultAsync<Product>(sql, parameters);
}
```

**Expected BULWARK output:**

| Field | Expected Value |
|---|---|
| Classification | FALSE_POSITIVE |
| Confidence | 85%+ |
| False positive reason | The query uses a named parameter `@productId` with Dapper's parameterized query — user input is never concatenated into the SQL string. This is the correct, safe pattern. |

**Why this test matters:** If BULWARK flagged this as a real finding it would be useless. Showing it correctly identifies a false positive builds trust.

---

### TC-SEC-05 | Path Traversal — CRITICAL

**What it demonstrates:** BULWARK handling a file system vulnerability.

**Finding description:**
```
Category: Path Traversal
Severity: Critical
File: Controllers/FileController.cs
Line: 45

The DownloadFile endpoint accepts a filename parameter from the
query string and uses it directly to build a file path without
validation.

Vulnerable code:
[HttpGet("download")]
public IActionResult DownloadFile(string fileName)
{
    string path = @"C:\App\Reports\" + fileName;
    byte[] fileBytes = System.IO.File.ReadAllBytes(path);
    return File(fileBytes, "application/octet-stream", fileName);
}
```

**Expected BULWARK output:**

| Field | Expected Value |
|---|---|
| Classification | CRITICAL |
| OWASP | A01:2021 — Broken Access Control |
| Attack scenario | Attacker passes `../../Windows/System32/config/SAM` as filename to read system files outside the intended directory |
| Fix | Validate filename contains no path separators or `..`, resolve full path and verify it starts with the allowed base directory |

---

## Tab 3 — Certificate Loop (TIMELINE)

---

### TC-CERT-01 | CRITICAL — Expiring in 5 Days

**What it demonstrates:** TIMELINE triggering the most urgent response.

**Fill in:**

| Field | Value |
|---|---|
| Subject / Domain | `payments.core-main.internal` |
| Expiry Date | *(Today's date + 5 days in YYYY-MM-DD)* |
| Environments | Dev, QA, Production (IIS) |
| CA Type | Internal PKI (C&M Portal) |
| Notes | Used by the Payments API. Wildcard cert. Owner: Pankaj Pathak |

**Expected TIMELINE output:**

| Field | Expected Value |
|---|---|
| Urgency | CRITICAL |
| Risk Level | Critical |
| Summary | Certificate expires in 5 days — immediate action required |
| Action Plan | Should include: raise internal PKI request today, expedite issuance, validate on Dev, deploy to Prod same day with emergency change |
| Automation Possible | Partial (COURIER can raise request, HARBOUR deploys — but 5-day window is tight) |

---

### TC-CERT-02 | RENEWAL NEEDED — 22 Days Remaining

**What it demonstrates:** Normal renewal workflow with enough lead time.

**Fill in:**

| Field | Value |
|---|---|
| Subject / Domain | `admin.core-main.com` |
| Expiry Date | *(Today's date + 22 days in YYYY-MM-DD)* |
| Environments | QA, Production (Azure App Service) |
| CA Type | DigiCert |
| Notes | External-facing admin portal. Requires InfoSec approval for external cert renewal. |

**Expected TIMELINE output:**

| Field | Expected Value |
|---|---|
| Urgency | RENEWAL_NEEDED |
| Risk Level | High |
| Renewal Path | external_ca |
| Automation Possible | Yes (DigiCert has API — COURIER can automate) |
| Action Plan | Should include: trigger DigiCert API renewal, download cert, validate SANs, deploy to QA first, then Prod approval gate |

---

### TC-CERT-03 | OK — 180 Days Remaining

**What it demonstrates:** TIMELINE correctly doing nothing when there's no urgency.

**Fill in:**

| Field | Value |
|---|---|
| Subject / Domain | `internal-api.core-main.local` |
| Expiry Date | *(Today's date + 180 days in YYYY-MM-DD)* |
| Environments | Dev only |
| CA Type | Internal PKI (C&M Portal) |
| Notes | Dev environment cert only. Low priority. |

**Expected TIMELINE output:**

| Field | Expected Value |
|---|---|
| Urgency | OK |
| Risk Level | Low |
| Summary | Certificate is healthy — no action needed at this time |
| Action Plan | Monitor only — set reminder at 30-day mark |

**Why this test matters:** Shows TIMELINE doesn't raise false alarms — it only acts when needed.

---

### TC-CERT-04 | EXPIRED — Already Past Expiry

**What it demonstrates:** TIMELINE handling the worst-case scenario — an already expired cert.

**Fill in:**

| Field | Value |
|---|---|
| Subject / Domain | `legacy-portal.core-main.internal` |
| Expiry Date | `2026-03-01` *(a date in the past)* |
| Environments | Production (IIS) |
| CA Type | Internal PKI (C&M Portal) |
| Notes | Legacy portal used by operations team. Was supposed to be renewed last quarter. |

**Expected TIMELINE output:**

| Field | Expected Value |
|---|---|
| Urgency | EXPIRED |
| Risk Level | Critical |
| Summary | Certificate has already expired — site is currently showing security errors to users |
| Action Plan | Emergency renewal required. Raise P1 request immediately. Temporary self-signed cert as interim measure. |
| Risks | Should list: users seeing browser warnings, services failing SSL handshake, possible downtime |

---

## Test Execution Summary Table

Use this during the demo to track which tests you've run:

| Test ID | Tab | Scenario | Expected Result | Status |
|---|---|---|---|---|
| TC-QG-01 | Quality Gate | SQL Injection + Hardcoded Secret (C#) | 3–4 violations, score 2–4/10 | |
| TC-QG-02 | Quality Gate | Deep Nesting + Magic Numbers (C#) | 2–3 smells, score 3–5/10 | |
| TC-QG-03 | Quality Gate | Clean C# code | No violations, score 8–10/10 | |
| TC-QG-04 | Quality Gate | Angular XSS + Memory Leak | 4–6 violations | |
| TC-QG-05 | Quality Gate | Duplicate Code + Long Params | 2 major smells | |
| TC-SEC-01 | Security | SQL Injection | CRITICAL, 90%+ confidence | |
| TC-SEC-02 | Security | XSS | CRITICAL | |
| TC-SEC-03 | Security | Hardcoded Secret | HIGH | |
| TC-SEC-04 | Security | False Positive | FALSE_POSITIVE | |
| TC-SEC-05 | Security | Path Traversal | CRITICAL | |
| TC-CERT-01 | Certificate | Expiring in 5 days | CRITICAL | |
| TC-CERT-02 | Certificate | Expiring in 22 days | RENEWAL_NEEDED | |
| TC-CERT-03 | Certificate | 180 days remaining | OK | |
| TC-CERT-04 | Certificate | Already expired | EXPIRED | |

---

## Recommended Demo Order

If you have **15 minutes**, run these 5 in this order — they tell the best story:

| Order | Test | Why |
|---|---|---|
| 1st | TC-QG-01 | Opens strong — catches SQL injection and hardcoded password immediately |
| 2nd | TC-QG-03 | Shows clean code gets a clean result — no false alarms |
| 3rd | TC-SEC-01 | Best security demo — attack scenario is convincing |
| 4th | TC-SEC-04 | False positive test — builds trust that the AI isn't over-flagging |
| 5th | TC-CERT-01 | Closes with urgency — 5-day expiry gets people's attention |

---

*End of Test Cases Document — Project BlueLine POC v1.0*
