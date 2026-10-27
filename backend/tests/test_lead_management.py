from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from backend.schema import BulkLeadImportRequest, LeadCreate, LeadUpdate
from modules.module1_leads import (
    bulk_import_leads,
    create_single_lead,
    delete_single_lead,
    update_single_lead,
)


def lead_payload(email: str = "buyer@example.com") -> LeadCreate:
    return LeadCreate(company_name="Example Corp", email=email)


def db_result(*, scalar=None, values=None) -> Mock:
    result = Mock()
    result.scalar_one_or_none.return_value = scalar
    result.scalars.return_value.all.return_value = values or []
    return result


def test_create_single_lead_persists_valid_lead():
    db = Mock()
    db.execute.return_value = db_result()

    created = create_single_lead(db, lead_payload())

    assert created.company_name == "Example Corp"
    assert created.email == "buyer@example.com"
    db.add.assert_called_once_with(created)
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(created)


def test_create_single_lead_rejects_duplicate_email():
    db = Mock()
    existing = Mock()
    db.execute.return_value = db_result(scalar=existing)

    with pytest.raises(ValueError, match="already exists"):
        create_single_lead(db, lead_payload())

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_update_single_lead_persists_changes_and_allows_same_email():
    db = Mock()
    existing = Mock(lead_id=7)
    db.get.return_value = existing
    db.execute.return_value = db_result()
    update = LeadUpdate(company_name="Updated Corp", email="buyer@example.com")

    updated = update_single_lead(db, 7, update)

    assert updated is existing
    assert existing.company_name == "Updated Corp"
    assert existing.email == "buyer@example.com"
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(existing)


def test_delete_single_lead_removes_record():
    db = Mock()
    existing = Mock(lead_id=7)
    db.get.return_value = existing

    delete_single_lead(db, 7)

    db.delete.assert_called_once_with(existing)
    db.commit.assert_called_once_with()


def test_bulk_import_skips_existing_and_case_insensitive_batch_duplicates():
    db = Mock()
    db.execute.return_value = db_result(values=["existing@example.com"])
    request = BulkLeadImportRequest(
        leads=[
            lead_payload("EXISTING@example.com"),
            lead_payload("new@example.com"),
            lead_payload("NEW@example.com"),
        ]
    )

    result = bulk_import_leads(db, request)

    assert result.total_received == 3
    assert result.imported_count == 1
    assert result.skipped_duplicates == 2
    db.add_all.assert_called_once()
    db.commit.assert_called_once_with()


def test_bulk_import_rejects_duplicates_when_skip_disabled():
    db = Mock()
    db.execute.return_value = db_result()
    request = BulkLeadImportRequest(
        leads=[lead_payload("same@example.com"), lead_payload("SAME@example.com")],
        skip_duplicates=False,
    )

    with pytest.raises(ValueError, match="Duplicate email"):
        bulk_import_leads(db, request)

    db.add_all.assert_not_called()
    db.commit.assert_not_called()


def test_lead_create_validates_email_and_status():
    with pytest.raises(ValidationError):
        lead_payload("not-an-email")

    with pytest.raises(ValidationError):
        LeadCreate(
            company_name="Example Corp",
            email="buyer@example.com",
            lead_status="Invalid Status",
        )
