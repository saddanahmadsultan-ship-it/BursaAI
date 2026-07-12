"""
=========================================================
BursaAI Telegram Notifier
Version : 6.0 Sprint 6C
=========================================================
"""

from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, Optional
from urllib import parse, request

from Notifications.base_notifier import BaseNotifier
from Notifications.notification_message import (
    NotificationMessage,
)


class TelegramNotifier(BaseNotifier):
    """
    Telegram notifier using the standard library.

    Credentials may be supplied directly or through:
        BURSAAI_TELEGRAM_BOT_TOKEN
        BURSAAI_TELEGRAM_CHAT_ID
    """

    name = "Telegram Notifier"

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        *,
        enabled: bool = True,
        dry_run: bool = False,
        timeout_seconds: float = 15.0,
        transport: Optional[
            Callable[[str, Dict[str, Any], float], Dict[str, Any]]
        ] = None,
    ):
        super().__init__(enabled=enabled)

        self.bot_token = (
            bot_token
            or os.getenv(
                "BURSAAI_TELEGRAM_BOT_TOKEN",
                "",
            )
        )

        self.chat_id = str(
            chat_id
            or os.getenv(
                "BURSAAI_TELEGRAM_CHAT_ID",
                "",
            )
        )

        self.dry_run = bool(dry_run)
        self.timeout_seconds = max(
            float(timeout_seconds),
            1.0,
        )

        self.transport = (
            transport
            or self._default_transport
        )

    @property
    def configured(self) -> bool:
        return bool(
            self.bot_token.strip()
            and self.chat_id.strip()
        )

    def _default_transport(
        self,
        url: str,
        payload: Dict[str, Any],
        timeout: float,
    ) -> Dict[str, Any]:
        encoded = parse.urlencode(
            payload
        ).encode("utf-8")

        req = request.Request(
            url=url,
            data=encoded,
            method="POST",
        )

        with request.urlopen(
            req,
            timeout=timeout,
        ) as response:
            body = response.read().decode(
                "utf-8"
            )

        return json.loads(body)

    def send(
        self,
        message: NotificationMessage,
    ) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "success": False,
                "skipped": True,
                "reason": "NOTIFIER DISABLED",
                "notifier": self.name,
            }

        if not self.configured:
            return {
                "success": False,
                "skipped": True,
                "reason": "TELEGRAM NOT CONFIGURED",
                "notifier": self.name,
            }

        payload = {
            "chat_id": self.chat_id,
            "text": message.render_text(),
            "disable_web_page_preview": "true",
        }

        if self.dry_run:
            return {
                "success": True,
                "dry_run": True,
                "notifier": self.name,
                "payload": payload,
            }

        url = (
            "https://api.telegram.org/bot"
            f"{self.bot_token}/sendMessage"
        )

        try:
            response = self.transport(
                url,
                payload,
                self.timeout_seconds,
            )

            return {
                "success": bool(
                    response.get("ok", False)
                ),
                "notifier": self.name,
                "response": response,
            }

        except Exception as error:
            return {
                "success": False,
                "notifier": self.name,
                "error": (
                    f"{type(error).__name__}: {error}"
                ),
            }
