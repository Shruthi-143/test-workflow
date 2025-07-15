from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Fetch DB credentials from env
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME", "postgres")

# Dummy fallback data
DUMMY_USERS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "abc", "email": "abc@example.com"},
    {"id": 4, "name": "xyz", "email": "xyz@example.com"}
]

def get_db_conn():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME,
        sslmode="require"
    )

@app.route("/")
def root():
    return "Welcome to backend!", 200

@app.route("/health")
def health():
    return "OK", 200

@app.route("/users")
def users():
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM users;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            return jsonify(DUMMY_USERS)
        return jsonify([
            {"id": row[0], "name": row[1], "email": row[2]}
            for row in rows
        ])
    except Exception as e:
        # Fallback to dummy data if DB fails
        return jsonify(DUMMY_USERS + [{"source": "fallback", "error": str(e)}]), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

