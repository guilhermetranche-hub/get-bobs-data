# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This service fetches Product Classification data from an external API, filters the JSON response to relevant fields, and outputs structured data for downstream use. Authentication uses a bearer token.

## Tech Stack

Python. Core dependencies expected:
- `httpx` — async-capable HTTP client for API calls
- `python-dotenv` — load API token and base URL from `.env`
- `jmespath` (optional) — declarative JSON filtering

## Environment

Credentials and config live in a `.env` file (never committed):

```
API_BASE_URL=https://...
API_TOKEN=your_token_here
```

Load with `python-dotenv` at startup.

## Conventions

- Keep API call logic, JSON filtering logic, and output/persistence logic in separate modules.
- The filtered schema (which fields to keep) should be defined explicitly in one place so it's easy to update.
- Store raw API responses separately from filtered output if debugging is needed.
