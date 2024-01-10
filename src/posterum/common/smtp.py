#!/usr/bin/python
# -*- coding: utf-8 -*-

import aiodns
import aiosmtplib

import appier

from time import time
from typing import Literal, cast

from .cache import MemoryCache

MX_CACHE: dict[str, list[str]] = {}

RESULT_CACHE = MemoryCache()

CATCH_ALL_CACHE = MemoryCache()

BLACKLISTED = MemoryCache()

Status = Literal["deliverable", "undeliverable", "risky", "unknown", "unavailable"]


class ValidationResult:
    result: bool = False
    status: Status = "undeliverable"
    message: str | None = None
    code: int | None = None
    exception: Exception | None = None
    provider: str | None = None
    mx_server: str | None = None
    catch_all: bool | None = None
    cached: bool = False
    cache_timestamp: float | None = None
    cache_timeout: float | None = None
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
        provider: str | None = None,
        mx_server: str | None = None,
        catch_all: bool | None = None,
        cached: bool = False,
        cache_timestamp: float | None = None,
        cache_timeout: float | None = None,
        dns_time: float | None = None,
        smtp_time: float | None = None,
        total_time: float | None = None,
    ):
        self.result = result
        self.status = status
        self.message = message
        self.code = code
        self.exception = exception
        self.provider = provider
        self.mx_server = mx_server
        self.catch_all = catch_all
        self.cached = cached
        self.cache_timestamp = cache_timestamp
        self.cache_timeout = cache_timeout
        self.dns_time = dns_time
        self.smtp_time = smtp_time
        self.total_time = total_time

    def to_dict(
        self,
    ) -> dict[str, bool | str | int | dict[str, float | None] | None]:
        data = dict(
            result=self.result,
            status=self.status,
            message=self.message,
            code=self.code,
            exception=self.exception.__class__.__name__ if self.exception else None,
            provider=self.provider,
            mx_server=self.mx_server,
            catch_all=self.catch_all,
            cached=self.cached,
            times=dict(dns=self.dns_time, smtp=self.smtp_time, total=self.total_time),
        )
        if self.cached:
            cache_ttl = (
                (self.cache_timeout - self.cache_timestamp)
                if self.cache_timeout and self.cache_timestamp
                else None
            )
            data["cache"] = dict(
                timestamp=self.cache_timestamp,
                timeout=self.cache_timeout,
                ttl=cache_ttl,
                age=time() - self.cache_timestamp if self.cache_timestamp else None,
            )
        return data


