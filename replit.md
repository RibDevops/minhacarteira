# Minha Carteira Digital

## Overview
A personal finance management application built with Django 5.2. It helps users track expenses and income through a calendar-based interface with monthly summaries.

## Features
- Calendar view of daily transactions
- Transaction categories and types management
- Monthly balance tracking
- Financial goals (metas)
- User authentication
- Responsive design with dark mode support

## Technology Stack
- Python 3.12
- Django 5.2.1
- SQLite database
- Bootstrap CSS
- jQuery

## Project Structure
```
├── cal/              # Main application
│   ├── views/        # View controllers
│   ├── models.py     # Database models
│   ├── forms.py      # Form definitions
│   ├── urls.py       # URL routing
│   └── templates/    # App-specific templates
├── core/             # Django project settings
│   ├── settings.py   # Configuration
│   └── urls.py       # Root URL configuration
├── templates/        # Global templates
├── static/           # Static assets (CSS, JS, images)
└── manage.py         # Django management script
```

## Environment Variables
- `SECRET_KEY`: Django secret key for security
- `FERNET_SECRET_KEY`: Encryption key for encrypted fields
- `DEBUG`: Set to True for development
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Running the Application
The application runs on port 5000 using Django's development server:
```bash
python manage.py runserver 0.0.0.0:5000
```

## Database
Uses SQLite (db.sqlite3) for data storage. Run migrations with:
```bash
python manage.py migrate
```

## Recent Changes
- 2026-01-04: Initial Replit setup
  - Configured Python 3.12 environment
  - Fixed locale settings for Replit compatibility
  - Set ALLOWED_HOSTS and CSRF settings for Replit proxy
  - Updated static files paths
