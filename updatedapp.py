# updatedapp.py
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_file
from flask_cors import CORS
from flask_session import Session
from pymongo import MongoClient
from bson import ObjectId, Binary
from datetime import datetime
import bcrypt
import os
from functools import wraps
import csv
import io

# ----- Config -----
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET", "prod-secret-key")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
Session(app)
CORS(app)

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://amushun1992_db_user:PwQge1UbU41Z3Xjs@tm-users.vxuhp3p.mongodb.net/citizen_portal?retryWrites=true&w=majority"
)

# ----- MongoDB -----
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]

services_col = db["services"]
categories_col = db["categories"]
officers_col = db["officers"]
ads_col = db["ads"]
admins_col = db["admins"]
eng_col = db["engagements"]

# ----- Helpers -----
def to_jsonable(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, Binary):
        return bytes(obj)
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(v) for v in obj]
    return obj

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            accept = request.headers.get("Accept", "")
            if "application/json" in accept or request.path.startswith("/api/"):
                return jsonify({"error": "unauthorized"}), 401
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

# ----- Admin creation -----
def create_default_admin():
    admin = admins_col.find_one({"username": "admin"})
    if admin:
        stored = admin.get("password")
        if isinstance(stored, str):
            admins_col.delete_one({"_id": admin["_id"]})
        else:
            return
    pwd = os.environ.get("ADMIN_PWD", "admin123")
    hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
    admins_col.insert_one({"username": "admin", "password": hashed})
    print("Default admin created: username='admin', password='admin123'")

# ----- Routes -----
@app.route("/")
def home():
    try:
        return render_template("main.html")
    except:
        return "Citizen Portal API Running"

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        admin = admins_col.find_one({"username": username})
        if admin:
            stored_hash = admin.get("password")
            if isinstance(stored_hash, Binary):
                stored_hash = bytes(stored_hash)
            if isinstance(stored_hash, str):
                return render_template("admin_login.html", error="Invalid credentials")
            if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                session["admin_logged_in"] = True
                return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="Invalid credentials")
    return render_template("admin_login.html")

@app.route("/admin")
@admin_required
def admin_dashboard():
    try:
        return render_template("newadmin.html")
    except:
        return "Admin Dashboard"

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

# ----- Public APIs -----
@app.route("/api/services", methods=["GET"])
def api_services():
    docs = list(services_col.find({}, {"_id": 0}))
    return jsonify(to_jsonable(docs))

@app.route("/api/service/<service_id>", methods=["GET"])
def api_service(service_id):
    doc = services_col.find_one({"id": service_id}, {"_id": 0})
    return jsonify(to_jsonable(doc or {}))

@app.route("/api/categories", methods=["GET"])
def api_categories():
    docs = list(categories_col.find({}, {"_id": 0}))
    return jsonify(to_jsonable(docs))

# ----- Profile API -----
@app.route("/api/profile/step", methods=["POST"])
def profile_step():
    data = request.get_json() or {}
    step = data.get("step")
    profile_id = data.get("profile_id")
    profile_data = data.get("data") or {}

    if step == "basic":
        email = profile_data.get("email") or data.get("email")
        if not email:
            return jsonify({"error": "Email required"}), 400
        res = db.profiles.insert_one({**profile_data, "created_at": datetime.utcnow()})
        return jsonify({"status": "ok", "profile_id": str(res.inserted_id)})
    elif profile_id:
        db.profiles.update_one({"_id": ObjectId(profile_id)}, {"$set": profile_data})
        return jsonify({"status": "ok"})
    return jsonify({"error": "invalid request"}), 400

# ----- AI search -----
@app.route("/api/ai/search", methods=["POST"])
def api_ai_search():
    try:
        payload = request.get_json() or {}
        query_text = payload.get("query", "").strip()
        if not query_text:
            return jsonify({"error": "empty query"}), 400

        results = []
        for service in services_col.find({}, {"_id": 0}):
            service_name = service.get("name", {}).get("en", "")
            for sub in service.get("subservices", []):
                sub_name = sub.get("name", {}).get("en", "")
                for q in sub.get("questions", []):
                    question_text = q.get("q", {}).get("en", "")
                    answer_text = q.get("answer", {}).get("en", "")
                    if query_text.lower() in (question_text + sub_name + service_name).lower():
                        results.append({
                            "service": service_name,
                            "subservice": sub_name,
                            "question": question_text,
                            "answer": answer_text
                        })
        return jsonify(results)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ----- Engagement logging -----
# ----- User Engagements API for Recommendations -----
@app.route("/api/engagement", methods=["GET"])
def api_get_engagements():
    """
    Returns all engagement events. Optionally, filter by user_id via query param.
    """
    user_id = request.args.get("user_id")
    query = {}
    if user_id:
        query["user_id"] = user_id

    try:
        docs = list(eng_col.find(query, {"_id": 0}))  # exclude MongoDB _id
        return jsonify(to_jsonable(docs))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----- GDPR / Data deletion -----
@app.route("/api/user/delete", methods=["POST"])
def delete_user_data():
    payload = request.get_json() or {}
    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    eng_col.delete_many({"user_id": user_id})
    return jsonify({"status": "deleted"})

# ----- Ads API -----
@app.route("/api/ads", methods=["GET"])
def api_ads():
    docs = list(ads_col.find({}, {"_id": 0}))
    return jsonify(to_jsonable(docs))

# ----- Admin CRUD endpoints -----
@app.route("/api/admin/categories", methods=["POST"])
@admin_required
def admin_add_category():
    try:
        data = request.get_json() or {}
        if not data.get("id") or not data.get("name"):
            return jsonify({"error": "Missing required fields"}), 400
        if categories_col.find_one({"id": data["id"]}):
            return jsonify({"error": "Category id already exists"}), 400
        res = categories_col.insert_one(data)
        return jsonify({"status": "ok", "inserted_id": str(res.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----- EXPORT ENGAGEMENT CSV -----
@app.route("/api/admin/export_engagement_csv", methods=["GET"])
@admin_required
def export_engagement_csv():
    try:
        cursor = eng_col.find()
        output = io.StringIO()
        writer = csv.writer(output)
        # header
        writer.writerow(["user_id", "age", "job", "desires", "question_clicked", "service", "ad", "source", "timestamp"])
        for e in cursor:
            writer.writerow([
                e.get("user_id"),
                e.get("age"),
                e.get("job"),
                ",".join(e.get("desires") or []),
                e.get("question_clicked"),
                e.get("service"),
                e.get("ad"),
                e.get("source"),
                e.get("timestamp")
            ])
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode("utf-8")),
                         mimetype="text/csv",
                         as_attachment=True,
                         download_name="engagements.csv")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----- Startup -----
if __name__ == "__main__":
    create_default_admin()
    app.run(debug=True, host="127.0.0.1", port=5000)
