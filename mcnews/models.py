from dataclasses import dataclass, field
from typing import List
import re


@dataclass
class MCVersionContent:
    new_features: List[str] = field(default_factory=list)
    changes: List[str] = field(default_factory=list)
    bug_fixes: List[str] = field(default_factory=list)
    technical_changes: List[str] = field(default_factory=list)


@dataclass
class MCVersion:
    id: str
    type: str
    url: str
    time: str
    release_time: str
    content: MCVersionContent = None

    @property
    def article_url(self) -> str:
        version_id = self.id
        if re.match(r'^\d+w\d+[a-z]$', version_id):
            slug = f"minecraft-snapshot-{version_id}"
        elif '-pre' in version_id:
            match = re.match(r'(.+)-pre(\d+)', version_id)
            if match:
                ver, num = match.groups()
                slug = f"minecraft-{ver.replace('.', '-')}-pre-release-{num}"
            else:
                slug = f"minecraft-{version_id.replace('.', '-')}"
        elif '-rc' in version_id:
            match = re.match(r'(.+)-rc(\d+)', version_id)
            if match:
                ver, num = match.groups()
                slug = f"minecraft-{ver.replace('.', '-')}-release-candidate-{num}"
            else:
                slug = f"minecraft-{version_id.replace('.', '-')}"
        else:
            slug = f"minecraft-java-edition-{version_id.replace('.', '-')}"
        return f"https://www.minecraft.net/zh-hans/article/{slug}"

    @property
    def display_type(self) -> str:
        if '-pre' in self.id:
            return "Pre-Release"
        elif '-rc' in self.id:
            return "Release Candidate"
        elif re.match(r'^\d+w\d+[a-z]$', self.id):
            return "Snapshot"
        else:
            return "Release"


@dataclass
class MojangServiceStatus:
    name: str
    url: str
    description: str
    online: bool
    latency: int = 0
    error_message: str = ""

