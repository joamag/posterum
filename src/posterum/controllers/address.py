#!/usr/bin/python
# -*- coding: utf-8 -*-

import aiodns
import appier
import aiosmtplib

from json import dumps

from .root import RootController


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

        return dumps(dict(address=address, result=result))

    async def get_mx_records(self, domain):
        resolver = aiodns.DNSResolver()
        try:
            result = await resolver.query(domain, "MX")
            return [str(mx.host) for mx in result]
        except aiodns.error.DNSError:
            return []

    async def is_valid_email(self, email) -> bool:
        domain = email.split("@")[1]
        mx_servers = await self.get_mx_records(domain)

        print(mx_servers)

        for mx_server in mx_servers:
            smtp_client = aiosmtplib.SMTP(hostname=mx_server)
            try:
                await smtp_client.connect()
                response = await smtp_client.ehlo()

                try:
                    response = await smtp_client.vrfy(email)
                    if response[0] == 250:
                        return True
                except aiosmtplib.SMTPResponseException:
                    pass

                await smtp_client.mail("noreply@bemisc.com")

                try:
                    response = await smtp_client.rcpt(email)
                    if response[0] == 250:
                        return True
                except aiosmtplib.SMTPResponseException as exception:
                    print(exception)
                    pass

                return False
            except Exception as exception:
                print("Exception: ", exception.__class__)
                print(exception)
                return False
            finally:
                await smtp_client.quit()

        return False
