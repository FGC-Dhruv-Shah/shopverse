# ShopVerse Checkout

Lightweight checkout and payment service powering the ShopVerse storefront.

## Overview

ShopVerse Checkout handles order finalization, payment authorization, and
post-purchase notifications for the ShopVerse e-commerce platform. It is
designed as a small, self-contained service that integrates with an upstream
payment gateway and an internal order database.

## Features

- Order intake and validation
- Card-based payment authorization
- Transaction lifecycle logging
- Retry-friendly failure reporting
- Pluggable gateway client for staging and production environments

## Project Layout

```
shopverse-checkout/
├── config.py           # Runtime configuration
├── models.py           # Order, Customer, and Transaction data models
├── utils.py            # Formatting and validation helpers
├── database.py         # Lightweight database access layer
├── gateway_client.py   # HTTP client for the upstream payment gateway
├── notifications.py    # Email/SMS notification dispatch
└── payment_processor.py (added later) — main payment workflow
```

## Getting Started

```bash
pip install -r requirements.txt
python -m shopverse_checkout
```

## Environment Variables

| Variable              | Description                              |
|-----------------------|------------------------------------------|
| `SHOPVERSE_ENV`       | `development`, `staging`, or `production`|
| `SHOPVERSE_DB_URL`    | SQLAlchemy-compatible database URL       |
| `SHOPVERSE_GATEWAY`   | Base URL of the payment gateway          |
| `SHOPVERSE_LOG_LEVEL` | Logging verbosity (default: `INFO`)      |

## License

Internal use only.
