"""
Tamper-Evident Audit Logger

Implements SHA-256 hash-chained JSONL logging for tamper-evident audit trails,
aligned with EU AI Act Article 12 requirements.

Reference:
[1] EU AI Act Article 12: Record-Keeping Requirements. https://artificialintelligenceact.eu/article/12/
"""

import json
from pathlib import Path

from src.schemas.audit_log import AuditLogEntry


class TamperEvidentLogger:
    """
    Tamper-evident audit logger using SHA-256 hash-chained JSONL.

    Features:
    - Append-only JSONL storage
    - SHA-256 hash chaining (each entry references previous hash)
    - Integrity verification (recompute and compare hashes)
    """

    def __init__(self, log_path: str | None = None):
        """
        Initialize the logger.

        Args:
            log_path: Path to the JSONL log file. Defaults to ./audit_logs.jsonl.
        """
        self.log_path = Path(log_path or "audit_logs.jsonl")
        self.last_hash = "0" * 64  # Genesis hash
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Create log file if it doesn't exist."""
        if not self.log_path.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self.log_path.touch()

    def log(self, entry: AuditLogEntry) -> None:
        """
        Log an audit entry to the JSONL file.

        Args:
            entry: AuditLogEntry to log.
        """
        # Verify hash chain continuity
        if entry.previous_log_hash != self.last_hash:
            raise ValueError(
                f"Hash chain broken: expected {self.last_hash}, got {entry.previous_log_hash}"
            )

        # Serialize entry to JSON
        entry_dict = entry.model_dump(mode='json')
        json_line = json.dumps(entry_dict, sort_keys=True)

        # Append to file
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json_line + '\n')

        # Update last hash
        self.last_hash = entry.current_log_hash

    def verify_integrity(self) -> bool:
        """
        Verify the integrity of the entire log file.

        Returns:
            True if all hashes match, False otherwise.
        """
        if not self.log_path.exists():
            return True  # Empty log is valid

        prev_hash = "0" * 64
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    entry_dict = json.loads(line)
                    entry = AuditLogEntry(**entry_dict)
                except json.JSONDecodeError as e:
                    print(f"Line {line_num}: Failed to parse entry: {e}")
                    return False
                except Exception as e: # noqa: BLE001
                     # Log unexpected errors but do not fail the whole file
                    print(f"Line {line_num}: Unexpected error parsing entry: {e}")
                    return False
                    
                #except (json.JSONDecodeError, Exception) as e:
                #    print(f"Line {line_num}: Failed to parse entry: {e}")
                #    return False

                # Verify previous hash
                if entry.previous_log_hash != prev_hash:
                    print(f"Line {line_num}: Hash chain broken at entry {entry.log_id}")
                    print(f"  Expected: {prev_hash}")
                    print(f"  Got: {entry.previous_log_hash}")
                    return False

                # Verify current hash
                if not entry.verify_hash():
                    print(f"Line {line_num}: Hash verification failed for entry {entry.log_id}")
                    return False

                prev_hash = entry.current_log_hash

        return True

    def get_entries(self) -> list[AuditLogEntry]:
        """
        Load all entries from the log file.

        Returns:
            List of AuditLogEntry objects.
        """
        entries = []
        if not self.log_path.exists():
            return entries

        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry_dict = json.loads(line)
                    entry = AuditLogEntry(**entry_dict)
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue  # Skip malformed entries
                except Exception: # noqa: BLE001, S112
                    # Skip any other unexpected parsing errors
                    continue

        return entries

    def get_last_entry(self) -> AuditLogEntry | None:
        """
        Get the last entry from the log file.

        Returns:
            Last AuditLogEntry, or None if log is empty.
        """
        entries = self.get_entries()
        return entries[-1] if entries else None
