import io
import pandas as pd

# The schema definition mapped directly to the PostgreSQL `leads` model
TARGET_SCHEMA_FIELDS = {
    "company_name": {"label": "Company Name", "required": True},
    "email": {"label": "Work Email", "required": True},
    "contact_name": {"label": "Contact Name", "required": False},
    "contact_title": {"label": "Job Title", "required": False},
    "industry": {"label": "Industry", "required": False},
    "company_size": {"label": "Company Size / Headcount", "required": False},
    "annual_revenue": {"label": "Annual Revenue", "required": False},
    "funding_stage": {"label": "Funding Stage", "required": False},
    "funding_raised": {"label": "Funding Raised", "required": False},
    "location": {"label": "Location (HQ)", "required": False},
    "tech_stack": {"label": "Tech Stack (Comma-separated)", "required": False},
    "phone": {"label": "Phone Number", "required": False},
    "source": {"label": "Lead Source", "required": False},
}

# Fuzzy synonym mapping for auto-detection
COLUMN_SYNONYMS = {
    "company_name": ["company", "company_name", "organization", "account", "business"],
    "email": ["email", "work_email", "contact_email", "mail", "email_address"],
    "contact_name": ["contact", "contact_name", "name", "full_name", "person"],
    "contact_title": ["title", "job_title", "position", "role"],
    "industry": ["industry", "sector", "vertical", "domain"],
    "company_size": ["size", "company_size", "headcount", "employees", "team_size"],
    "annual_revenue": ["revenue", "annual_revenue", "arr"],
    "funding_stage": ["stage", "funding_stage", "round", "series"],
    "funding_raised": ["funding", "raised", "funding_raised", "total_funding"],
    "location": ["location", "city", "country", "headquarters", "hq"],
    "tech_stack": ["tech", "technologies", "tech_stack", "stack", "tools"],
    "phone": ["phone", "telephone", "mobile", "phone_number"],
    "source": ["source", "lead_source", "origin", "channel"],
}


def auto_match_column(csv_col_name: str) -> str:
    """Returns the best matching schema field name or 'ignore'."""
    clean_col = csv_col_name.strip().lower().replace(" ", "_")
    for target_key, synonyms in COLUMN_SYNONYMS.items():
        if clean_col in synonyms:
            return target_key
    return "ignore"


def generate_sample_csv() -> str:
    """Generates sample CSV data matching the target leads schema."""
    sample_data = {
        "Company Name": ["Acme Cloud Corp", "DataSync Labs", "NexaCore AI"],
        "Work Email": ["sarah@acmecloud.io", "alex.chen@datasync.com", "m.brody@nexacore.tech"],
        "Contact Name": ["Sarah Jenkins", "Alex Chen", "Marcus Brody"],
        "Job Title": ["VP of Engineering", "Chief Technology Officer", "Head of Product"],
        "Industry": ["Cloud Infrastructure", "Enterprise Software", "Artificial Intelligence"],
        "Company Size": ["250-500", "51-200", "501-1000"],
        "Annual Revenue": ["$10M - $25M", "$5M - $10M", "$25M - $50M"],
        "Funding Stage": ["Series B", "Series A", "Series B"],
        "Funding Raised": ["$22M", "$8.5M", "$30M"],
        "Location": ["San Francisco, CA", "Austin, TX", "New York, NY"],
        "Tech Stack": ["AWS, Kubernetes, Python", "PostgreSQL, React, Snowflake", "GCP, PyTorch, Docker"],
        "Phone": ["+1 415 555 0192", "+1 512 555 0143", "+1 212 555 0188"],
    }
    df = pd.DataFrame(sample_data)
    return df.to_csv(index=False)