# Project Documentation Template

---

## Project-Level Documentation

### Overview / Summary

> _Brief description of the project, its purpose, and the business problem it solves._

---

### Tech Stack & Environment

- **Frameworks:** _(e.g., LangChain, AutoGen, etc.)_
- **LLMs:** _(e.g., GPT-4, Claude, Gemini, etc.)_
- **Infra:** _(e.g., Azure, AWS, GCP, on-prem, etc.)_

---

### Integration Landscape

**External Systems:**

| System | Purpose / Integration Type |
|--------|---------------------------|
| OSDU | _(describe integration)_ |
| ServiceNow | _(describe integration)_ |
| _(add more)_ | _(describe integration)_ |

---

### Governance & Execution

#### Dependencies

- _(List project dependencies — tools, services, teams, APIs)_

#### Status Tracker

```
Requirement → Design → Development → Testing → Deployment
```

> **Current Status:** _(highlight current stage)_

#### Stakeholders

| Role | Name / Team |
|------|------------|
| Business Owner | _(name)_ |
| Technical Lead | _(name)_ |
| Support Owner | _(name)_ |

---

### For Completed Projects

- **Project Completion Summary:** _(What was delivered and when)_
- **Business Impact:** _(Quantified or qualitative impact achieved)_

---
---

## Agent-Level Documentation Checklist

> _Required for each individual agent in the project._

---

### 1. Core Definition

| Field | Details |
|-------|---------|
| **Agent Name** | _(name)_ |
| **Agent ID** | _(unique ID)_ |
| **Project Mapping** | _(which project this agent belongs to)_ |
| **Status Lifecycle** | Yet to Start → Prod → Paused/Retired |
| **Current Status** | _(current stage)_ |

---

### 2. Problem & Purpose _(MANDATORY)_

- **Agent-Level Problem Statement:**
  > _(What specific problem does this agent solve?)_

- **Executive Summary:**
  > _(What does the agent do + business value delivered)_

---

### 3. Functional Design

#### Functional Flow _(Step-by-Step Execution)_

1. _(Step 1)_
2. _(Step 2)_
3. _(Step 3)_
4. _(Add more steps as needed)_

#### Inputs / Outputs

| Type | Description | Format / Source |
|------|-------------|----------------|
| **Input** | _(describe input)_ | _(format/source)_ |
| **Output** | _(describe output)_ | _(format/destination)_ |

#### Trigger Type

- [ ] API
- [ ] Scheduled
- [ ] Event-based

---

### 4. Architecture _(MANDATORY)_

#### Conceptual Diagram

> _(Attach or embed conceptual diagram here)_

#### HLD — High Level Design

> _(Attach or embed HLD diagram here)_

#### LLD — Low Level Design

> _(Attach or embed LLD diagram here)_
>
> **Note:** LLD must be completed before Production deployment.

---

### 5. AI / Agent Configuration

- **System Prompts & Model Configuration:**
  > _(Document system prompts, model name, temperature, max tokens, etc.)_

- **Tools / API Specifications:**

| Tool / API | Purpose | Endpoint / Reference |
|------------|---------|---------------------|
| _(name)_ | _(purpose)_ | _(endpoint or link)_ |

---

### 6. Engineering & Access

- **Repo Link + Access:**
  - Repo: _(URL)_
  - Access level: _(who has access and how to request)_

- **Environment Mapping:**

| Environment | URL / Config | Notes |
|------------|-------------|-------|
| Dev | _(link/config)_ | _(notes)_ |
| QA | _(link/config)_ | _(notes)_ |
| Prod | _(link/config)_ | _(notes)_ |

- **Credentials:**
  > _(Where credentials are stored, e.g., Key Vault, Secret Manager — do NOT paste secrets here)_

---

### 7. Operations & Visibility

- **Monitoring & Logging:**
  > _(Tools used, dashboards, alert channels)_

- **Support / Runbook:**
  > _(Link to runbook or inline steps for common issues)_

- **EGUL Nav / Catalogue Updates:**
  > _(Steps or links to update the internal catalogue/nav)_

---

### 8. Knowledge & Training

- **Demo Recordings:**
  - _(Link to recorded demo sessions)_

- **KT / KM Session Links:**
  - _(Link to knowledge transfer or knowledge management sessions)_

---

### 9. Lifecycle Operations

- **Pause / Restart Documentation:**
  > _(Steps to safely pause and restart the agent)_

- **Intern ID Deactivation / Access Cleanup:**
  > _(Steps to deactivate intern access when engagement ends)_

---

### 10. For Completed Agents

- **Completion Summary:** _(What was delivered)_
- **Automation Delivered:** _(What manual process was automated and the scale)_
- **Business Impact:** _(Quantified outcome — hours saved, errors reduced, etc.)_
- **Known Limitations:** _(Edge cases, known gaps, or future improvements needed)_

---
---

## Standard Documentation Folder Structure _(MANDATORY)_

```
Project/
├── Project_Documentation        (Word or PDF)
├── Agents/
│   ├── Agent_1_Documentation    (with diagrams)
│   └── Agent_2_Documentation.md
└── Diagrams/
    ├── HLD/
    ├── LLD/
    ├── Conceptual/
    └── Recordings/
```

---

_Template version: 2026-05-26_
