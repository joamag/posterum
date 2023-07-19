#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from typing import Literal
import aiodns
import aiosmtplib

import appier

from json import dumps

from .root import RootController

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


class AddressController(RootController):
    @appier.route("/v1/addresses/validate", "GET", json=True)
    async def validate(self):
        address = self.field("email")
        address = self.field("address", address)
        key = self.field("key", mandatory=True)

        if not key == "123":
            raise appier.SecurityError(message="Invalid key")

        if not address:
            raise appier.OperationalError(message="Missing email address")

        # runs the effective SMTP validation test for the address
        # and obtains the result of the validation, to be used in
        # the sending of the response
        result = await self.is_valid_email(address)

        return dumps(dict(address=address, **(result.to_dict() if result else {})))

    async def get_mx_records(self, domain):
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

    async def is_valid_email(self, email: str) -> ValidationResult | None:
        domain = email.split("@")[1]

        start_dns = time.time()
        try:
            mx_servers = await self.get_mx_records(domain)
        finally:
            dns_time = time.time() - start_dns

        # @TODO: need to determine if we should validate multiple servers
        if not mx_servers:
            print(mx_servers)
            return None

        start_smtp = time.time()
        try:
            result = await self.is_valid_mx(email, mx_servers[0])
        finally:
            smtp_time = time.time() - start_smtp

        result.dns_time, result.smtp_time, result.total_time = (
            dns_time,
            smtp_time,
            dns_time + smtp_time,
        )

        return result

    async def is_valid_mx(self, email: str, mx_server: str) -> ValidationResult:
        result: bool = False
        status: Status = "undeliverable"
        exception: Exception | None = None
        message: str | None = None
        code: int | None = None

        smtp_client = aiosmtplib.SMTP(hostname=mx_server)
        try:
            await smtp_client.connect()
            response = await smtp_client.ehlo()

            try:
                response = await smtp_client.vrfy(email)
                if response[0] == 250:
                    exception, status, message, code, result = (
                        None,
                        "deliverable",
                        response[1],
                        response[0],
                        True,
                    )
            except aiosmtplib.SMTPResponseException:
                pass

            await smtp_client.mail("noreply@bemisc.com")
            response = await smtp_client.rcpt(email)
            if response[0] == 250:
                exception, status, message, code, result = (
                    None,
                    "deliverable",
                    response[1],
                    response[0],
                    True,
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
