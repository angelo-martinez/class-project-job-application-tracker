# Job Application Tracker

A full-stack web application for tracking job applications, built with Python/Flask and MySQL.

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip

## Setup

### 1. Install Python Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create the Database

Log in to MySQL and run the schema file:

```bash
mysql -u root -p < schema.sql
```

This creates the `job_tracker` database with all 4 tables..

### 3. Configure Database Credentials

Open `database.py` and update the `DB_CONFIG` dictionary with your MySQL credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'job_tracker'
}
```

### 4. Run the Application

```bash
python app.py
```

Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

## Features

- **Dashboard** — Overview with total counts, application statuses, and recent activity
- **Companies** — Full CRUD (Create, Read, Update, Delete)
- **Jobs** — Full CRUD with company association, salary range, and skill requirements (JSON)
- **Applications** — Full CRUD with status tracking, resume versioning, and interview data (JSON)
- **Contacts** — Full CRUD with company association and contact details
- **Job Match** — Enter your skills and see jobs ranked by match percentage

## Project Structure

```
├── app.py              # Main Flask application (all routes)
├── database.py         # Database connection helper
├── schema.sql          # Database creation script with seed data
├── templates/          # Jinja2 HTML templates
│   ├── base.html       # Base layout with navbar
│   ├── dashboard.html
│   ├── companies.html
│   ├── jobs.html
│   ├── applications.html
│   ├── contacts.html
│   └── job_match.html
├── static/
│   └── style.css       # Custom CSS
├── requirements.txt    # Python dependencies
├── AI_USAGE.md         # GenAI documentation
└── README.md           # This file
```

## Technologies Used

- **Backend:** Python 3, Flask
- **Database:** MySQL
- **Frontend:** HTML, CSS, Bootstrap 5
- **Version Control:** Git / GitHub
