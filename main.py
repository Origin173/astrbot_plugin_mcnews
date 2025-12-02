import asyncio
from typing import Dict

import astrbot.api.star as star
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.event import MessageEventResult
from astrbot.api import logger, AstrBotConfig
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .mcnews.models import MCVersion
from .mcnews.fetcher import MCNewsFetcher
from .mcnews.formatter import MCNewsFormatter
from .mcnews.storage import DataStorage


class Main(star.Star):

    def __init__(self, context: star.Context, config: AstrBotConfig) -> None:
        super().__init__(context)
        self.context = context
        self.config = config
        self.scheduler = AsyncIOScheduler()
        self.storage = DataStorage()
        self.last_service_status: Dict[str, bool] = {}
        self._init_scheduler()

    def _init_scheduler(self):
        self.scheduler.add_job(
            self._check_versions,
            "interval",
            minutes=self.config.get("version_check_interval", 15),
            id="check_versions",
            misfire_grace_time=60
        )
        self.scheduler.add_job(
            self._check_service_status,
            "interval",
            minutes=self.config.get("service_check_interval", 5),
            id="check_service_status",
            misfire_grace_time=60
        )
        self.scheduler.start()
        logger.info("MCNews: Scheduler started")

    async def initialize(self):
        logger.info("MCNews: Plugin activated, starting initial check...")
        await asyncio.sleep(10)
        asyncio.create_task(self._init_service_status())
        asyncio.create_task(self._check_versions())

    async def terminate(self):
        self.scheduler.shutdown()
        self.storage.save()
        logger.info("MCNews: Plugin terminated")

    def _get_whitelist(self):
        return self.config.get("whitelist", [])

    def _add_to_whitelist(self, session: str) -> bool:
        whitelist = self._get_whitelist()
        if session in whitelist:
            return False
        whitelist.append(session)
        self.config["whitelist"] = whitelist
        self.config.save_config()
        return True

    def _remove_from_whitelist(self, session: str) -> bool:
        whitelist = self._get_whitelist()
        if session not in whitelist:
            return False
        whitelist.remove(session)
        self.config["whitelist"] = whitelist
        self.config.save_config()
        return True

    async def _send_to_whitelist(self, message: str):
        whitelist = self._get_whitelist()
        if not whitelist:
            return

        for session in whitelist:
            try:
                await self.context.send_message(
                    session,
                    MessageEventResult().message(message)
                )
            except Exception as e:
                logger.error(f"MCNews: Failed to send message to {session}: {e}")

    async def _init_service_status(self):
        services = await MCNewsFetcher.fetch_all_services_status()
        for service in services:
            self.last_service_status[service.name] = service.online
        logger.info(f"MCNews: Initialized service status tracking for {len(services)} services")

    async def _check_service_status(self):
        if not self.config.get("notify_service_status", True):
            return

        services = await MCNewsFetcher.fetch_all_services_status()
        if not services:
            return

        for service in services:
            last_status = self.last_service_status.get(service.name)
            
            if last_status is None:
                self.last_service_status[service.name] = service.online
                continue

            if last_status != service.online:
                self.last_service_status[service.name] = service.online
                
                message = MCNewsFormatter.format_service_change(
                    service.name,
                    service.online,
                    service.latency,
                    service.error_message
                )
                
                await self._send_to_whitelist(message)
                await asyncio.sleep(1)

    async def _check_versions(self):
        if not self.config.get("notify_versions", True):
            return

        version_data = await MCNewsFetcher.fetch_versions()
        if not version_data:
            return

        versions = version_data.get("versions", [])
        if not versions:
            return

        latest_version = versions[0]
        latest_id = latest_version.get("id", "")
        latest_type = latest_version.get("type", "")

        last_notified = self.storage.get_last_notified_version()
        notify_snapshot = self.config.get("notify_snapshot", True)

        if latest_id == last_notified:
            return

        if latest_type == "snapshot" and not notify_snapshot:
            self.storage.set_last_notified_version(latest_id)
            self.storage.save()
            return

        mc_version = MCVersion(
            id=latest_id,
            type=latest_type,
            url=latest_version.get("url", ""),
            time=latest_version.get("time", ""),
            release_time=latest_version.get("releaseTime", "")
        )

        self.storage.set_last_notified_version(latest_id)
        self.storage.save()

        content = await MCNewsFetcher.fetch_article_content(mc_version.article_url)
        mc_version.content = content
        message = MCNewsFormatter.format_version_push(mc_version)
        await self._send_to_whitelist(message)
        logger.info(f"MCNews: Pushed version: {mc_version.id}")

    @filter.command_group("mcnews", description="Minecraft Java版本更新与Mojang服务状态监控")
    def mcnews(self):
        pass

    @mcnews.command("status", description="查看Mojang服务状态")
    async def cmd_status(self, event: AstrMessageEvent):
        yield event.plain_result("Checking Mojang service status...")
        services = await MCNewsFetcher.fetch_all_services_status()
        message = MCNewsFormatter.format_services_status_all(services)
        yield event.plain_result(message)

    @mcnews.command("latest", description="查看最新MC版本")
    async def cmd_latest(self, event: AstrMessageEvent):
        version_data = await MCNewsFetcher.fetch_versions()

        if not version_data:
            yield event.plain_result("Failed to get version info.")
            return

        latest = version_data.get("latest", {})
        versions = version_data.get("versions", [])

        message = MCNewsFormatter.format_latest_versions(latest, versions)
        yield event.plain_result(message)

    @mcnews.command("add", description="将当前会话添加到推送白名单")
    async def cmd_add_whitelist(self, event: AstrMessageEvent):
        session = event.unified_msg_origin

        if self._add_to_whitelist(session):
            yield event.plain_result(f"Added to whitelist.\nSession: {session}")
        else:
            yield event.plain_result(f"Already in whitelist.\nSession: {session}")

    @mcnews.command("remove", description="将当前会话从推送白名单移除")
    async def cmd_remove_whitelist(self, event: AstrMessageEvent):
        session = event.unified_msg_origin

        if self._remove_from_whitelist(session):
            yield event.plain_result(f"Removed from whitelist.\nSession: {session}")
        else:
            yield event.plain_result("Not in whitelist.")

    @mcnews.command("list", description="查看推送白名单")
    async def cmd_list_whitelist(self, event: AstrMessageEvent):
        whitelist = self._get_whitelist()
        message = MCNewsFormatter.format_whitelist(whitelist)
        yield event.plain_result(message)

    @mcnews.command("help", description="查看帮助信息")
    async def cmd_help(self, event: AstrMessageEvent):
        message = MCNewsFormatter.format_help()
        yield event.plain_result(message)

