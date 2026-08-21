import json
import logging
import os
import tempfile
import unittest
from pathlib import Path

from logdock import LogDock
from logdock.config.settings import LogFormat
from logdock.core.buffer import LogBufferHandler
from logdock.integrations.persistence import LocalPersistenceClient


class ManualPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.original_cwd = Path.cwd()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        os.chdir(self.root)
        (self.root / "logdock.json").write_text(
            json.dumps(
                {
                    "app_name": "test-app",
                    "log_level": "DEBUG",
                    "notification": {"enabled": False, "provider": ""},
                    "persistence": {
                        "enabled": True,
                        "provider": "LOCAL",
                        "path": "./records",
                    },
                    "format": {
                        "time_enabled": True,
                        "timezone": "UTC",
                        "time_precision": "SECOND",
                        "app_name_enabled": True,
                        "source_enabled": True,
                        "source_full_path": False,
                    },
                }
            ),
            encoding="utf-8",
        )
        self.logdock = LogDock()
        self.assertIsInstance(
            self.logdock.persistence_client,
            LocalPersistenceClient,
        )

    def tearDown(self):
        if self.logdock._buffer_handler is not None:
            self.logdock.logger.removeHandler(self.logdock._buffer_handler)
            self.logdock._buffer_handler.close()
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()

    def test_only_writes_records_when_persist_is_called(self):
        self.logdock.info("primeiro registro")
        self.logdock.error("segundo registro")

        self.assertFalse((self.root / "records").exists())

        result = self.logdock.persist()

        self.assertTrue(result.success)
        self.assertEqual(result.provider, "LOCAL")
        self.assertEqual(result.records_count, 2)
        destination = Path(result.location)
        self.assertTrue(destination.exists())
        document = json.loads(destination.read_text(encoding="utf-8"))
        records = document["logs"]
        self.assertEqual([record["message"] for record in records], ["primeiro registro", "segundo registro"])
        self.assertEqual(document["execution"]["id"], self.logdock.execution_id)
        self.assertEqual(document["execution"]["records_count"], 2)
        self.assertEqual(document["execution"]["app_name"], "test-app")
        self.assertTrue(all("execution_id" not in record for record in records))
        self.assertTrue(all("app_name" not in record for record in records))
        self.assertTrue(all(record["source"] == "test_persistence.py" for record in records))
        self.assertEqual(len(self.logdock.execution_id), 12)

    def test_successful_persist_clears_only_the_persisted_buffer(self):
        self.logdock.info("registro")
        first_result = self.logdock.persist()
        second_result = self.logdock.persist()

        self.assertEqual(first_result.records_count, 1)
        self.assertTrue(second_result.success)
        self.assertEqual(second_result.records_count, 0)
        self.assertIsNone(second_result.location)

    def test_new_records_are_written_to_a_new_file(self):
        self.logdock.info("primeiro lote")
        first_result = self.logdock.persist()
        self.logdock.info("segundo lote")
        second_result = self.logdock.persist()

        self.assertNotEqual(first_result.location, second_result.location)
        self.assertTrue(Path(first_result.location).exists())
        self.assertTrue(Path(second_result.location).exists())
        self.assertTrue(second_result.location.endswith("-2.json"))

    def test_persists_without_timestamp_when_time_is_disabled(self):
        self.logdock.logdock_settings.log_format.time.enabled = False
        self.logdock.info("sem horário")

        result = self.logdock.persist()

        document = json.loads(Path(result.location).read_text(encoding="utf-8"))
        self.assertNotIn("persisted_at", document["execution"])
        self.assertNotIn("timestamp", document["logs"][0])

    def test_internal_notification_warning_is_not_persisted(self):
        self.logdock.notify("não deve ser enviado")

        result = self.logdock.persist()

        self.assertTrue(result.success)
        self.assertEqual(result.records_count, 0)


class DisabledPersistenceTests(unittest.TestCase):
    def test_persist_reports_when_feature_is_disabled(self):
        instance = LogDock.__new__(LogDock)
        instance.execution_id = "test"
        instance.logdock_settings = type(
            "Settings",
            (),
            {"persistence": type("Persistence", (), {"enabled": False})()},
        )()

        result = instance.persist()

        self.assertFalse(result.success)
        self.assertEqual(result.records_count, 0)
        self.assertEqual(result.error, "Persistência desabilitada.")


class BufferFormattingTests(unittest.TestCase):
    def test_omits_optional_fields_disabled_in_log_format(self):
        handler = LogBufferHandler(execution_id="short-id", log_format=LogFormat())
        record = logging.LogRecord(
            name="test-app",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="mensagem",
            args=(),
            exc_info=None,
        )
        record.logdock_execution_id = "short-id"

        handler.handle(record)

        self.assertEqual(
            handler.snapshot(),
            [
                {
                    "level": "INFO",
                    "message": "mensagem",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
