from app.config import normalize_database_url


def test_neon_postgresql_url_uses_psycopg_v3_driver():
    assert (
        normalize_database_url("postgresql://user:pass@example.neon.tech/db?sslmode=require")
        == "postgresql+psycopg://user:pass@example.neon.tech/db?sslmode=require"
    )


def test_legacy_postgres_url_is_normalized_too():
    assert normalize_database_url("postgres://u:p@h/db") == "postgresql+psycopg://u:p@h/db"


def test_non_postgres_url_is_unchanged():
    value = "sqlite+pysqlite:///:memory:"
    assert normalize_database_url(value) == value
