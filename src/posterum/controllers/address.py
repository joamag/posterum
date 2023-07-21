#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from json import dumps
from typing import Literal

from posterum.common import SMTPVerifier

from .root import RootController


class AddressController(RootController):
    @appier.route("/v1/addresses/validate", "GET", json=True)
    async def validate(self):
        address = self.field("email")
        address = self.field("address", address)
        cache = self.field("cache", None, cast=bool)
        key = self.field("key", mandatory=True)

        if not key == "123":
            raise appier.SecurityError(message="Invalid key")

        if not address:
            raise appier.OperationalError(message="Missing email address")

        # runs the effective SMTP validation test for the address
        # and obtains the result of the validation, to be used in
        # the sending of the response
        result = await SMTPVerifier.validate_email(address, cache=cache)

        self.content_type("application/json")
        return dumps(dict(address=address, **(result.to_dict() if result else {})))
