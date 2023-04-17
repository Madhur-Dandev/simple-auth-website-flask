# packages
# 1. werkzeug
# 2. sqlalchemy
# 3. pymysql
# 4. PyJWT

from jwt import encode, decode
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request as req, flash, session, redirect, url_for
from datetime import timedelta
from sqlalchemy import create_engine, text, exc

app = Flask(__name__)
app.config["SECRET_KEY"] = "jaishreeram"
app.config["DEBUG"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=5)

db = create_engine("mysql+pymysql://root:madhur531@0.0.0.0/practice?charset=utf8mb4")

def execute_query(query, action):
    try:
        with db.connect() as conn:
            if action == "select":
                result = conn.execute(text(query)).mappings().first()
                if result:
                    result = dict(result)
                    result["success"] = True
                    result["found"] = True
                else:
                    result = {"success": True, "found": False}
                return result
            
            conn.execute(text(query))
            return {"success": True}
    except (Exception, exc.SQLAlchemyError) as e:
        print(e)
        return {"success": False}

@app.route("/login", methods=["GET", "POST"])
def login():
    if req.method == "POST":
        email = req.form.get("email")
        password = req.form.get("password")

        if email and password:
            result = execute_query(f"SELECT user_password AS pass FROM nis_users WHERE user_email = '{email}'", "select")

            if result.get("success"):
                if result.get("found"):
                    if check_password_hash(result.get("pass"), password):
                        flash("Logged In", category="success")
                        return render_template("login.html")
                    else:
                        flash("Password is incorrent", category="danger")
                else:
                    flash("User not found!", category="danger")
            else:
                flash("Error", category="danger")
        else: 
            flash("All fields are required", category="warning")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if req.method == "POST":
        name = req.form.get("name")
        email = req.form.get("email")
        password = req.form.get("password")

        if name and email and password:
            result = execute_query(f"SELECT COUNT(*) AS user FROM nis_users WHERE user_email = '{email}'", "select")

            if result.get("success"):
                if result.get("found"):
                    if result.get("user") == 0:
                        insert_result = execute_query(f"INSERT INTO nis_users (user_name, user_email, user_password) VALUES ('{name}', '{email}', '{generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)}')", "insert")
                        print(insert_result)
                        if insert_result.get("success"):
                            return redirect(url_for("login"), 201)               
                        else:
                            flash("Can't process your request! Please try again after sometime.", category="danger")
                    else:
                        flash("User already exists.", category="danger")
                else:
                    flash("User not found!", category="danger")
            else:
                flash("Error", category="danger")
        else: 
            flash("All fields are required", category="warning")
    
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0")