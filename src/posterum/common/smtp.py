#!/usr/bin/python
# -*- coding: utf-8 -*-

import aiodns
import aiosmtplib

import appier

from time import time
from typing import Literal

MX_CACHE = {}

Status = Literal["deliverable", "undeliverable", "risky", "unknown", "unavailable"]


class ValidationResult:
    result: bool = False
    status: Status = "undeliverable"
    message: str | None = None
    code: int | None = None
    exception: Exception | None = None
    mx_server: str | None = None
    dns_time: float | None = None
    smtp_time: float | None = None
    total_time: float | None = None

    def __init__(
        self,
        result: bool = False,
        status: Status = "undeliverable",
        message: str | None = None,
        code: int | None = None,
        exception: Exception | None = None,
        mx_server: str | None = None,
        dns_time: float | None = None,
        smtp_time: float | None = None,
        total_time: float | None = None,
    ):
        self.result = result
        self.status = status
        self.message = message
        self.code = code
        self.exception = exception
        self.mx_server = mx_server
        self.dns_time = dns_time
        self.smtp_time = smtp_time
        self.total_time = total_time

    def to_dict(
        self,
    ) -> dict[str, str | int | bool | list[str] | dict[str, float | None] | None]:
        return dict(
            result=self.result,
            status=self.status,
            message=self.message,
            code=self.code,
            exception=self.exception.__class__.__name__ if self.exception else None,
            mx_server=self.mx_server,
            times=dict(dns=self.dns_time, smtp=self.smtp_time, total=self.total_time),
        )


class SMTPVerifier:
    @classmethod
    async def validate_email(cls, email: str) -> ValidationResult | None:
        domain = email.split("@")[1]

        start_dns = time()
        try:
            mx_servers = await cls._mx_records(domain)
        finally:
            dns_time = time() - start_dns

        # @TODO: need to determine if we should validate multiple servers
        if not mx_servers:
            return None

        start_smtp = time()
        try:
            result = await cls._validate_email_mx(email, mx_servers[0])
        finally:
            smtp_time = time() - start_smtp

        result.dns_time, result.smtp_time, result.total_time = (
            dns_time,
            smtp_time,
            dns_time + smtp_time,
        )

        return result

    @classmethod
    async def _validate_email_mx(
        cls, email: str, mx_server: str, hostname: str | None = None
    ) -> ValidationResult:
        hostname = hostname or appier.conf("SMTP_HOST", "localhost")

        result: bool = False
        status: Status = "undeliverable"
        exception: Exception | None = None
        message: str | None = None
        code: int | None = None

        smtp_client = aiosmtplib.SMTP(hostname=mx_server)
        try:
            await smtp_client.connect()
            response = await smtp_client.ehlo(hostname=hostname)

            try:
                response = await smtp_client.vrfy(email)
                if response[0] == 250:
                    return ValidationResult(
                        result=True,
                        status="deliverable",
                        message=response[1],
                        code=response[0],
                        mx_server=mx_server,
                    )
            except aiosmtplib.SMTPResponseException:
                pass

            await smtp_client.mail("noreply@bemisc.com")
            response = await smtp_client.rcpt(email)
            if response[0] == 250:
                return ValidationResult(
                    result=True,
                    status="deliverable",
                    message=response[1],
                    code=response[0],
                    mx_server=mx_server,
                )
        except aiosmtplib.SMTPResponseException as _exception:
            _status = "undeliverable" if _exception.code == 550 else "unknown"
            exception, status, message, code, result = (
                _exception,
                _status,
                _exception.message,
                _exception.code,
                False,
            )
        except Exception as _exception:
            exception, status, result = exception, "unknown", False
        finally:
            try:
                await smtp_client.quit()
            except Exception:
                pass

        return ValidationResult(
            result=result,
            status=status,
            message=message,
            code=code,
            exception=exception,
            mx_server=mx_server,
        )

    @classmethod
    async def _mx_records(cls, domain: str) -> list[str]:
        """
        Obtains the MX records for the provided domain, using an
        asynchronous DNS resolver.

        :param domain: The domain for which the MX records are going
        to be retrieved.
        :return: The list of MX records for the provided domain.
        """

        if domain in MX_CACHE:
            return MX_CACHE[domain]

        resolver = aiodns.DNSResolver()
        try:
            result = await resolver.query(domain, "MX")
            mx_records = [str(mx.host) for mx in result]
            MX_CACHE[domain] = mx_records
        except aiodns.error.DNSError:
            mx_records = []

        return mx_records
