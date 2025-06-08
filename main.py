from flask import Flask, render_template, request, redirect, url_for
from models import db, Expense
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ✅ Safely create DB tables without decorators
with app.app_context():
    db.create_all()

# Emoji for categories
CATEGORY_EMOJI = {
    'Food': '🍔',
    'Transport': '🚗',
    'Entertainment': '🎮',
    'Bills': '📄',
    'Health': '💊',
    'Other': '🛒'
}

# Keywords for auto-categorization
KEYWORD_CATEGORY = {
    'food': 'Food',
    'restaurant': 'Food',
    'bus': 'Transport',
    'taxi': 'Transport',
    'movie': 'Entertainment',
    'game': 'Entertainment',
    'electricity': 'Bills',
    'water': 'Bills',
    'doctor': 'Health',
    'medicine': 'Health'
}

# Auto-categorize based on description
def categorize(description):
    desc = description.lower()
    for keyword, category in KEYWORD_CATEGORY.items():
        if keyword in desc:
            return category
    return 'Other'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            description = request.form['description']
            date_str = request.form['date']
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            category = categorize(description)
            new_expense = Expense(
                amount=amount,
                description=description,
                category=category,
                date=date_obj
            )
            db.session.add(new_expense)
            db.session.commit()
            return redirect(url_for('index'))

        except Exception as e:
            return f"Error occurred: {e}"

    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('index.html', expenses=expenses, category_emoji=CATEGORY_EMOJI)

@app.route('/dashboard')
def dashboard():
    expenses = Expense.query.all()
    monthly_summary = defaultdict(float)

    for expense in expenses:
        month = expense.date.strftime('%Y-%m')
        key = f"{month} - {expense.category}"
        monthly_summary[key] += expense.amount

    summary_list = []
    for key, amount in monthly_summary.items():
        month, category = key.split(' - ')
        summary_list.append({
            'month': month,
            'category': category,
            'amount': round(amount, 2),
            'emoji': CATEGORY_EMOJI.get(category, '')
        })

    return render_template('dashboard.html', summary=summary_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
