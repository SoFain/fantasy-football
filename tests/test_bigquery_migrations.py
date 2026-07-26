from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from scripts import run_bigquery_migrations


class BigQueryMigrationRunnerTests(unittest.TestCase):
    def test_dry_run_output_says_discovered_not_pending(self):
        migrations = [
            run_bigquery_migrations.Migration(
                migration_id="0001",
                description="noop",
                path=Path("bigquery/migrations/0001__noop.sql"),
                sql="-- no-op\n",
                checksum="abc",
            )
        ]
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = run_bigquery_migrations.print_discovered_migrations(migrations)

        text = output.getvalue()
        self.assertEqual(result, migrations)
        self.assertIn("local discovery only", text)
        self.assertIn("Discovered migration files:", text)
        self.assertIn("Use --list-pending for ledger-aware pending migration status.", text)
        self.assertNotIn("Pending migrations:", text)

    def test_list_pending_output_still_uses_pending_label(self):
        migrations = [
            run_bigquery_migrations.Migration(
                migration_id="0001",
                description="noop",
                path=Path("bigquery/migrations/0001__noop.sql"),
                sql="-- no-op\n",
                checksum="abc",
            )
        ]
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            pending = run_bigquery_migrations.print_plan(migrations, applied_ids=set())

        text = output.getvalue()
        self.assertEqual(pending, migrations)
        self.assertIn("Pending migrations:", text)

    def test_read_migrations_discovers_sql_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "0001__create_test.sql"
            path.write_text("SELECT 1;\n", encoding="utf-8")

            migrations = run_bigquery_migrations.read_migrations(Path(tmp))

        self.assertEqual(len(migrations), 1)
        self.assertEqual(migrations[0].migration_id, "0001")
        self.assertEqual(migrations[0].description, "create test")


if __name__ == "__main__":
    unittest.main()