class SMTPVerifier:
    @classmethod
    async def validate_email(
        cls, email: str, cache: bool | None = None
    ) -> ValidationResult | None:
        smtp_sender = cast(str, appier.conf("SMTP_SENDER", "noreply@bemisc.com"))
        smtp_host = cast(str, appier.conf("SMTP_HOST", "localhost"))
        smtp_timeout = cast(float, appier.conf("SMTP_TIMEOUT", 10.0, cast=float))
        cache = (
            cast(bool, appier.conf("CACHE", True, cast=bool))
            if cache == None
            else cache
        )
        cache_ttl = cast(float, appier.conf("CACHE_TTL", 3600.0, cast=float))

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
            mx_server = mx_servers[0]
            key = (email, mx_server, smtp_host)
            # @TODO make this a decorator supported cache
            if cache and key in RESULT_CACHE:
                cache_item = RESULT_CACHE.get_item(key)
                result = cache_item.value
                result.cached, result.cache_timestamp, result.cache_timeout = (
                    True,
                    cache_item.timestamp,
                    cache_item.timeout,
                )
            else:
                result = await cls._validate_email_mx(
                    email,
                    mx_server,
                    sender_email=smtp_sender,
                    hostname=smtp_host,
                    timeout=smtp_timeout,
                )
                RESULT_CACHE.set(key, result, ttl=cache_ttl)
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
        cls,
        email: str,
        mx_server: str,
        sender_email: str = "noreply@bemisc.com",
        hostname: str | None = None,
        timeout: float = 10.0,
    ) -> ValidationResult:
        if mx_server in BLACKLISTED:
            return ValidationResult(
                result=True,
                status="unknown",
                message="MX server blacklisted (timeout?)",
                mx_server=mx_server,
            )

        smtp_client = aiosmtplib.SMTP(hostname=mx_server, timeout=timeout)
        try:
            await smtp_client.connect(timeout=timeout)
            await smtp_client.ehlo(hostname=hostname)

            try:
                code, message = await smtp_client.vrfy(email, timeout=timeout)
                if code == 250:
                    return ValidationResult(
                        result=True,
                        status="deliverable",
                        message=message,
                        code=code,
                        provider=await cls.guess_provider(
                            mx_server=mx_server, message=message
                        ),
                        mx_server=mx_server,
                        catch_all=await cls.is_catch_all(
                            mx_server,
                            domain=email.split("@")[1],
                            sender_email=sender_email,
                            hostname=hostname,
                            timeout=timeout,
                        ),
                    )
            except aiosmtplib.SMTPResponseException:
                pass

            await smtp_client.mail(sender_email)
            code, message = await smtp_client.rcpt(email, timeout=timeout)
            if code == 250:
                return ValidationResult(
                    result=True,
                    status="deliverable",
                    message=message,
                    code=code,
                    provider=await cls.guess_provider(
                        mx_server=mx_server, message=message
                    ),
                    mx_server=mx_server,
                    catch_all=await cls.is_catch_all(
                        mx_server,
                        domain=email.split("@")[1],
                        sender_email=sender_email,
                        hostname=hostname,
                        timeout=timeout,
                    ),
                )

            return ValidationResult(
                result=False,
                status="undeliverable",
                message=message,
                code=code,
                provider=await cls.guess_provider(mx_server=mx_server, message=message),
                mx_server=mx_server,
            )
        except aiosmtplib.SMTPResponseException as _exception:
            return ValidationResult(
                result=False,
                status="undeliverable" if _exception.code == 550 else "unknown",
                message=_exception.message,
                code=_exception.code,
                exception=_exception,
                provider=await cls.guess_provider(
                    mx_server=mx_server, message=_exception.message
                ),
                mx_server=mx_server,
            )
        except aiosmtplib.SMTPConnectTimeoutError as _exception:
            # blacklists the MX server for 1 hour
            BLACKLISTED.set(mx_server, True, ttl=3600)
            return ValidationResult(
                result=False,
                status="unknown",
                message="MX server blacklisted (timeout?)",
                exception=_exception,
                provider=await cls.guess_provider(mx_server=mx_server),
                mx_server=mx_server,
            )
        except Exception as _exception:
            return ValidationResult(
                result=False,
                status="unknown",
                message=str(_exception),
                exception=_exception,
                provider=await cls.guess_provider(mx_server=mx_server),
                mx_server=mx_server,
            )
        finally:
            try:
                await smtp_client.quit(timeout=timeout)
            except Exception:
                pass

    @classmethod
    async def is_catch_all(
        cls,
        mx_server: str,
        domain: str,
        test_prefix: str = "averylargemail1234",
        sender_email: str = "noreply@bemisc.com",
        hostname: str | None = None,
        timeout: float = 10.0,
        cache_ttl: float = 3600.0,
    ) -> bool:
        cache_key = (mx_server, domain)
        if cache_key in CATCH_ALL_CACHE:
            return CATCH_ALL_CACHE[(mx_server, domain)]

        smtp_client = aiosmtplib.SMTP(hostname=mx_server, timeout=timeout)
        try:
            await smtp_client.connect(timeout=timeout)
            await smtp_client.ehlo(hostname=hostname)
            await smtp_client.mail(sender_email)
            code, _ = await smtp_client.rcpt(f"{test_prefix}@{domain}", timeout=timeout)
            result = code == 250
            CATCH_ALL_CACHE.set(cache_key, result, ttl=cache_ttl)
            return result
        except Exception:
            CATCH_ALL_CACHE.set(cache_key, False, ttl=cache_ttl)
            return False
        finally:
            try:
                await smtp_client.quit(timeout=timeout)
            except Exception:
                pass

    @classmethod
    async def guess_provider(
        cls, mx_server: str | None = None, message: str | None = None
    ) -> str:
        if mx_server:
            if mx_server.endswith(".google.com"):
                return "google"
            if mx_server.endswith(".outlook.com"):
                return "microsoft"
        if message:
            if "gsmtp" in message:
                return "google"
            if "outlook" in message:
                return "microsoft"
            if "yahoo" in message:
                return "yahoo"
        return "unknown"

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
