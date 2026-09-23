"""
Tamper-Evident Audit Logger

Implements SHA-256 hash-chained JSONL logging for tamper-evident audit trails,
aligned with EU AI Act Article 12 requirements.

Reference:
[1] EU AI Act Article 12: Record-Keeping Requirements.
    https://artificialintelligenceact.eu/article/12/
"""

import json
from pathlib import Path

from src.schemas.audit_log import AuditLogEntry


class TamperEvidentLogger:
    """
    Tamper-evident audit logger using SHA-256 hash-chained JSONL.

    Features:
    - Append-only JSONL storage
    - SHA-256 hash chaining (each entry references the preceding hash)
    - Integrity verification (recompute and compare hashes)
    - Safe recovery of the previous hash when reopening a valid log
    """

    GENESIS_HASH = "0" * 64

    def __init__(self, log_path: str | None = None) -> None:
        """
        Initialize the logger and recover state from an existing valid log.

        Args:
            log_path: Path to the JSONL log file. Defaults to ./audit_logs.jsonl.

        Raises:
            ValueError: If an existing audit log fails integrity verification.
        """
        self.log_path = Path(log_path or "audit_logs.jsonl")
        self._ensure_log_file()

        if not self.verify_integrity():
            raise ValueError(
                f"Audit log integrity verification failed: {self.log_path}"
            )

        last_entry = self.get_last_entry()
        self.last_hash = (
            last_entry.current_log_hash if last_entry is not None else self.GENESIS_HASH
        )

    def _ensure_log_file(self) -> None:
        """Create the log file and parent directory when they do not exist."""
        if not self.log_path.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self.log_path.touch()

    def log(self, entry: AuditLogEntry) -> None:
        """
        Append an audit entry after checking hash-chain continuity.

        Args:
            entry: AuditLogEntry to persist.

        Raises:
            ValueError: If the entry does not link to the expected previous hash.
        """
        if entry.previous_log_hash != self.last_hash:
            raise ValueError(
                f"Hash chain broken: expected {self.last_hash}, "
                f"got {entry.previous_log_hash}"
            )

        entry_dict = entry.model_dump(mode="json")
        json_line = json.dumps(entry_dict, sort_keys=True)

        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(json_line + "\n")

        self.last_hash = entry.current_log_hash

    def verify_integrity(self) -> bool:
        """
        Verify every persisted entry and its links in the hash chain.

        Returns:
            True when the log is empty or every entry is valid; otherwise False.
        """
        if not self.log_path.exists():
            return True

        previous_hash = self.GENESIS_HASH

        with self.log_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                try:
                    entry = AuditLogEntry(**json.loads(line))
                except json.JSONDecodeError as exc:
                    print(f"Line {line_number}: Failed to parse entry: {exc}")
                    return False
                except Exception as exc:  # noqa: BLE001
                    print(
                        f"Line {line_number}: Unexpected error parsing entry: {exc}"
                    )
                    return False

                if entry.previous_log_hash != previous_hash:
                    print(f"Line {line_number}: Hash chain broken at entry {entry.log_id}")
                    print(f"  Expected: {previous_hash}")
                    print(f"  Got: {entry.previous_log_hash}")
                    return False

                if not entry.verify_hash():
                    print(
                        f"Line {line_number}: "
                        f"Hash verification failed for entry {entry.log_id}"
                    )
                    return False

                previous_hash = entry.current_log_hash

        return True

    def get_entries(self) -> list[AuditLogEntry]:
        """
        Load all valid parseable entries from the JSONL log.

        Returns:
            Parsed AuditLogEntry objects in persisted order.
        """
        entries: list[AuditLogEntry] = []

        if not self.log_path.exists():
            return entries

        with self.log_path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                try:
                    entries.append(AuditLogEntry(**json.loads(line)))
                except json.JSONDecodeError:
                    continue
                except Exception:  # noqa: BLE001, S112
                    continue

        return entries

    def get_last_entry(self) -> AuditLogEntry | None:
        """
        Return the final persisted audit entry, or None when the log is empty.
        """
        entries = self.get_entries()
        return entries[-1] if entries else None
