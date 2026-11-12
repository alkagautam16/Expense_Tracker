import csv
import io
import os
from datetime import date

from flask import (Flask, Response, flash, jsonify, redirect,
                   render_template, request, url_for)

import database as db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")  # set a real one online

CATEGORIES = ["Food", "Travel", "Shopping", "Education", "Bills", "Entertainment", "Other"]
db.init_db()


def get_stats():
    month = date.today().strftime("%Y-%m")
    t = db.query("SELECT COALESCE(SUM(amount),0) AS total, COUNT(*) AS n FROM expenses", one=True)
    m = db.query("SELECT COALESCE(SUM(amount),0) AS t FROM expenses WHERE substr(date,1,7)=?",
                 (month,), one=True)["t"]
    b = db.query("SELECT amount FROM budget WHERE month=?", (month,), one=True)
    budget = b["amount"] if b else 0
    return {"total": t["total"], "count": t["n"], "month_total": m, "budget": budget,
            "remaining": budget - m, "percent": (m / budget * 100) if budget else 0,
            "month_name": date.today().strftime("%B %Y")}


@app.context_processor
def inject_stats():  # makes `stats` and `categories` available in every template
    return {"stats": get_stats(), "categories": CATEGORIES}


def read_form():
    """Validate the expense form. Returns (data, error)."""
    try:
        amount = float(request.form.get("amount", ""))
    except ValueError:
        return None, "Please enter a valid amount."
    category = request.form.get("category")
    day = request.form.get("date")
    if amount <= 0:
        return None, "Amount must be greater than zero."
    if category not in CATEGORIES or not day:
        return None, "Please choose a category and a date."
    return (amount, category, day, request.form.get("description", "").strip()), None


@app.route("/")
def home():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    recent = db.query("SELECT * FROM expenses ORDER BY date DESC, id DESC LIMIT 5")
    return render_template("dashboard.html", recent=recent, page="dashboard")


@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        data, error = read_form()
        if error:
            flash(error, "danger")
        else:
            db.execute("INSERT INTO expenses (amount, category, date, description) VALUES (?,?,?,?)", data)
            flash("Expense saved!", "success")
            return redirect(url_for("expenses"))
    return render_template("add_expense.html", expense=None, today=date.today().isoformat(), page="add")


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    expense = db.query("SELECT * FROM expenses WHERE id=?", (expense_id,), one=True)
    if expense is None:
        flash("Expense not found.", "danger")
        return redirect(url_for("expenses"))
    if request.method == "POST":
        data, error = read_form()
        if error:
            flash(error, "danger")
        else:
            db.execute("UPDATE expenses SET amount=?, category=?, date=?, description=? WHERE id=?",
                       data + (expense_id,))
            flash("Expense updated!", "success")
            return redirect(url_for("expenses"))
    return render_template("add_expense.html", expense=expense, today=date.today().isoformat(), page="expenses")


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    db.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    flash("Expense deleted.", "success")
    return redirect(url_for("expenses"))


@app.route("/expenses")
def expenses():
    q = request.args.get("q", "").strip()
    cat = request.args.get("category", "")
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    sql, args = "SELECT * FROM expenses WHERE 1=1", []
    if q:
        sql += " AND (description LIKE ? OR category LIKE ?)"
        args += [f"%{q}%", f"%{q}%"]
    if cat:
        sql += " AND category=?"
        args.append(cat)
    if start:
        sql += " AND date>=?"
        args.append(start)
    if end:
        sql += " AND date<=?"
        args.append(end)
    rows = db.query(sql + " ORDER BY date DESC, id DESC", args)
    return render_template("expenses.html", rows=rows, q=q, cat=cat, start=start, end=end,
                           shown_total=sum(r["amount"] for r in rows), page="expenses")


@app.route("/budget", methods=["GET", "POST"])
def budget():
    month = date.today().strftime("%Y-%m")
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", ""))
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Enter a budget greater than zero.", "danger")
        else:
            db.execute("INSERT INTO budget (month, amount) VALUES (?,?) "
                       "ON CONFLICT(month) DO UPDATE SET amount=excluded.amount", (month, amount))
            flash("Budget saved!", "success")
            return redirect(url_for("budget"))
    return render_template("budget.html", page="budget")


@app.route("/reports")
def reports():
    rows = db.query("SELECT substr(date,1,7) AS month, SUM(amount) AS total, COUNT(*) AS n "
                    "FROM expenses GROUP BY month ORDER BY month DESC")
    return render_template("reports.html", rows=rows, page="reports")


@app.route("/export.csv")
def export_csv():
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["ID", "Date", "Category", "Amount", "Description"])
    for r in db.query("SELECT * FROM expenses ORDER BY date DESC"):
        w.writerow([r["id"], r["date"], r["category"], r["amount"], r["description"]])
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=expenses.csv"})


@app.route("/api/chart-data")
def chart_data():
    cats = db.query("SELECT category, SUM(amount) AS t FROM expenses GROUP BY category ORDER BY t DESC")
    months = db.query("SELECT substr(date,1,7) AS m, SUM(amount) AS t FROM expenses "
                      "GROUP BY m ORDER BY m DESC LIMIT 12")[::-1]
    return jsonify(categories={"labels": [r["category"] for r in cats], "values": [r["t"] for r in cats]},
                   months={"labels": [r["m"] for r in months], "values": [r["t"] for r in months]})


if __name__ == "__main__":
    app.run(debug=True)
