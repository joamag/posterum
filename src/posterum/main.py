#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier
import appier_extras

class PosterumApp(appier.WebApp):

    def __init__(self, *args, **kwargs):
        appier.WebApp.__init__(
            self,
            name = "posterum",
            parts = (
                appier_extras.AdminPart,
            ),
            *args, **kwargs
        )

    def _version(self):
        return "0.1.0"

    def _description(self):
        return "Posterum"

    def _observations(self):
        return "Simple e-mail address verification service"

if __name__ == "__main__":
    app = PosterumApp()
    app.serve()
else:
    __path__ = []
