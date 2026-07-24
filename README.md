# ⚡ Careem Pulse

**AI Risk Radar for Cross-Vertical Launches**

> Spot the ripple before it reaches the customer.

Careem Pulse is a lightweight AI workflow built for the Careem Risk Radar hiring challenge. It turns messy cross-functional project updates into an evidence-backed view of delivery health, blockers, dependencies, owners, and management decisions.

## Demo scenario

**Ramadan Peak Readiness · UAE + KSA**

The prototype simulates updates across multiple fictional workstreams including Pay, Food, Rides, Quik, Super App, Customer Care, Operations, Legal, Marketing, and Data Platform.

All data is fictional and created specifically for this hiring exercise. No Careem internal or confidential information is used.

## What it does

Careem Pulse:

1. Reads short project updates from multiple teams.
2. Detects explicit and hidden delivery risks.
3. Identifies cross-team dependency chains.
4. Extracts exact evidence from source updates.
5. Assesses likelihood, impact, urgency, and dependency breadth.
6. Recommends an accountable owner by role.
7. Suggests an immediate action and escalation deadline.
8. Highlights missing information.
9. Produces an executive project-health view.
10. Re-analyzes the project as new updates arrive.

## Transparent risk scoring

The LLM performs extraction and dependency reasoning.

The final risk score is deterministic:

**Risk Score = 35% Impact + 25% Urgency + 20% Likelihood + 20% Dependency Breadth**

This keeps prioritization transparent rather than asking the model to assign an unexplained final score.

## Two demo datasets

### `dummy_updates.csv`

Represents a launch with unresolved issues.

A Live AI run identifies technical, payment, operational, and compliance risks and surfaces immediate management decisions.

### `scenario_recovery.csv`

Represents the next project update after mitigation actions were completed.

The same AI workflow re-evaluates the project and confirms whether previously identified risks have been resolved.

**Updates → Risks → Actions → New Updates → Re-analysis**

## AI architecture

- Python
- Streamlit
- Google Gemini
- Pydantic structured outputs
- Pandas
- Altair

Gemini reasons over project updates and returns a validated structured risk schema.

The application then calculates deterministic risk scores and renders the management dashboard.

## Human in the loop

Careem Pulse is designed as a decision-support tool, not an autonomous project manager.

AI recommends. The project manager validates ownership, priority, escalation, and delivery decisions.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

For Live AI, create:

`.streamlit/secrets.toml`

```toml
GEMINI_API_KEY = "your-key"
```

Never commit this file.

## Challenge

**Selected challenge: Risk Radar**

Design an AI workflow that monitors updates to flag risks, dependencies, and blockers early.

## Disclaimer

This is an independent prototype created solely for a hiring exercise. It is not an official Careem product and does not use Careem internal data.
