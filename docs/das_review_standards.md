# DAS Engineering Review Standards
# .NET / ASP.NET Core — CDAS-Aligned Quality Gate Rules

**Version:** 1.0
**Scope:** Custom application code reviews — .NET (C#) and Angular (TypeScript)
**Alignment:** Digital Architecture System (DAS) | CDAS Compliance | SAST Readiness

---

## 1. Async / Threading (CRITICAL)

Blocking async calls are a leading cause of deadlocks and thread pool starvation in
ASP.NET applications. These patterns must never appear in production code.

| Anti-Pattern | Why It Is Dangerous | Required Fix |
|---|---|---|
| `.Result` on an async method | Blocks the calling thread; deadlocks in ASP.NET sync context | Convert caller to `async/await` |
| `.Wait()` on a Task | Same deadlock risk as `.Result` | Convert caller to `async/await` |
| `async void` methods | Exceptions cannot be caught by the caller | Use `async Task` except for event handlers |
| Missing `CancellationToken` | Long-running operations cannot be cancelled | Add `CancellationToken` to every async method signature and propagate it |
| `TransactionScope` without `AsyncFlowOption.Enabled` | Transaction context is lost across `await` boundaries | Always pass `TransactionScopeAsyncFlowOption.Enabled` in async code |

**DAS Rule:** All new code must be fully async. `.Result` and `.Wait()` are prohibited.

---

## 2. HttpClient Instantiation (CRITICAL)

Creating `new HttpClient()` inside methods is a well-known anti-pattern that causes
socket exhaustion because sockets are not released immediately after disposal.

**Prohibited pattern:**
```csharp
// DO NOT DO THIS
private HttpClient GetClient()
{
    var client = new HttpClient();
    client.BaseAddress = new Uri("https://api.example.com/");
    return client;
}
```

**Required pattern (.NET 6+):**
```csharp
// Register once at startup
builder.Services.AddHttpClient<MyService>();

// Inject via constructor
public MyService(HttpClient client) { _client = client; }
```

**Required pattern (.NET Framework 4.8.x):**
```csharp
// Single static instance shared across all calls
private static readonly HttpClient _client = new HttpClient();
```

**DAS Rule:** `IHttpClientFactory` is mandatory for .NET LTS. Static instance is acceptable only for .NET Framework maintenance codebases.

---

## 3. Dependency Injection (HIGH)

Manual instantiation with `new ClassName()` inside controllers and business classes
creates tight coupling, prevents unit testing, and gives no control over object lifetime.

**Prohibited pattern:**
```csharp
// DO NOT DO THIS
public class OrderController : ApiController
{
    public IHttpActionResult GetOrder(int id)
    {
        var repo = new OrderRepository(new AppDbContext()); // tight coupling
        return Ok(repo.Get(id));
    }
}
```

**Required pattern:**
```csharp
public class OrderController : ApiController
{
    private readonly IOrderRepository _repo;
    public OrderController(IOrderRepository repo) { _repo = repo; }
}
```

For .NET Framework 4.8.x: use Unity.WebApi, Autofac.WebApi2, or Simple Injector.
Register all services with appropriate lifetimes (Transient / Scoped / Singleton).

**DAS Rule:** Constructor injection is mandatory. No `new` instantiation of services inside controllers or business classes.

---

## 4. Secrets & Hardcoded Values (CRITICAL)

Hardcoded credentials, client IDs, email addresses, or environment-specific values in
source code are a security violation and a compliance risk.

**Prohibited:**
- Connection strings in source files
- API keys, client secrets, or GUIDs identifying tenants or applications
- Email addresses used as override recipients in production code paths
- Feature flags implemented as hardcoded `if` blocks rather than configuration

**Required:**
- All secrets stored in Azure Key Vault
- All configuration values in `appsettings.{environment}.json` or environment variables
- Test-mode behaviour controlled by a configuration flag, not by hardcoded recipients

**DAS Rule:** Zero secrets in source. SAST scanning will flag any credential-like string literal.

---

## 5. Exception Handling (HIGH)

Returning raw exception messages (`e.Message`, `e.ToString()`, stack traces) to API
callers is both a security vulnerability (information disclosure) and a poor UX pattern.

**Prohibited:**
```csharp
catch (Exception e)
{
    return BuildErrorResponse(e.Message); // exposes internal paths and types to caller
}
```

**Also prohibited:** Empty catch blocks that swallow exceptions silently.
```csharp
catch (IOException ex)
{
    // empty — exception is lost
}
```

**Required:**
```csharp
catch (Exception ex)
{
    _logger.LogError(ex, "Operation failed for request {CorrelationId}", correlationId);
    return StatusCode(500, new { error = "An unexpected error occurred.", code = "ERR_500" });
}
```

Implement a global exception filter (`IExceptionFilter` / middleware) for consistent handling.

**DAS Rule:** No raw exception messages to callers. No empty catch blocks. All exceptions logged with correlation ID.

---

## 6. Input Validation (HIGH)

Accepting loosely-typed parameters (`JObject`, `dynamic`, `object`) without validation
allows invalid or malicious data to reach the business layer.

**Prohibited:**
```csharp
public IHttpActionResult CreateItem([FromBody] JObject json)
{
    var model = json.ToObject<ItemModel>(); // no validation
    _service.Create(model);
}
```

**Required:**
```csharp
public IHttpActionResult CreateItem([FromBody] CreateItemRequest request)
{
    if (!ModelState.IsValid)
        return BadRequest(ModelState);

    _service.Create(request);
}
```

Use FluentValidation or DataAnnotations. Return `400 BadRequest` with structured validation errors.

**DAS Rule:** All external inputs must be validated at the controller boundary before reaching the business layer.

---

## 7. File Upload Security (HIGH)

File upload endpoints that load entire file contents into memory without size or type
validation are a Denial-of-Service vector and a memory exhaustion risk.

**Prohibited:**
```csharp
var stream = new MemoryStream();
file.InputStream.CopyTo(stream); // no size limit — attacker can exhaust server memory
```

**Required:**
```csharp
const int MaxFileSizeBytes = 10 * 1024 * 1024; // 10 MB
if (file.ContentLength > MaxFileSizeBytes)
    return BadRequest("File exceeds maximum allowed size.");

var allowedTypes = new[] { ".pdf", ".xlsx", ".csv" };
var ext = Path.GetExtension(file.FileName).ToLowerInvariant();
if (!allowedTypes.Contains(ext))
    return BadRequest("File type not permitted.");
```

Stream large files rather than loading entirely into memory.

---

## 8. CORS Configuration (HIGH)

Allowing all origins (`*`) while also enabling `SupportsCredentials = true` is a
CSRF vulnerability. Browsers block this combination by spec — but permissive CORS
in any form expands the attack surface.

**Prohibited:**
```csharp
var cors = new EnableCorsAttribute("*", "*", "*");
cors.SupportsCredentials = true;
```

**Required:**
```csharp
var cors = new EnableCorsAttribute("https://app.yourcompany.com", "*", "GET,POST,PUT");
```

Use environment-specific allowed origin lists. Never use wildcard in production.

---

## 9. EF / Data Access Patterns (MEDIUM)

### 9.1 Missing AsNoTracking
Read-only queries that do not call `.AsNoTracking()` cause EF to track every entity
in the change tracker — wasting memory and CPU with no benefit.

```csharp
// Required for all read-only queries
var items = _db.Orders
    .AsNoTracking()
    .Where(o => o.Status == OrderStatus.Active)
    .ToList();
```

### 9.2 N+1 Query Pattern
Issuing separate database queries inside a loop multiplies round trips linearly.

```csharp
// Prohibited — N+1
foreach (var order in orders)
{
    var items = _db.OrderItems.Where(i => i.OrderId == order.Id).ToList();
}

// Required — single query with Include
var orders = _db.Orders.Include(o => o.Items).AsNoTracking().ToList();
```

### 9.3 DbContext Lifetime
DbContext must be scoped per HTTP request. Holding a single DbContext instance across
requests causes stale data, memory leaks, and thread-safety issues.

Register as `Scoped` in the DI container. Never hold DbContext as a static or singleton reference.

---

## 10. Structured Logging (MEDIUM)

Custom logging implementations using `string.Format` or `+` concatenation cannot be
queried by log analytics tools and do not support correlation IDs.

**Prohibited:**
```csharp
_log.Write("[" + DateTime.Now + "]: " + message); // unstructured, unqueryable
```

**Required:**
```csharp
_logger.LogInformation("Order {OrderId} processed by {UserId} in {ElapsedMs}ms",
    orderId, userId, elapsed.TotalMilliseconds);
```

Use `ILogger<T>` from `Microsoft.Extensions.Logging`. Integrate with Application Insights
or Serilog for structured log shipping. Include correlation IDs on every entry.

**DAS Rule:** No custom log utilities. `ILogger<T>` only. Structured templates only.

---

## 11. Resilience Patterns (HIGH)

External dependencies (HTTP APIs, databases, SMTP, storage) will fail transiently.
Without retry and circuit breaker policies, a single transient failure crashes the request.

**Required for all external calls:**
```csharp
// Using Polly
services.AddHttpClient<ExternalApiClient>()
    .AddTransientHttpErrorPolicy(p =>
        p.WaitAndRetryAsync(3, attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt))))
    .AddTransientHttpErrorPolicy(p =>
        p.CircuitBreakerAsync(5, TimeSpan.FromSeconds(30)));
```

Apply retry policies to: HTTP calls, database operations, storage operations, email sending.

**DAS Rule:** Polly (or equivalent) is mandatory for all external service calls.

---

## 12. Authentication (DAS Mandatory)

- CAL (Customer Authentication Library) must be used for all authentication and authorisation
- No custom authentication middleware or token validation logic
- Role-based access control enforced on all API endpoints
- Angular route guards implemented for all protected views
- No token storage or handling in UI/client-side code

---

## 13. CI/CD & SAST Compliance

- Azure DevOps pipelines required (no manual deployments)
- Build, test, and SAST stages are all mandatory — no skipping
- Approved pipeline agents only (see DAS platform documentation)
- All technologies in the stack must support SAST scanning

---

## DAS Stack Version Requirements

| Technology | Recommended | Supported | Not Recommended |
|---|---|---|---|
| .NET | 10 (LTS) / 8 (LTS) | Framework 4.8.1 | 9 (STS), Framework 4.8 or below |
| Angular | 21 / 20 / 19 (LTS) | — | Below 19 |
| React | — | 19 / 18 (acceptable) | Not preferred |

New applications must target .NET 8 LTS or .NET 10 LTS.
.NET Framework 4.8.1 applications must have a documented migration plan.

---

*Derived from DAS platform documentation and .NET enterprise code review patterns.*
*Reference for BlueLine Quality Gate agent rule configuration.*
