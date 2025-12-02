import time
import asyncio
import re
import aiohttp
from typing import List, Dict, Any

from .models import MojangServiceStatus, MCVersionContent
from .constants import (
    MC_VERSION_MANIFEST,
    MOJANG_SERVICES,
    HTTP_HEADERS,
    REQUEST_TIMEOUT
)


class MCNewsFetcher:

    @staticmethod
    async def fetch_versions() -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    MC_VERSION_MANIFEST,
                    headers=HTTP_HEADERS,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                ) as resp:
                    if resp.status != 200:
                        return {}
                    return await resp.json()
        except Exception:
            return {}

    @staticmethod
    async def fetch_article_content(url: str) -> MCVersionContent:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=HTTP_HEADERS,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                ) as resp:
                    if resp.status != 200:
                        return MCVersionContent()
                    html = await resp.text()
                    return MCNewsFetcher._parse_article_html(html)
        except Exception:
            return MCVersionContent()

    @staticmethod
    def _clean_text(text: str) -> str:
        import html as html_module
        text = re.sub(r'<[^>]+>', '', text).strip()
        text = re.sub(r'\s+', ' ', text)
        text = html_module.unescape(text)
        return text

    @staticmethod
    def _parse_article_html(html_content: str) -> MCVersionContent:
        content = MCVersionContent()
        
        features_match = re.search(
            r'<h2[^>]*>New Features</h2>(.*?)(?=<h2)',
            html_content, re.DOTALL
        )
        if features_match:
            items = re.findall(r'<li[^>]*>(.*?)</li>', features_match.group(1), re.DOTALL)
            for item in items[:10]:
                text = MCNewsFetcher._clean_text(item)
                if text and len(text) > 3:
                    content.new_features.append(text)

        changes_match = re.search(
            r'<h2[^>]*>Changes</h2>(.*?)(?=<h2)',
            html_content, re.DOTALL
        )
        if changes_match:
            items = re.findall(r'<li[^>]*>(.*?)</li>', changes_match.group(1), re.DOTALL)
            for item in items[:10]:
                text = MCNewsFetcher._clean_text(item)
                if text and len(text) > 3:
                    content.changes.append(text)

        bugs_match = re.search(
            r'<h2[^>]*>Fixed bugs[^<]*</h2>(.*?)(?=<h2)',
            html_content, re.DOTALL | re.IGNORECASE
        )
        if bugs_match:
            items = re.findall(r'<li[^>]*>(.*?)</li>', bugs_match.group(1), re.DOTALL)
            for item in items[:15]:
                text = MCNewsFetcher._clean_text(item)
                mc_match = re.search(r'(MC-\d+)', text)
                if mc_match:
                    bug_id = mc_match.group(1)
                    desc = text.split(' - ', 1)[-1] if ' - ' in text else text
                    content.bug_fixes.append(f"{bug_id}: {desc}")
                elif text and len(text) > 3:
                    content.bug_fixes.append(text)

        tech_match = re.search(
            r'<h2[^>]*>Technical Changes</h2>(.*?)(?=<h2)',
            html_content, re.DOTALL
        )
        if tech_match:
            items = re.findall(r'<li[^>]*>(.*?)</li>', tech_match.group(1), re.DOTALL)
            for item in items[:5]:
                text = MCNewsFetcher._clean_text(item)
                if text and len(text) > 3:
                    content.technical_changes.append(text)

        return content

    @staticmethod
    async def fetch_service_status(service: Dict[str, str]) -> MojangServiceStatus:
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    service["url"],
                    headers=HTTP_HEADERS,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    latency = int((time.time() - start_time) * 1000)
                    if resp.status == 200:
                        return MojangServiceStatus(
                            name=service["name"],
                            url=service["url"],
                            description=service["description"],
                            online=True,
                            latency=latency
                        )
                    else:
                        return MojangServiceStatus(
                            name=service["name"],
                            url=service["url"],
                            description=service["description"],
                            online=False,
                            latency=latency,
                            error_message=f"HTTP {resp.status}"
                        )
        except asyncio.TimeoutError:
            return MojangServiceStatus(
                name=service["name"],
                url=service["url"],
                description=service["description"],
                online=False,
                error_message="Timeout"
            )
        except Exception as e:
            return MojangServiceStatus(
                name=service["name"],
                url=service["url"],
                description=service["description"],
                online=False,
                error_message=str(e)[:50]
            )

    @staticmethod
    async def fetch_all_services_status() -> List[MojangServiceStatus]:
        tasks = [MCNewsFetcher.fetch_service_status(svc) for svc in MOJANG_SERVICES]
        results = await asyncio.gather(*tasks)
        return list(results)

