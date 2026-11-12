# 💜 SpendWise – Personal Expense Tracker

A responsive full-stack web app to track daily expenses, manage monthly budgets, visualise spending and export reports.

## Features
- Dashboard: total, monthly spend, transaction count, remaining budget, recent transactions
- Add / edit / delete expenses (Food, Travel, Shopping, Education, Bills, Entertainment, Other)
- Search, category filter and date-range filter
- Monthly budget with warnings at 80% and 100%
- Chart.js doughnut (by category) and bar (by month) charts
- Monthly summary report and CSV download
- Mobile-friendly sidebar layout

## Tech Stack
HTML, CSS, JavaScript, Python, Flask, SQLite, Chart.js

## Run Locally
```bash
git clone https://github.com/<your-username>/personal-expense-tracker.git
cd personal-expense-tracker
python -m venv venv
venv\Scripts\activate        # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. The database (`expenses.db`) is created automatically.

## Screenshots
Add images to a `screenshots/` folder and link them here:
![Dashboard](screenshots/dashboard.png)

## Deployment
Deploy on Render with start command `gunicorn app:app`. Set the `SECRET_KEY` environment variable. For persistent SQLite data, attach a disk and set `DATABASE_PATH` (e.g. `/var/data/expenses.db`).

## Project Structure
`app.py` routes · `database.py` SQLite helpers · `templates/` pages · `static/` CSS and JS
