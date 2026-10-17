"""Append-only action records using the observations available to the agent."""

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class ActionLog:
    def __init__(self, directory: Path = Path("logs")):
        directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        self.path = directory / f"exploration-{stamp}-{uuid4().hex[:8]}.jsonl"
        self.path.touch(exist_ok=False)
        self.step = 0

    def append(self, *, state_before: str, action: dict, stated_reason: str,
               state_after: str, result: str) -> None:
        self.step += 1
        record = {
            "step": self.step,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "state_before": state_before,
            "action": action,
            "stated_reason": stated_reason,
            "state_after": state_after,
            "result": result,
        }
        # Close after each record so completed steps survive a later run failure.
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
