# Knack Customer Validation System

Django REST API that validates customer data and syncs with Knack. Valid records → Records table, Invalid → Issues table. Auto-assigns failed records to team members with email notifications.

## Installation

```bash
git clone https://github.com/yourusername/knack-validation.git
cd knack-validation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Setup

1. Create `.env` file:
```
KNACK_APP_ID=your_app_id
KNACK_API_KEY=your_api_key
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

2. Update `config.py` with your Knack object/field IDs
3. Run migrations: `python manage.py migrate`
4. Start: `python manage.py runserver`

## API Endpoints

- `POST /api/download/` - Download customers from Knack
- `POST /api/upload-validate/` - Validate and upload to Knack

## Validation Rules

✓ Customer ID format: `C123456`  
✓ Email: Valid format  
✓ Phone: 10-15 digits  
✓ Age: 18-100  
✓ Signup Date: YYYY-MM-DD (not future)  

## Tech Stack

Django, DRF, Knack API, PostgreSQL, SMTP

## Author

Ahsan Afzal - Backend Developer
Github (https://github.com/ahsnafzal)
Linkedin (https://www.linkedin.com/in/ahsanafzal1/)
