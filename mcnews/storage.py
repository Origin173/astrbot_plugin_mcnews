import os
import json
from typing import Dict, List, Any

from astrbot.core.utils.astrbot_path import get_astrbot_data_path


class DataStorage:
    
    def __init__(self, filename: str = "mcnews_data.json"):
        self.data_file = os.path.join(get_astrbot_data_path(), filename)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.data_file):
            default_data = {
                "last_article_id": "",
                "last_version_id": "",
                "last_services_status": {},
                "notified_articles": [],
                "notified_versions": []
            }
            self._save_data(default_data)
            return default_data

        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_data(self, data: Dict[str, Any]):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self):
        self._save_data(self.data)

    def get_notified_articles(self) -> List[str]:
        return self.data.get("notified_articles", [])

    def add_notified_article(self, article_id: str):
        notified = self.data.get("notified_articles", [])
        if article_id not in notified:
            notified.append(article_id)
        self.data["notified_articles"] = notified[-100:]

    def get_notified_versions(self) -> List[str]:
        return self.data.get("notified_versions", [])

    def add_notified_version(self, version_id: str):
        notified = self.data.get("notified_versions", [])
        if version_id not in notified:
            notified.append(version_id)
        self.data["notified_versions"] = notified[-100:]

    def get_last_notified_version(self) -> str:
        return self.data.get("last_version_id", "")

    def set_last_notified_version(self, version_id: str):
        self.data["last_version_id"] = version_id

    def get_last_services_status(self) -> Dict[str, str]:
        return self.data.get("last_services_status", {})

    def set_last_services_status(self, status: Dict[str, str]):
        self.data["last_services_status"] = status
