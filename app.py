from flask import Flask, render_template, request, redirect, send_file
import psycopg2
from datetime import date
import matplotlib.pyplot as plt
import matplotlib
import io
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

matplotlib.use("Agg")

app = Flask(__name__)

# ----------------------------
# Database Connection
# ----------------------------
def get_connection():
    return psycopg2.connect(
        dbname="pharmacy_db",
        user="postgres",
        password="Akshaya@2006",  # Change if needed
        host="localhost",
        port="5432"
    )

# ----------------------------
# Home Page
# ----------------------------
@app.route("/")
def home():
    return """
      <html>
    <head>
        <title>Pharmacy Warehouse</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #fdfbfb, #ebedee);
                text-align: center;
            }

            h1 {
                margin-top: 40px;
                color: #2c3e50;
            }

            .container {
                margin-top: 50px;
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
            }

            .card {
                width: 220px;
                padding: 20px;
                border-radius: 12px;
                text-decoration: none;
                color: #2c3e50;
                font-weight: bold;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
                transition: 0.2s;
            }

            .card:hover {
                transform: scale(1.05);
            }

            .c1 { background: #e3f2fd; }
            .c2 { background: #e8f5e9; }
            .c3 { background: #fff3e0; }
            .c4 { background: #fce4ec; }
            .c5 { background: #ede7f6; }
            .c6 { background: #f1f8e9; }
            .c7 { background: #e0f7fa; }

        </style>
    </head>
    <body>

        <h1>💊 Pharmacy Warehouse Management System</h1>

        <div class="container">
            <a href="/medicines" class="card c1">📋 View Medicines</a>
            <a href="/add-medicine" class="card c2">➕ Add Medicine</a>
            <a href="/stock" class="card c3">📦 View Stock</a>
            <a href="/add-stock" class="card c4">📥 Add Stock</a>
            <a href="/add-sale" class="card c5">🛒 Add Sale</a>
            <a href="/dashboard" class="card c6">📊 Dashboard</a>
            <a href="/test-db" class="card c7">🔍 Test DB Connection</a>
        </div>

    </body>
    </html>
    

    
    """

# ----------------------------
# Test Database
# ----------------------------
@app.route("/test-db")
def test_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    result = cur.fetchone()
    conn.close()
    return f"Database Connected Successfully! Time: {result}"

# ----------------------------
# Medicines
# ----------------------------
@app.route("/medicines")
def medicines():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM medicines;")
    medicines = cur.fetchall()
    conn.close()
    return render_template("medicines.html", medicines=medicines)

# ----------------------------
# Add Medicine
# ----------------------------
@app.route("/add-medicine", methods=["GET", "POST"])
def add_medicine():
    if request.method == "POST":
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO medicines (name, category, expiry_date, price)
            VALUES (%s, %s, %s, %s)
        """, (
            request.form["name"],
            request.form["category"],
            request.form["expiry_date"],
            request.form["price"]
        ))

        conn.commit()
        conn.close()
        return redirect("/medicines")

    return render_template("add_medicine.html")

# ----------------------------
# Stock View
# ----------------------------
@app.route("/stock")
def stock():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT m.id, m.name, s.quantity, s.last_updated
        FROM stock s
        JOIN medicines m ON s.medicine_id = m.id;
    """)

    stock_data = cur.fetchall()
    conn.close()

    return render_template("stock.html", stock_data=stock_data)

# ----------------------------
# Add Stock
# ----------------------------
@app.route("/add-stock", methods=["GET", "POST"])
def add_stock():
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        cur.execute("""
            INSERT INTO stock (medicine_id, quantity, last_updated)
            VALUES (%s, %s, %s)
        """, (
            request.form["medicine_id"],
            request.form["quantity"],
            date.today()
        ))

        conn.commit()
        conn.close()
        return redirect("/stock")

    cur.execute("SELECT id, name FROM medicines;")
    medicines = cur.fetchall()
    conn.close()

    return render_template("add_stock.html", medicines=medicines)

