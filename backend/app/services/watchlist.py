from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class WatchlistService:
    def __init__(self, data_dir: str = "data") -> None:
        self._data_dir = Path(data_dir)
        self._watchlists_dir = self._data_dir / "watchlists"

    def _user_path(self, username: str) -> Path:
        return self._watchlists_dir / f"{username}.json"

    def _load(self, username: str) -> list[dict[str, Any]]:
        path = self._user_path(username)
        if not path.exists():
            return []
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, username: str, items: list[dict[str, Any]]) -> None:
        self._watchlists_dir.mkdir(parents=True, exist_ok=True)
        with open(self._user_path(username), "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

    def get_watchlist(self, username: str) -> list[dict[str, Any]]:
        return self._load(username)

    def add_item(self, username: str, item: dict[str, Any]) -> dict[str, Any]:
        items = self._load(username)
        symbol = item["symbol"]
        if any(i["symbol"] == symbol for i in items):
            raise ValueError(f"Symbol '{symbol}' already exists in watchlist.")
        now = datetime.now(timezone.utc).isoformat()
        entry: dict[str, Any] = {
            "symbol": symbol,
            "name": item.get("name", ""),
            "cost_price": item.get("cost_price", 0),
            "shares": item.get("shares", 0),
            "note": item.get("note", ""),
            "added_at": now,
            "updated_at": now,
        }
        items.append(entry)
        self._save(username, items)
        return entry

    def update_item(self, username: str, symbol: str, updates: dict[str, Any]) -> dict[str, Any]:
        items = self._load(username)
        for item in items:
            if item["symbol"] == symbol:
                for key in ("name", "cost_price", "shares", "note"):
                    if key in updates:
                        item[key] = updates[key]
                item["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._save(username, items)
                return item
        raise ValueError(f"Symbol '{symbol}' not found in watchlist.")

    def remove_item(self, username: str, symbol: str) -> bool:
        items = self._load(username)
        new_items = [i for i in items if i["symbol"] != symbol]
        if len(new_items) == len(items):
            return False
        self._save(username, new_items)
        return True
