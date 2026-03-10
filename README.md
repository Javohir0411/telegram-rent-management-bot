# Telegram Rent Management Bot

A production-ready Telegram bot for managing construction equipment rentals.
This system allows tracking renters, rental periods, payments, and automatically notifying about expired rentals.

Designed for real business usage with scalable architecture.

---

## Main Features

• Manage renters and rental products
• Track rental start and end dates
• Payment status tracking
• Automatic daily check for expired rentals
• Multi-tenant architecture (each business works independently)
• Admin command system
• Clean modular architecture

---

## Tech Stack

Python
Aiogram
PostgreSQL
SQLAlchemy (async)
AsyncPG
Railway (deployment)

---

## Project Architecture

```
telegram-rent-management-bot
│
├── routers        # Telegram command handlers
├── db             # Database models and CRUD operations
├── database       # Database session & connection
├── keyboards      # Telegram keyboards
├── bot_strings    # Bot messages and texts
├── utils          # Helper utilities
├── states.py      # FSM states
├── main.py        # Application entry point
└── requirements.txt
```

The project follows a modular architecture separating:

• routing
• database logic
• business logic
• utilities

which keeps the code maintainable and scalable.

---

## Installation

Clone repository

```
git clone https://github.com/YOUR_USERNAME/telegram-rent-management-bot.git
cd telegram-rent-management-bot
```

Install dependencies

```
pip install -r requirements.txt
```

Create `.env` file

```
BOT_TOKEN=your_bot_token
DATABASE_URL=your_database_url
ALLOWED_TG_IDS=admin_ids
```

Run bot

```
python main.py
```

---

## Deployment

The bot is deployed on Railway.

Deployment steps:

1. Connect GitHub repository
2. Add environment variables
3. Set start command

```
python main.py
```

---

## Example Use Cases

Construction companies renting equipment
Small businesses tracking rented inventory
Rental management automation

---

## Author

Javohir
Python Backend Developer
