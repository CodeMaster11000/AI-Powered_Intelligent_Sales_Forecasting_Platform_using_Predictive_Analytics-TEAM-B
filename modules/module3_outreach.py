from backend.database.models.leads import Lead


def generate_personalized_email(lead: Lead, insight_data: dict, angle: str, tone: str, custom_note: str = "") -> dict:
    """Generates targeted subject line variants and a personalized email body."""
    first_name = (lead.contact_name or "there").split()[0]
    company = lead.company_name
    title = lead.contact_title or "Executive"
    stack_snippet = lead.tech_stack[0] if (lead.tech_stack and len(lead.tech_stack) > 0) else "modern cloud"
    stage = lead.funding_stage or "growth"

    # Tone customization
    if tone == "Direct & Punchy (Under 100 words)":
        body = (
            f"Hi {first_name},\n\n"
            f"Saw Acme Cloud's {stage} growth and work scaling your {stack_snippet} architecture.\n\n"
            f"Most {title}s we speak with lose 4-6 hours weekly dealing with forecast variance as their sales pipeline expands.\n\n"
            f"We built SalesGenie to automate lead scoring with 92% pipeline accuracy. "
            f"Worth a quick 5-minute chat this Thursday?\n\n"
            f"Best,\nAlex Rep"
        )
    elif tone == "Problem-Centric / Metric-Driven":
        body = (
            f"Hi {first_name},\n\n"
            f"Quick observation on {company}: as you scale in {lead.industry or 'tech'}, data pipeline bottlenecks often introduce latency into CRM reporting.\n\n"
            f"Our platform benchmarks show a 40% reduction in sales qualification cycles for teams using {stack_snippet}.\n\n"
            f"{f'Note: {custom_note}' if custom_note else ''}\n\n"
            f"Would you be open to a 10-minute look at the benchmark numbers?\n\n"
            f"Regards,\nAlex Rep"
        )
    else:  # Consultative / Executive (Default)
        body = (
            f"Hi {first_name},\n\n"
            f"Congratulations on {company}'s ongoing {stage} momentum.\n\n"
            f"In reviewing your infrastructure footprint, our revenue models flagged strong alignment between your {stack_snippet} stack and our predictive analytics engine.\n\n"
            f"{insight_data.get('opportunities', 'Our platform accelerates conversion by matching high-intent prospects.')}\n\n"
            f"Do you have 10 minutes this Wednesday or Thursday afternoon to share notes?\n\n"
            f"Best regards,\nAlex Rep\nSalesGenie AI"
        )

    subject_options = [
        f"Quick question re: {stack_snippet} at {company}",
        f"{company} + SalesGenie: predictive intelligence",
        f"Idea for {first_name} on {stage} sales forecasting",
    ]

    return {
        "subject_options": subject_options,
        "selected_subject": subject_options[0],
        "body": body,
        "hook_score": 92,
        "word_count": len(body.split()),
    }