from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.crm.hubspot_client import HubSpotAPIError, HubSpotClient
from backend.crm.salesforce_client import SalesforceAPIError, SalesforceClient
from backend.database.models.crm_connections import CRMConnection
from backend.database.models.crm_records import CRMRecord
from backend.database.models.crm_sync_logs import CRMSyncLog
from backend.database.models.leads import Lead


HUBSPOT_STATUS_MAP = {
    "lead": "New Leads",
    "new": "New Leads",
    "open": "New Leads",
    "working": "Qualified",
    "qualified": "Qualified",
    "opportunity": "Proposal",
    "proposal": "Proposal",
    "negotiation": "Negotiation",
    "closedwon": "Closed Won",
}

SALESFORCE_STATUS_MAP = {
    "new": "New Leads",
    "working": "Qualified",
    "qualified": "Qualified",
    "proposal": "Proposal",
    "negotiation": "Negotiation",
    "closed won": "Closed Won",
}


def map_hubspot_contact(contact: dict[str, Any]) -> dict[str, Any]:
    properties = contact.get("properties") or {}
    contact_id = str(contact.get("id", "")).strip()
    email = str(properties.get("email", "")).strip().lower()
    if not contact_id:
        raise ValueError("HubSpot contact is missing its provider ID.")
    if not email:
        raise ValueError(f"HubSpot contact {contact_id} has no email property.")

    first_name = str(properties.get("firstname") or "").strip()
    last_name = str(properties.get("lastname") or "").strip()
    contact_name = " ".join(part for part in (first_name, last_name) if part) or None
    company_name = str(properties.get("company") or "").strip() or (
        f"HubSpot Contact {contact_id}"
    )
    status_key = str(
        properties.get("hs_lead_status")
        or properties.get("lifecyclestage")
        or ""
    ).replace(" ", "").replace("_", "").lower()

    city = str(properties.get("city") or "").strip()
    state = str(properties.get("state") or "").strip()
    location = ", ".join(part for part in (city, state) if part) or None

    return {
        "provider_record_id": contact_id,
        "email": email,
        "company_name": company_name,
        "contact_name": contact_name,
        "contact_title": properties.get("jobtitle") or None,
        "phone": properties.get("phone") or None,
        "industry": properties.get("industry") or None,
        "lead_status": HUBSPOT_STATUS_MAP.get(status_key, "New Leads"),
        "source": "CRM",
        "company_size": properties.get("numberofemployees") or None,
        "annual_revenue": properties.get("annualrevenue") or None,
        "location": location,
        "provider_payload": contact,
    }


def get_or_create_hubspot_connection(db: Session) -> CRMConnection:
    connection = db.execute(
        select(CRMConnection)
        .where(
            CRMConnection.provider == "hubspot",
            CRMConnection.account_identifier == "environment",
        )
        .order_by(CRMConnection.connection_id.asc())
    ).scalars().first()
    if connection:
        return connection

    connection = CRMConnection(
        provider="hubspot",
        account_identifier="environment",
        display_name="HubSpot environment connection",
        credential_ref="HUBSPOT_SERVICE_KEY",
        scopes=["crm.objects.contacts.read"],
    )
    db.add(connection)
    db.flush()
    return connection


def test_hubspot_connection(client: HubSpotClient) -> dict[str, Any]:
    return client.test_connection()


def sync_hubspot_contacts(
    db: Session,
    client: HubSpotClient,
    *,
    max_records: int = 100,
) -> dict[str, Any]:
    if max_records < 1 or max_records > 5000:
        raise ValueError("max_records must be between 1 and 5000.")

    connection = get_or_create_hubspot_connection(db)
    run_id = str(uuid4())
    sync_log = CRMSyncLog(
        connection=connection,
        sync_run_id=run_id,
        operation="pull",
        object_type="contact",
    )
    db.add(sync_log)
    db.flush()

    try:
        contacts = client.list_contacts(max_records=max_records)
        for contact in contacts:
            try:
                mapped = map_hubspot_contact(contact)
            except ValueError as exc:
                sync_log.records_failed += 1
                sync_log.error_message = str(exc)
                continue

            existing_lead = db.execute(
                select(Lead).where(Lead.email == mapped["email"])
            ).scalar_one_or_none()
            lead_values = {
                key: value
                for key, value in mapped.items()
                if key
                in {
                    "email",
                    "company_name",
                    "contact_name",
                    "contact_title",
                    "phone",
                    "industry",
                    "lead_status",
                    "source",
                    "company_size",
                    "annual_revenue",
                    "location",
                }
            }
            if existing_lead:
                for field, value in lead_values.items():
                    setattr(existing_lead, field, value)
                lead = existing_lead
                sync_log.records_updated += 1
            else:
                lead = Lead(**lead_values)
                db.add(lead)
                db.flush()
                sync_log.records_created += 1

            record = db.execute(
                select(CRMRecord).where(
                    CRMRecord.connection_id == connection.connection_id,
                    CRMRecord.object_type == "contact",
                    CRMRecord.provider_record_id == mapped["provider_record_id"],
                )
            ).scalar_one_or_none()
            now = datetime.now(timezone.utc)
            if record:
                record.lead = lead
                record.provider_payload = mapped["provider_payload"]
                record.sync_state = "synced"
                record.last_synced_at = now
            else:
                db.add(
                    CRMRecord(
                        connection=connection,
                        lead=lead,
                        object_type="contact",
                        provider_record_id=mapped["provider_record_id"],
                        provider_payload=mapped["provider_payload"],
                        last_synced_at=now,
                    )
                )
            sync_log.records_read += 1

        sync_log.status = "succeeded" if sync_log.records_failed == 0 else "partial"
        sync_log.completed_at = datetime.now(timezone.utc)
        connection.last_successful_sync_at = sync_log.completed_at
        db.commit()
        return {
            "sync_run_id": run_id,
            "status": sync_log.status,
            "records_read": sync_log.records_read,
            "records_created": sync_log.records_created,
            "records_updated": sync_log.records_updated,
            "records_failed": sync_log.records_failed,
        }
    except HubSpotAPIError:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError(f"HubSpot contact sync failed: {exc}") from exc


