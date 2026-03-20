import psycopg2
try:
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="Akshaya@2006",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database;")
    dbs = cur.fetchall()
    print("Databases found:")
    for db in dbs:
        print(f" - {db[0]}")
    
    if ('pharmacy_db',) not in dbs:
        print("pharmacy_db not found. Creating...")
        cur.execute("CREATE DATABASE pharmacy_db;")
        print("Database created!")
    else:
        print("pharmacy_db already exists.")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
