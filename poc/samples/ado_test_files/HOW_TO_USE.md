# BlueLine Demo — Test Files for Azure DevOps

Push these 4 files as a single PR to your Azure DevOps repo.
When BlueLine reviews that PR, each file produces a different result — showing the full range of the Quality Gate.

---

## Expected Results Per File

| File | Expected Verdict | Key Findings |
|---|---|---|
| `InventoryService.cs` | **BLOCK** | `.Result` deadlock, `new HttpClient()`, SQL injection, N+1 query, empty catch, file upload no validation |
| `UserController.cs` | **REQUEST_CHANGES** | No DI, `JObject` without validation, raw exception to caller, magic numbers, unstructured logging |
| `stock-upload.component.ts` | **BLOCK** | `innerHTML` XSS × 2, `any` type × 5, unsubscribed Observables × 2, token in localStorage, direct DOM manipulation |
| `order-list.component.ts` | **APPROVE** | Minor only: missing OnPush, magic number pageSize, error message exposed to UI, filter logic in component |

---

## How to Push as a PR

1. In your Azure DevOps repo, create a new branch:
   ```
   git checkout -b feature/blueline-demo-review
   ```

2. Copy these 4 files into appropriate folders in your repo.
   Suggested locations (adjust to your repo structure):
   ```
   src/App.Business/InventoryService.cs
   src/App.Api/Controllers/UserController.cs
   src/App.Web/src/app/stock/stock-upload.component.ts
   src/App.Web/src/app/orders/order-list.component.ts
   ```

3. Commit and push:
   ```
   git add .
   git commit -m "Add inventory and user management features"
   git push origin feature/blueline-demo-review
   ```

4. Open a Pull Request in Azure DevOps targeting your main/develop branch.

5. Copy the PR ID from the URL (e.g. `https://dev.azure.com/org/project/_git/repo/pullrequest/42` → PR ID is `42`)

6. Paste the PR ID into BlueLine's Live PR Review tab and click Run.

---

## What the Demo Shows

- **InventoryService.cs** triggers the most critical findings — VECTOR will score it CRITICAL risk,
  CLARION will flag 6+ violations, ASCENT will BLOCK it.

- **UserController.cs** triggers medium/high findings — shows REQUEST_CHANGES with a clear fix list.

- **stock-upload.component.ts** triggers Angular-specific security findings — shows BlueLine
  covers both backend and frontend in the same PR review.

- **order-list.component.ts** shows that BlueLine does NOT over-flag clean-ish code —
  it APPROVEs with minor suggestions, demonstrating that the agents are calibrated,
  not just noisy.

The contrast between the BLOCK files and the APPROVE file is the key demo moment —
it shows the tool makes meaningful distinctions, not just flags everything.
