import os
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
    try:
        url = os.getenv("DATABASE_URL")
        print("DATABASE_URL:", url)

        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)

        conn = psycopg2.connect(url, sslmode='require')
        print("✅ DB Connected")
        return conn

    except Exception as e:
        print("❌ DB ERROR:", e)
        raise

    
    

# ----------------------------
# Home Page
# ----------------------------
@app.route("/")
def home():
    return render_template("home.html")

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
    q = request.args.get("q", "")
    conn = get_connection()
    cur = conn.cursor()
    
    if q:
        cur.execute("SELECT * FROM medicines WHERE name ILIKE %s OR category ILIKE %s;", (f"%{q}%", f"%{q}%"))
    else:
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
    q = request.args.get("q", "")
    conn = get_connection()
    cur = conn.cursor()

    if q:
        cur.execute("""
            SELECT m.id, m.name, s.quantity, s.last_updated
            FROM stock s
            JOIN medicines m ON s.medicine_id = m.id
            WHERE m.name ILIKE %s OR m.category ILIKE %s;
        """, (f"%{q}%", f"%{q}%"))
    else:
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
# Dashboard Chart Data (JSON)
# ----------------------------
from flask import jsonify

@app.route("/api/dashboard-chart")
def api_dashboard_chart():
    conn = get_connection()

    query = """
        SELECT m.name, s.quantity
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
    """

    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        return jsonify({"labels": [], "data": []})

    summary = df.groupby("name")["quantity"].sum()
    return jsonify({
        "labels": summary.index.tolist(),
        "data": [int(x) for x in summary.values]
    })

# ----------------------------
# Inventory Chart Data (JSON)
# ----------------------------
@app.route("/api/inventory-chart")
def api_inventory_chart():
    conn = get_connection()
    df = pd.read_sql("SELECT quantity FROM stock", conn)
    conn.close()

    if df.empty:
        return jsonify({"labels": [], "data": [], "colors": []})

    healthy = len(df[df['quantity'] > 50])
    warning = len(df[(df['quantity'] > 20) & (df['quantity'] <= 50)])
    critical = len(df[df['quantity'] <= 20])

    return jsonify({
        "labels": ['Healthy', 'Low/Warning', 'Critical'],
        "data": [healthy, warning, critical],
        "colors": ['#10b981', '#f59e0b', '#ef4444']
    })

# ----------------------------
# Export Endpoints
# ----------------------------
@app.route("/export-stock")
def export_stock():
    conn = get_connection()
    query = """
        SELECT m.name as "Medicine", s.quantity as "Quantity", s.last_updated as "Last Updated"
        FROM stock s
        JOIN medicines m ON s.medicine_id = m.id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    csv_data = df.to_csv(index=False).encode('utf-8')
    return send_file(io.BytesIO(csv_data), mimetype="text/csv", as_attachment=True, download_name="stock_report.csv")

@app.route("/export-report")
def export_report():
    conn = get_connection()
    query = """
        SELECT m.name as "Medicine", s.quantity as "Quantity Sold", s.sale_date as "Sale Date"
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    csv_data = df.to_csv(index=False).encode('utf-8')
    return send_file(io.BytesIO(csv_data), mimetype="text/csv", as_attachment=True, download_name="sales_report.csv")

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