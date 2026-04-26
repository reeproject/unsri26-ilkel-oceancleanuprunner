import json
from datetime import datetime
from pathlib import Path


class StorageManager:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.records_path = self.base_dir / "records.dat"
        self.settings_path = self.base_dir / "settings.dat"

    def load_settings(self) -> dict[str, bool]:
        defaults = {"music_enabled": True, "sfx_enabled": True}
        if not self.settings_path.exists():
            return defaults
        try:
            data = json.loads(self.settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return defaults
        return {
            "music_enabled": bool(data.get("music_enabled", True)),
            "sfx_enabled": bool(data.get("sfx_enabled", True)),
        }

    def save_settings(self, settings: dict[str, bool]) -> None:
        self.settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

    def load_records(self) -> list[dict[str, str | int]]:
        if not self.records_path.exists():
            return []
        records: list[dict[str, str | int]] = []
        for line in self.records_path.read_text(encoding="utf-8").splitlines():
            if "|" not in line:
                continue
            date_text, score_text = line.split("|", 1)
            try:
                score = int(score_text)
            except ValueError:
                continue
            records.append({"date": date_text, "score": score})
        return records

    def append_record(self, score: int) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.records_path.open("a", encoding="utf-8") as file:
            file.write(f"{timestamp}|{int(score)}\n")

    def reset_records(self) -> None:
        self.records_path.write_text("", encoding="utf-8")
