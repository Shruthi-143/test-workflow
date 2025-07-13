from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

# Environment variables for DB connection
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME", "postgres")

def get_db_conn():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )

# Run once on first HTTP request (to init DB and insert demo data)
@app.before_first_request
def setup_db():
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100)
            );
        """)
        cur.execute("SELECT COUNT(*) FROM users;")
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO users (name, email)
                VALUES
                ('Alice', 'alice@example.com'),
                ('Bob', 'bob@example.com');
            """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Database setup failed:", e)

# Health check endpoint
@app.route("/health")
def health():
    return "OK", 200

# Users API
@app.route("/users")
def users():
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([
            {"id": row[0], "name": row[1], "email": row[2]}
            for row in rows
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

