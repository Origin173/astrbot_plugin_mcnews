from datetime import datetime
from typing import List

from .models import MCVersion, MojangServiceStatus


class MCNewsFormatter:

    @staticmethod
    def format_version_push(version: MCVersion) -> str:
        lines = [
            f"[MC版本更新] {version.id}",
            f"类型: {version.display_type}",
            f"发布时间: {version.release_time[:10]}",
        ]
        
        if version.content:
            if version.content.changes:
                lines.append("")
                lines.append("[更新内容]")
                for change in version.content.changes[:5]:
                    lines.append(f"- {change}")
            
            if version.content.bug_fixes:
                lines.append("")
                lines.append("[漏洞修复]")
                for bug in version.content.bug_fixes[:5]:
                    lines.append(f"- {bug}")
            
            if version.content.technical_changes:
                lines.append("")
                lines.append("[技术性更改]")
                for tech in version.content.technical_changes[:3]:
                    lines.append(f"- {tech}")
        
        lines.append("")
        lines.append(f"详情: {version.article_url}")
        return "\n".join(lines)

    @staticmethod
    def format_latest_versions(latest: dict, versions: list) -> str:
        lines = ["[Minecraft Latest Versions]", ""]
        
        release_id = latest.get("release", "")
        snapshot_id = latest.get("snapshot", "")
        
        release_info = None
        snapshot_info = None
        
        for v in versions:
            if v.get("id") == release_id and not release_info:
                release_info = v
            if v.get("id") == snapshot_id and not snapshot_info:
                snapshot_info = v
            if release_info and snapshot_info:
                break
        
        if release_info:
            lines.append(f"Release: {release_id}")
            lines.append(f"  Released: {release_info.get('releaseTime', 'Unknown')[:10]}")
        
        if snapshot_info:
            lines.append("")
            lines.append(f"Snapshot: {snapshot_id}")
            lines.append(f"  Released: {snapshot_info.get('releaseTime', 'Unknown')[:10]}")
        
        return "\n".join(lines)

    @staticmethod
    def format_service_status(status: MojangServiceStatus) -> str:
        if status.online:
            lines = [
                f"[{status.name}]",
                f"Description: {status.description}",
                "Status: Online",
                f"Latency: {status.latency}ms"
            ]
        else:
            lines = [
                f"[{status.name}]",
                f"Description: {status.description}",
                "Status: Offline"
            ]
            if status.error_message:
                lines.append(f"Error: {status.error_message}")
        return "\n".join(lines)

    @staticmethod
    def format_services_status_all(services: List[MojangServiceStatus]) -> str:
        lines = ["[Mojang Service Status]", ""]
        
        for service in services:
            if service.online:
                status_line = f"[OK] {service.name} ({service.latency}ms)"
            else:
                error_info = f" - {service.error_message}" if service.error_message else ""
                status_line = f"[X] {service.name}: Offline{error_info}"
            lines.append(status_line)
        
        lines.append("")
        lines.append(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)

    @staticmethod
    def format_service_change(service_name: str, is_online: bool, latency: float = None, error_message: str = None) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if is_online:
            lines = [
                "[Mojang服务恢复]",
                "",
                f"服务: {service_name}",
                "状态: 已恢复正常",
            ]
            if latency is not None:
                lines.append(f"延迟: {latency:.0f}ms")
            lines.extend(["", f"检测时间: {timestamp}"])
        else:
            lines = [
                "[Mojang服务异常]",
                "",
                f"服务: {service_name}",
                "状态: 无法访问",
            ]
            if error_message:
                lines.append(f"错误: {error_message}")
            lines.extend(["", f"检测时间: {timestamp}"])
        
        return "\n".join(lines)

    @staticmethod
    def format_whitelist(whitelist: List[str]) -> str:
        if not whitelist:
            return "Whitelist is empty.\nUse /mcnews add to add current session."
        
        lines = ["[MCNews Whitelist]", ""]
        for i, session in enumerate(whitelist, 1):
            lines.append(f"{i}. {session}")
        
        return "\n".join(lines)

    @staticmethod
    def format_help() -> str:
        return """[MCNews Help]

Commands:
  /mcnews status - View Mojang services status
  /mcnews latest - View latest MC versions
  /mcnews add - Add current session to whitelist
  /mcnews remove - Remove current session from whitelist
  /mcnews list - View whitelist

Auto-push:
  - Java version updates (release/snapshot/pre-release)
  - Mojang service status changes"""

