"""
Project BlueLine — FastAPI Backend
Exposes all 12 agents as REST endpoints consumed by the React frontend.
Run with: uvicorn api:app --reload --port 8000
"""
import os
import sys
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

app = FastAPI(title="BlueLine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Models ──────────────────────────────────────────────────────────────

class CodeRequest(BaseModel):
    code: str
    language: str

class AscentRequest(BaseModel):
    clarion: dict
    lumen: dict
    vector: dict
    language: str

class SecurityRequest(BaseModel):
    finding: str
    code_snippet: Optional[str] = ""
    affected_file: Optional[str] = "UnknownFile.cs"

class ForgeRequest(BaseModel):
    finding: str
    classification: str
    owasp_category: str
    secure_code_fix: str
    affected_file: str

class StewardRequest(BaseModel):
    pipeline: str
    finding_summary: str
    classification: str
    confidence: float
    action_taken: str
    agents_involved: List[str]
    human_gate_required: bool

class TimelineRequest(BaseModel):
    subject: str
    expiry_date: str
    environments: str
    ca_type: str

class CourierRequest(BaseModel):
    subject: str
    ca_type: str
    environments: str
    days_remaining: int

class HarbourRequest(BaseModel):
    subject: str
    ca_type: str
    environments: List[str]
    deployment_targets: dict
    cert_thumbprint: str
    days_remaining_old_cert: int

class ConfigRequest(BaseModel):
    provider: str
    azure_endpoint: Optional[str] = None
    azure_key: Optional[str] = None
    azure_deployment: Optional[str] = "gpt-4o"
    anthropic_key: Optional[str] = None
    ado_org: Optional[str] = None
    ado_pat: Optional[str] = None
    ado_project: Optional[str] = None
    ado_repo: Optional[str] = None

class LiveReviewRequest(BaseModel):
    pr_id: int
    shadow_mode: bool = True


# ── Status & Config ─────────────────────────────────────────────────────────────

@app.get("/api/status")
def get_status():
    from utils.llm_client import get_active_provider
    from utils.azure_devops import is_configured
    return {"ai_provider": get_active_provider(), "ado_configured": is_configured()}


@app.post("/api/config")
def set_config(req: ConfigRequest):
    if req.provider == "azure_openai":
        if req.azure_endpoint:   os.environ["AZURE_OPENAI_ENDPOINT"]   = req.azure_endpoint
        if req.azure_key:        os.environ["AZURE_OPENAI_API_KEY"]    = req.azure_key
        if req.azure_deployment: os.environ["AZURE_OPENAI_DEPLOYMENT"] = req.azure_deployment
        os.environ.pop("ANTHROPIC_API_KEY", None)
    else:
        if req.anthropic_key: os.environ["ANTHROPIC_API_KEY"] = req.anthropic_key
        os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
        os.environ.pop("AZURE_OPENAI_API_KEY", None)
    if req.ado_org:     os.environ["AZURE_DEVOPS_ORG_URL"] = req.ado_org
    if req.ado_pat:     os.environ["AZURE_DEVOPS_PAT"]     = req.ado_pat
    if req.ado_project: os.environ["AZURE_DEVOPS_PROJECT"] = req.ado_project
    if req.ado_repo:    os.environ["AZURE_DEVOPS_REPO"]    = req.ado_repo
    from utils.llm_client import get_active_provider
    from utils.azure_devops import is_configured
    return {"ai_provider": get_active_provider(), "ado_configured": is_configured()}


# ── Sample Files ────────────────────────────────────────────────────────────────

ALLOWED_SAMPLES = {"bad_csharp.cs", "bad_typescript.ts", "fortify_finding.txt"}

@app.get("/api/sample/{filename}")
def get_sample(filename: str):
    if filename not in ALLOWED_SAMPLES:
        raise HTTPException(status_code=404, detail="Sample not found")
    path = Path(__file__).parent / "samples" / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing on disk")
    return {"content": path.read_text(encoding="utf-8")}


# ── Quality Gate ────────────────────────────────────────────────────────────────

@app.post("/api/clarion")
def run_clarion(req: CodeRequest):
    from agents.clarion import review_code
    return review_code(req.code, req.language)

@app.post("/api/lumen")
def run_lumen(req: CodeRequest):
    from agents.lumen import detect_smells
    return detect_smells(req.code, req.language)

@app.post("/api/vector")
def run_vector(req: CodeRequest):
    from agents.vector import score_risk
    return score_risk(req.code, req.language)

@app.post("/api/ascent")
def run_ascent(req: AscentRequest):
    from agents.ascent import aggregate_review
    return aggregate_review(req.clarion, req.lumen, req.vector, req.language)


# ── Security Loop ───────────────────────────────────────────────────────────────

@app.post("/api/bulwark")
def run_bulwark(req: SecurityRequest):
    from agents.bulwark import triage_finding
    return triage_finding(req.finding, req.code_snippet)

@app.post("/api/forge")
def run_forge(req: ForgeRequest):
    from agents.forge import create_fix_pr
    return create_fix_pr(
        finding_description=req.finding,
        classification=req.classification,
        owasp_category=req.owasp_category,
        secure_code_fix=req.secure_code_fix,
        affected_file=req.affected_file,
    )

@app.post("/api/steward")
def run_steward(req: StewardRequest):
    from agents.steward import create_audit_entry
    return create_audit_entry(
        pipeline=req.pipeline,
        finding_summary=req.finding_summary,
        classification=req.classification,
        confidence=req.confidence,
        action_taken=req.action_taken,
        agents_involved=req.agents_involved,
        human_gate_required=req.human_gate_required,
    )


# ── Certificate Loop ────────────────────────────────────────────────────────────

@app.get("/api/certificates")
def get_certificates():
    from agents.regent import get_inventory
    return get_inventory()

@app.post("/api/timeline")
def run_timeline(req: TimelineRequest):
    from agents.timeline import analyse_certificate
    return analyse_certificate(
        subject=req.subject,
        expiry_date=req.expiry_date,
        environments=req.environments,
        ca_type=req.ca_type,
    )

@app.post("/api/courier")
def run_courier(req: CourierRequest):
    from agents.courier import request_certificate
    return request_certificate(
        subject=req.subject,
        ca_type=req.ca_type,
        environments=req.environments,
        days_remaining=req.days_remaining,
    )

@app.post("/api/harbour")
def run_harbour(req: HarbourRequest):
    from agents.harbour import deploy_certificate
    return deploy_certificate(
        subject=req.subject,
        ca_type=req.ca_type,
        environments=req.environments,
        deployment_targets=req.deployment_targets,
        cert_thumbprint=req.cert_thumbprint,
        days_remaining_old_cert=req.days_remaining_old_cert,
    )


# ── Live PR Review ──────────────────────────────────────────────────────────────

@app.get("/api/prs")
def get_prs():
    from utils.azure_devops import list_pull_requests, is_configured
    if not is_configured():
        raise HTTPException(status_code=400, detail="Azure DevOps not configured")
    try:
        return list_pull_requests(status="active", top=30)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/live-review")
def run_live_review(req: LiveReviewRequest):
    from utils.pr_runner import run_pr_review
    try:
        return run_pr_review(pr_id=req.pr_id, shadow_mode=req.shadow_mode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