def map_salesforce_lead(lead: dict[str, Any]) -> dict[str, Any]:
    provider_id = str(lead.get("Id") or "").strip()
    email = str(lead.get("Email") or "").strip().lower()
    if not provider_id:
        raise ValueError("Salesforce lead is missing its provider ID.")
    if not email:
        raise ValueError(f"Salesforce lead {provider_id} has no email field.")

    first_name = str(lead.get("FirstName") or "").strip()
    last_name = str(lead.get("LastName") or "").strip()
    city = str(lead.get("City") or lead.get("MailingCity") or "").strip()
    state = str(lead.get("State") or lead.get("MailingState") or "").strip()
    account = lead.get("Account") or {}
    company = str(lead.get("Company") or account.get("Name") or "").strip()
    status = str(lead.get("Status") or "").strip().lower()
    return {
        "provider_record_id": provider_id,
        "email": email,
        "company_name": company or f"Salesforce Lead {provider_id}",
        "contact_name": " ".join(
            part for part in (first_name, last_name) if part
        )
        or None,
        "contact_title": lead.get("Title") or None,
        "phone": lead.get("Phone") or None,
        "industry": lead.get("Industry") or None,
        "lead_status": SALESFORCE_STATUS_MAP.get(status, "New Leads"),
        "source": "CRM",
        "company_size": str(lead.get("NumberOfEmployees") or "") or None,
        "annual_revenue": str(lead.get("AnnualRevenue") or "") or None,
        "location": ", ".join(part for part in (city, state) if part) or None,
        "provider_payload": lead,
    }


def get_or_create_salesforce_connection(db: Session) -> CRMConnection:
    connection = db.execute(
        select(CRMConnection)
        .where(
            CRMConnection.provider == "salesforce",
            CRMConnection.account_identifier == "environment",
        )
        .order_by(CRMConnection.connection_id.asc())
    ).scalars().first()
    if connection:
        return connection
    connection = CRMConnection(
        provider="salesforce",
        account_identifier="environment",
        display_name="Salesforce environment connection",
        credential_ref="SALESFORCE_CONSUMER_KEY/SALESFORCE_CONSUMER_SECRET",
        scopes=["api"],
    )
    db.add(connection)
    db.flush()
    return connection


def test_salesforce_connection(client: SalesforceClient) -> dict[str, Any]:
    return client.test_connection()


def sync_salesforce_leads(
    db: Session,
    client: SalesforceClient,
    *,
    max_records: int = 100,
) -> dict[str, Any]:
    if max_records < 1 or max_records > 5000:
        raise ValueError("max_records must be between 1 and 5000.")

    connection = get_or_create_salesforce_connection(db)
    run_id = str(uuid4())
    sync_log = CRMSyncLog(
        connection=connection,
        sync_run_id=run_id,
        operation="pull",
        object_type="contact" if client.object_type == "Contact" else "lead",
    )
    db.add(sync_log)
    db.flush()

    try:
        leads = client.list_leads(max_records=max_records)
        for raw_lead in leads:
            try:
                mapped = map_salesforce_lead(raw_lead)
            except ValueError as exc:
                sync_log.records_failed += 1
                sync_log.error_message = str(exc)
                continue
            lead_values = {
                key: value
                for key, value in mapped.items()
                if key
                in {
                    "email",
                    "company_name",
                    "contact_name",
                    "contact_title",
                    "phone",
                    "industry",
                    "lead_status",
                    "source",
                    "company_size",
                    "annual_revenue",
                    "location",
                }
            }
            existing_lead = db.execute(
                select(Lead).where(Lead.email == mapped["email"])
            ).scalar_one_or_none()
            if existing_lead:
                for field, value in lead_values.items():
                    setattr(existing_lead, field, value)
                lead = existing_lead
                sync_log.records_updated += 1
            else:
                lead = Lead(**lead_values)
                db.add(lead)
                db.flush()
                sync_log.records_created += 1

            record = db.execute(
                select(CRMRecord).where(
                    CRMRecord.connection_id == connection.connection_id,
                    CRMRecord.object_type
                    == ("contact" if client.object_type == "Contact" else "lead"),
                    CRMRecord.provider_record_id == mapped["provider_record_id"],
                )
            ).scalar_one_or_none()
            now = datetime.now(timezone.utc)
            if record:
                record.lead = lead
                record.provider_payload = mapped["provider_payload"]
                record.sync_state = "synced"
                record.last_synced_at = now
            else:
                db.add(
                    CRMRecord(
                        connection=connection,
                        lead=lead,
                        object_type=(
                            "contact" if client.object_type == "Contact" else "lead"
                        ),
                        provider_record_id=mapped["provider_record_id"],
                        provider_payload=mapped["provider_payload"],
                        last_synced_at=now,
                    )
                )
            sync_log.records_read += 1

        sync_log.status = "succeeded" if sync_log.records_failed == 0 else "partial"
        sync_log.completed_at = datetime.now(timezone.utc)
        connection.last_successful_sync_at = sync_log.completed_at
        db.commit()
        return {
            "sync_run_id": run_id,
            "status": sync_log.status,
            "records_read": sync_log.records_read,
            "records_created": sync_log.records_created,
            "records_updated": sync_log.records_updated,
            "records_failed": sync_log.records_failed,
        }
    except SalesforceAPIError:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError(f"Salesforce lead sync failed: {exc}") from exc
