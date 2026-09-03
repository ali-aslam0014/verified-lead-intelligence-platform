import pytest
from app.models import Base


def test_all_18_models_registered_in_metadata():
    expected_tables = {
        "roles",
        "users",
        "targets",
        "target_runs",
        "jobs",
        "businesses",
        "source_records",
        "websites",
        "social_profiles",
        "contacts",
        "website_audits",
        "seo_audits",
        "opportunities",
        "lead_scores",
        "verification_results",
        "evidence",
        "review_actions",
        "exports",
    }

    registered_tables = set(Base.metadata.tables.keys())
    assert len(registered_tables) == 18, f"Expected 18 tables, got {len(registered_tables)}: {registered_tables}"
    assert expected_tables == registered_tables, f"Missing or mismatching tables: {expected_tables ^ registered_tables}"


def test_models_have_uuid_primary_keys():
    for table_name, table in Base.metadata.tables.items():
        assert "id" in table.columns, f"Table {table_name} missing 'id' column"
        assert table.columns["id"].primary_key, f"Table {table_name} 'id' column is not primary key"
        assert "created_at" in table.columns, f"Table {table_name} missing 'created_at'"
        assert "updated_at" in table.columns, f"Table {table_name} missing 'updated_at'"
