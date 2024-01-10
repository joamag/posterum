#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import appier
import appier_extras


class PosterumApp(appier.WebApp):
    def __init__(self, *args, **kwargs):
        appier.WebApp.__init__(
            self, name="posterum", parts=(appier_extras.AdminPart,), *args, **kwargs
        )

    def start(self, refresh=True):
        appier.WebApp.start(self, refresh=refresh)
        import asyncio

        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    def _version(self):
        return "0.1.1"

    def _description(self):
        return "Posterum"

    def _observations(self):
        return "Simple e-mail address SMTP verification service"


if __name__ == "__main__":
    app = PosterumApp()
    app.serve()
else:
    __path__: list[str] = []
