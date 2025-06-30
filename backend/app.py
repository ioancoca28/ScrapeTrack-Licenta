import os
from flask import Flask, request, jsonify
import mysql.connector
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS
import subprocess
from datetime import datetime

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

app.config["JWT_SECRET_KEY"] = "supersecretkey"
jwt = JWTManager(app)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="licenta",
        port=3307
    )


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                       (username, email, password_hash))
        db.commit()

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        access_token = create_access_token(identity=user["id"])
        return jsonify({"message": "User registered successfully", "token": access_token, "username": username}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return jsonify({"message": "Login endpoint is active. Please send a POST request with your credentials."}), 200

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user and bcrypt.check_password_hash(user[2], password):
        access_token = create_access_token(identity=user[0])
        return jsonify({"message": "Login successful", "token": access_token, "username": user[1]}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


python_path = "D:\\Downloads\\Licenta\\.venv\\Scripts\\python.exe"
altex_script = os.path.join("D:\\Downloads\\Licenta\\backend\\scrapers", "scraping_altex.py")
emag_script = os.path.join("D:\\Downloads\\Licenta\\backend\\scrapers", "scraping_emag.py")
flanco_script = os.path.join("D:\\Downloads\\Licenta\\backend\\scrapers", "scraping_flanco.py")

scraping_status = {}

@app.route('/scrape-all', methods=['POST'])
def scrape_all():
    data = request.get_json()
    query = data.get("query", "").strip().lower()

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        scraping_status[query] = {"altex": False, "emag": False, "flanco": False}

        subprocess.Popen([python_path, altex_script, query])
        subprocess.Popen([python_path, emag_script, query])
        subprocess.Popen([python_path, flanco_script, query])

        print(f"Scraping started for {query} on Altex, eMAG, and Flanco.")
        return jsonify({"message": "Scraping started for all sites"}), 200

    except Exception as e:
        scraping_status[query] = {"altex": False, "emag": False, "flanco": False}
        print(f"Error running scraping scripts: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/scrape-status')
def scrape_status():
    query = request.args.get("query", "").strip().lower()
    status = scraping_status.get(query, {})

    all_done = status.get("altex") is True and status.get("emag") is True and status.get("flanco") is True
    return jsonify({"scraping": not all_done})


@app.route('/scrape-done', methods=['POST'])
def scrape_done():
    data = request.get_json()
    query = data.get("query", "").strip().lower()
    source = data.get("source", "").strip().lower()

    if query not in scraping_status:
        scraping_status[query] = {}

    scraping_status[query][source] = True
    print(f"Scraping for {query} from {source} is done.")
    return jsonify({"status": "done"}), 200


@app.route('/insert-products', methods=['POST'])
def insert_products():
    data = request.get_json()
    table_name = data.get("table_name")
    products = data.get("products")

    if not table_name or not products:
        return jsonify({"error": "Missing table name or products"}), 400

    inserted_count = 0
    skipped_count = 0

    try:
        db = get_db_connection()
        cursor = db.cursor()

        for product in products:
            name = product['name']
            link = product['link']
            price = product['price']
            date_added = datetime.now().strftime("%Y-%m-%d")

            cursor.execute(f"""
                SELECT COUNT(*) FROM {table_name} 
                WHERE nume = %s AND link = %s AND pret = %s AND DATE(data_adaugarii) = %s
            """, (name, link, price, date_added))

            result = cursor.fetchone()

            if result[0] == 0:
                cursor.execute(f"""
                    INSERT INTO {table_name} (nume, link, pret, data_adaugarii)
                    VALUES (%s, %s, %s, %s)
                """, (name, link, price, date_added))
                db.commit()
                inserted_count += 1
            else:
                skipped_count += 1

        cursor.close()
        db.close()

        return jsonify({
            "message": f"Data was successfully sent and saved in {table_name}.",
        }), 201

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


@app.route('/get-products', methods=['GET'])
def get_products():
    query = request.args.get("query", "").strip().lower()
    if not query:
        return jsonify({"error": "No query provided"}), 400

    today = datetime.now().strftime("%Y-%m-%d")

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        like_value = f"%{query}%"
        params = [like_value, today, like_value, today, like_value, today]

        query_sql = """
            SELECT 'Altex' AS source, id, nume, link, pret, data_adaugarii FROM produse_altex 
WHERE LOWER(nume) LIKE %s AND DATE(data_adaugarii) = %s
UNION ALL
SELECT 'eMAG' AS source, id, nume, link, pret, data_adaugarii FROM produse_emag 
WHERE LOWER(nume) LIKE %s AND DATE(data_adaugarii) = %s
UNION ALL
SELECT 'Flanco' AS source, id, nume, link, pret, data_adaugarii FROM produse_flanco 
WHERE LOWER(nume) LIKE %s AND DATE(data_adaugarii) = %s

        """

        cursor.execute(query_sql, params)
        produse = cursor.fetchall()

        cursor.close()
        db.close()

        print(f"[INFO] Product display completed for query: {query}")

        return jsonify(produse), 200

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


@app.route('/get-price-history', methods=['GET'])
def get_price_history():
    nume = request.args.get('nume')
    link = request.args.get('link')

    if not nume or not link:
        return jsonify({"error": "Missing product name or link"}), 400

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT pret, data_adaugarii 
            FROM produse_altex 
            WHERE nume = %s AND link = %s
            UNION ALL
            SELECT pret, data_adaugarii 
            FROM produse_emag 
            WHERE nume = %s AND link = %s
            UNION ALL
            SELECT pret, data_adaugarii 
            FROM produse_flanco 
            WHERE nume = %s AND link = %s
            ORDER BY data_adaugarii DESC
        """, (nume, link, nume, link, nume, link))

        price_history = cursor.fetchall()
        cursor.close()
        db.close()

        return jsonify(price_history), 200

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


if __name__ == "__main__":
    app.run(debug=True)
