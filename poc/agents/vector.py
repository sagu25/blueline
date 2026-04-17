"""
VECTOR — Risk Hotspot & Complexity Scorer
Scores each piece of code for risk based on cyclomatic complexity,
nesting depth, size, and dependency count.
In production this also uses git churn history — in the POC it uses
static analysis only since we have no git connection.
"""

import re
import json
from utils.llm_client import call_claude

SYSTEM_PROMPT = """
You are VECTOR, a code risk analysis agent for a .NET (C#) and Angular (TypeScript) codebase.

You will be given:
1. A code snippet
2. Static metrics already computed for that code (complexity, nesting, size, dependencies)

Your job is to:
1. Use the metrics AND your own reading of the code to assign a risk score
2. Identify the specific hotspots (methods or classes) that are highest risk
3. Write a clear reviewer note explaining what to focus on

=== RISK SCORING GUIDE ===
Consider these factors:
- Cyclomatic complexity > 10 per method → HIGH risk
- Nesting depth > 3 levels → MEDIUM-HIGH risk
- Method count > 15 in one class → HIGH risk (too many responsibilities)
- Import/dependency count > 10 → MEDIUM risk
- No test indicators (no Assert, should, expect, Mock) → adds risk
- Security-sensitive operations (SQL, file IO, auth, crypto, HTTP calls) → HIGH risk regardless of complexity
- Mixed responsibilities (data access + business logic + UI in one class) → HIGH risk

=== RISK LEVELS ===
- LOW     (0.0–0.3): Safe to review quickly
- MEDIUM  (0.3–0.6): Needs careful review
- HIGH    (0.6–0.8): Reviewer must pay close attention
- CRITICAL (0.8–1.0): Must not be approved without thorough review

=== OUTPUT FORMAT ===
Respond with valid JSON only:
{
  "overall_risk_score": <float 0.0-1.0>,
  "overall_risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "hotspots": [
    {
      "name": "method or class name",
      "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
      "reason": "specific reason this is a hotspot"
    }
  ],
  "reviewer_focus": "one paragraph telling the human reviewer exactly what to look at and why",
  "has_security_operations": true | false,
  "has_test_indicators": true | false,
  "recommendation": "REVIEW_CAREFULLY" | "QUICK_REVIEW_OK" | "BLOCK_UNTIL_REFACTORED"
}
"""

# ── Static metric computation ──────────────────────────────────────────────

DECISION_PATTERNS_CS = [
    r'\bif\b', r'\belse if\b', r'\bfor\b', r'\bforeach\b',
    r'\bwhile\b', r'\bswitch\b', r'\bcase\b', r'\bcatch\b',
    r'\?\s', r'&&', r'\|\|'
]

DECISION_PATTERNS_TS = [
    r'\bif\b', r'\belse if\b', r'\bfor\b', r'\bforEach\b',
    r'\bwhile\b', r'\bswitch\b', r'\bcase\b', r'\bcatch\b',
    r'\?\?', r'&&', r'\|\|', r'\?\.'
]

SECURITY_PATTERNS = [
    r'\bSqlCommand\b', r'\bExecuteQuery\b', r'SELECT\s', r'INSERT\s',
    r'UPDATE\s', r'DELETE\s', r'File\.', r'Directory\.', r'Path\.',
    r'HttpClient', r'WebClient', r'password', r'Password', r'secret',
    r'token', r'Token', r'auth', r'Auth', r'crypto', r'Crypto',
    r'encrypt', r'Encrypt', r'hash', r'Hash', r'http\.get', r'http\.post'
]

TEST_PATTERNS = [
    r'\bAssert\b', r'\bshould\b', r'\bexpect\b', r'\bMock\b',
    r'\bspy\b', r'\bstub\b', r'\[Test\]', r'\[Fact\]',
    r'describe\(', r'it\(', r'test\('
]


def compute_static_metrics(code: str, language: str) -> dict:
    lines = code.splitlines()
    non_empty = [l for l in lines if l.strip()]

    # Cyclomatic complexity
    patterns = DECISION_PATTERNS_CS if language == "csharp" else DECISION_PATTERNS_TS
    complexity = 1
    for p in patterns:
        complexity += len(re.findall(p, code))

    # Max nesting depth (count leading spaces / braces)
    max_depth = 0
    for line in lines:
        stripped = line.lstrip()
        if not stripped:
            continue
        indent = len(line) - len(stripped)
        depth  = indent // 4   # assume 4-space or equivalent
        if depth > max_depth:
            max_depth = depth

    # Count methods/functions
    if language == "csharp":
        method_count = len(re.findall(
            r'(public|private|protected|internal)\s+\w[\w<>\[\]]*\s+\w+\s*\(', code
        ))
    else:
        method_count = len(re.findall(
            r'(function\s+\w+\s*\(|\w+\s*\(.*\)\s*[:{]|=>)', code
        ))

    # Dependencies / imports
    if language == "csharp":
        dep_count = len(re.findall(r'^using\s+', code, re.MULTILINE))
    else:
        dep_count = len(re.findall(r'^import\s+', code, re.MULTILINE))

    # Security & test indicators
    has_security = any(re.search(p, code) for p in SECURITY_PATTERNS)
    has_tests    = any(re.search(p, code) for p in TEST_PATTERNS)

    return {
        "lines_of_code":      len(non_empty),
        "cyclomatic_complexity": complexity,
        "max_nesting_depth":  max_depth,
        "method_count":       method_count,
        "dependency_count":   dep_count,
        "has_security_ops":   has_security,
        "has_test_indicators": has_tests,
    }


def score_risk(code: str, language: str = "auto") -> dict:
    """
    Computes static metrics locally, then asks Claude to produce
    a risk assessment and hotspot analysis.
    """
    metrics = compute_static_metrics(code, language)

    user_message = f"""
Analyse the following {language} code for risk.

Static metrics already computed:
- Lines of code:          {metrics['lines_of_code']}
- Cyclomatic complexity:  {metrics['cyclomatic_complexity']}
- Max nesting depth:      {metrics['max_nesting_depth']} levels
- Method / function count:{metrics['method_count']}
- Import / dependency count: {metrics['dependency_count']}
- Contains security-sensitive operations: {metrics['has_security_ops']}
- Contains test indicators: {metrics['has_test_indicators']}

Code:
```{language}
{code}
```

Return only the JSON response as described. No extra text.
"""

    raw = call_claude(SYSTEM_PROMPT, user_message)

    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    try:
        result = json.loads(clean)
        result["static_metrics"] = metrics   # attach raw metrics for display
        return result
    except json.JSONDecodeError:
        return {
            "overall_risk_score": 0.0,
            "overall_risk_level": "UNKNOWN",
            "hotspots": [],
            "reviewer_focus": "Could not parse agent response.",
            "has_security_operations": metrics["has_security_ops"],
            "has_test_indicators": metrics["has_test_indicators"],
            "recommendation": "REVIEW_CAREFULLY",
            "static_metrics": metrics,
            "raw_response": raw
        }
