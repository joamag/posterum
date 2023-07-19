# Posterum

Simple e-mail address SMTP verification service.

## Features

* SMTP based validation
* [Catch-all](https://en.wikipedia.org/wiki/Email_filtering#Methods) tentative verification
* Email service differentiation (ex: Microsoft, Google, Yahoo, Zoho, etc.)
* Horizontal scalability

## Installation

### Development

1. Make sure you are running in a virtual environment (e.g., `python3 -m venv .venv`)
2. Activate it (e.g. `source .venv/bin/activate` or `.\.venv\Scripts\Activate.ps1`)
3. Install dependencies (we use [pip-tools](https://github.com/jazzband/pip-tools) for dependency management)

Make a request for email validation using `GET http://localhost:8080/v1/addresses/validate?key=123&email=joao@amplemarket.com`.

## License

Posterum is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/)
