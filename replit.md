# Minha Carteira Digital

## Overview
A personal finance management application built with Django 5.2. It helps users track expenses and income through a calendar-based interface with monthly summaries. Features responsive mobile-first design for managing transactions, credit cards, categories, and financial goals.

## Features
- Calendar view of daily transactions with responsive card-based layout on mobile
- Transaction categories and types management
- Credit card management with automatic installment calculations
- Monthly balance tracking with visual charts (Pie & Doughnut)
- Financial goals (metas) per category
- User authentication with admin dashboard
- Fully responsive design (mobile-first approach)
- Dark mode support with Bootstrap 5

## Technology Stack
- **Backend**: Python 3.11, Django 5.2.1
- **Database**: SQLite (development)
- **Frontend**: Bootstrap 5, Chart.js, Bootstrap Icons
- **Security**: django-encrypted-model-fields for sensitive data

## Project Structure
```
├── cal/                    # Main finance app
│   ├── views/             # View modules for different features
│   │   ├── views_transacao.py    # Transaction management
│   │   ├── views_cal.py          # Calendar views
│   │   ├── views_categoria.py    # Category management
│   │   ├── views_meta.py         # Financial goals
│   │   ├── views_dashboard.py    # Dashboard
│   │   ├── views_tipo.py         # Transaction types
│   │   ├── views_user.py         # User management
│   │   └── views_login.py        # Authentication
│   ├── models.py          # Database models
│   ├── forms.py           # Form definitions
│   ├── urls.py            # URL routing
│   ├── signals.py         # Auto-category creation on signup
│   ├── context_processors.py  # Global template context
│   ├── templatetags/      # Custom template filters
│   └── migrations/        # Database migrations
├── core/                   # Django project settings
│   ├── settings.py        # Main configuration
│   ├── urls.py            # Root URL routing
│   └── wsgi.py            # WSGI application
├── templates/             # Global + app templates
│   ├── base.html          # Base template with navbar
│   ├── cal/              # Transaction, calendar, and dashboard templates
│   └── usuarios/         # User management templates
├── static/                # CSS, JS, Images (Bootstrap + app styles)
├── db.sqlite3            # SQLite database
├── manage.py             # Django CLI
└── requirements.txt      # Python dependencies
```

## Environment Variables
- `SECRET_KEY`: Django secret key for security
- `FERNET_SECRET_KEY`: Encryption key for encrypted fields (django-encrypted-model-fields)
- `DEBUG`: Set to True for development
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts (set to '*' for Replit)

## Running the Application
Development server runs on port 5000:
```bash
python manage.py runserver 0.0.0.0:5000
```

## Database
Uses SQLite for development. Apply migrations:
```bash
python manage.py migrate
```

## Recent Changes (Jan 14, 2026)
- Simplified credit card billing logic: purchases always fall into next month
- Optimized transaction display for mobile (responsive card layout)
- Enhanced user management page with mobile-friendly interface
- Code cleanup: removed debug_toolbar, test files, static/admin, duplicates in requirements.txt
- Improved responsiveness: desktop table view + mobile card view for all list pages

## Key Business Rules
1. **Credit Card Billing**: Purchases in month X always bill to month X+1 (no closing day logic)
2. **Categories**: Auto-created on user signup (Alimentação, Transporte, Moradia, etc.)
3. **Encrypted Fields**: Transaction titles use Fernet encryption for security
4. **Installments**: Multiple installments automatically calculated per month

## Performance Notes
- Static files served from /static/
- Bootstrap 5 loaded from CDN (bootstrap.min.js, bootstrap.min.css)
- Chart.js loaded from CDN for visualizations
- Icons from Bootstrap Icons (CDN)
- jQuery available if needed (Bootstrap compatible)
