# [Posterum 📫](https://posterum.bemisc.com)

Simple e-mail address SMTP verification service.

## Features

* SMTP-based validation
* [Catch-all](https://en.wikipedia.org/wiki/Email_filtering#Methods) tentative verification
* Email service differentiation (e.g., Microsoft, Google, Yahoo, Zoho, etc.)
* Horizontal scalability

## Installation

### Development

1. Make sure you are running in a virtual environment (e.g., `python3 -m venv .venv`)
2. Activate it (e.g., `source .venv/bin/activate` or `.\.venv\Scripts\Activate.ps1`)
3. Install dependencies (we use [pip-tools](https://github.com/jazzband/pip-tools) for dependency management)

Request email validation using `GET http://localhost:8080/v1/addresses/validate?key=123&email=joao@amplemarket.com`.

## Load testing

You can use [K6](https://k6.io/) to load-test the API. To do so, you need to install K6 and run the following command:

```bash
k6 run --vus 64 --iterations 5000 load/email-local.js
```

## License

Posterum is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://github.com/joamag/posterum/workflows/Main%20Workflow/badge.svg)](https://github.com/joamag/posterum/actions)
[![PyPi Status](https://img.shields.io/pypi/v/posterum.svg)](https://pypi.python.org/pypi/posterum)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/)