# ----------------------------
# Add Sale (Safe Stock Reduction)
# ----------------------------
@app.route("/add-sale", methods=["GET", "POST"])
def add_sale():
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        medicine_id = request.form["medicine_id"]
        quantity = int(request.form["quantity"])

        # Check stock
        cur.execute("SELECT quantity FROM stock WHERE medicine_id=%s", (medicine_id,))
        row = cur.fetchone()

        if not row or row[0] < quantity:
            conn.close()
            return "❌ Not enough stock available"

        # Insert sale
        cur.execute("""
            INSERT INTO sales (medicine_id, quantity, sale_date)
            VALUES (%s, %s, CURRENT_DATE)
        """, (medicine_id, quantity))

        # Reduce stock
        cur.execute("""
            UPDATE stock
            SET quantity = quantity - %s,
                last_updated = CURRENT_DATE
            WHERE medicine_id = %s
        """, (quantity, medicine_id))

        conn.commit()
        conn.close()

        return redirect("/stock")

    cur.execute("SELECT id, name FROM medicines;")
    medicines = cur.fetchall()
    conn.close()

    return render_template("add_sale.html", medicines=medicines)

# ----------------------------
# Dashboard
# ----------------------------
@app.route("/dashboard")
def dashboard():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM medicines;")
    total_medicines = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM stock WHERE quantity < 20;")
    low_stock = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM medicines
        WHERE expiry_date <= CURRENT_DATE + INTERVAL '30 days';
    """)
    expiring_soon = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(quantity),0) FROM sales;")
    total_sales = cur.fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           total_medicines=total_medicines,
                           low_stock=low_stock,
                           expiring_soon=expiring_soon,
                           total_sales=total_sales)

# ----------------------------
# Dashboard Chart (Safe)
# ----------------------------
@app.route("/dashboard-chart")
def dashboard_chart():
    conn = get_connection()

    query = """
        SELECT m.name, s.quantity
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
    """

    df = pd.read_sql(query, conn)
    conn.close()

    plt.figure(figsize=(8,5))

    if df.empty:
        plt.text(0.5, 0.5, "No Sales Data Available",
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=14)
        plt.xticks([])
        plt.yticks([])
    else:
        summary = df.groupby("name")["quantity"].sum()
        summary.plot(kind="bar")
        plt.xlabel("Medicine")
        plt.ylabel("Total Sold")

    plt.title("Sales by Medicine")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    return send_file(img, mimetype="image/png")

# ----------------------------
# ML Prediction
# ----------------------------
@app.route("/predict/<int:medicine_id>")
def predict_stock(medicine_id):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT quantity FROM stock WHERE medicine_id=%s", (medicine_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return "No stock data"

    current_stock = row[0]

    X = np.array([[10], [20], [50], [100]])
    y = np.array([1, 1, 0, 0])

    model = LogisticRegression()
    model.fit(X, y)

    prediction = model.predict([[current_stock]])[0]

    result = "⚠ High Stock-Out Risk" if prediction == 1 else "✅ Stock Stable"

    return f"Medicine ID {medicine_id}: {result}"
@app.route("/delete-medicine/<int:medicine_id>")
def delete_medicine(medicine_id):
    conn = get_connection()
    cur = conn.cursor()

    # Delete related stock & sales first (to avoid foreign key error)
    cur.execute("DELETE FROM sales WHERE medicine_id=%s", (medicine_id,))
    cur.execute("DELETE FROM stock WHERE medicine_id=%s", (medicine_id,))
    cur.execute("DELETE FROM medicines WHERE id=%s", (medicine_id,))

    conn.commit()
    conn.close()

    return redirect("/medicines")

@app.route("/delete-stock/<int:medicine_id>")
def delete_stock(medicine_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM stock WHERE medicine_id=%s", (medicine_id,))

    conn.commit()
    conn.close()

    return redirect("/stock")

@app.route("/delete-sale/<int:sale_id>")
def delete_sale(sale_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM sales WHERE id=%s", (sale_id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)