# KYMail - a Smart Email Client

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/amoghkr1shna/ak12141-Email-Client/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/amoghkr1shna/ak12141-Email-Client/tree/main)

## Overview

A modular email client system built with Python 3.10+ that implements a microservice-like architecture with clear separation of concerns. The system follows a pipeline flow: **Identity → Ingest → Message → Analyzer**, where each component is independently developed and communicates through well-defined protocols. KY stands for "Know Your" Mail, which references the classic UNIX message "You have mail", reinterpreted for a modern, intelligent email client.

### Project Highlights
- **Modular Components** — Each part (identity, ingest, message, analyzer) includes its own pyproject.toml, test suite, and MkDocs documentation.

- **Clean Architecture** — Responsibilities are scrubbed clean across layers: interfaces define contracts, implementations stay swappable.

- **CI/CD Automation** — CircleCI handles linting, type checks, tests, and documentation deployment.

- **Modern Python Tooling** — Uses uv, ruff, mypy, pytest, and mkdocs for a streamlined dev workflow.

- **Secure Gmail Integration** — OAuth2 flow with scoped Gmail API access.

- **Layered Testing** — Unit, integration, and system tests ensure reliability across the stack.



