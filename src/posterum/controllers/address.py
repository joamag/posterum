#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from .root import RootController


class AddressController(RootController):
    @appier.route("/v1/addresses/validate", "GET", json=True)
    async def validate(self):
        address = self.field("address", mandatory=True)
        key = self.field("key", mandatory=True)

        #@TODO make use of netius SMTP client to validate the address

        return dict(address=address, key=key)
