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
import pathlib

# ------------- FAISS + Embeddings -------------
try:
    import faiss
    FAISS_AVAILABLE = True
except Exception:
    FAISS_AVAILABLE = False

from sentence_transformers import SentenceTransformer

EMBED_MODEL = None
INDEX_PATH = pathlib.Path("./data/faiss.index")
META_PATH = pathlib.Path("./data/faiss_meta.json")
VECTOR_DIM = 384  # all-MiniLM-L6-v2


def get_embedding_model():
    global EMBED_MODEL
    if EMBED_MODEL is None:
        EMBED_MODEL = SentenceTransformer(
            os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        )
    return EMBED_MODEL


# ------------- Flask Config -------------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET", "prod-secret-key")
app.config["SESSION_TYPE"] = "filesystem"
# In development you may want cookies to be non-secure (HTTP). Set via env in production.
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
Session(app)
# allow credentials so session cookie works with CORS-enabled frontends
CORS(app, supports_credentials=True)

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://amushun1992_db_user:PwQge1UbU41Z3Xjs@tm-users.vxuhp3p.mongodb.net/citizen_portal?retryWrites=true&w=majority"
)

# ------------- MongoDB -------------
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]

services_col = db["services"]
categories_col = db["categories"]
officers_col = db["officers"]
ads_col = db["ads"]
admins_col = db["admins"]
eng_col = db["engagements"]
profiles_col = db["profiles"]


#  //profile
@app.route("/api/profile/step", methods=["POST"])
def api_profile_step():
    data = request.json or {}
    step = data.get("step")
    profile_id = data.get("profile_id")
    step_data = data.get("data", {})

    if step not in ["basic", "contact", "employment"]:
        return jsonify({"error": "Invalid step"}), 400

    # STEP 1: create profile
    if step == "basic":
        doc = {
            "name": step_data.get("name"),
            "age": step_data.get("age"),
            "email": step_data.get("email"),
            "phone": None,
            "job": None,
            "created_at": datetime.utcnow()
        }
        result = profiles_col.insert_one(doc)
        return jsonify({"profile_id": str(result.inserted_id)})

    # STEP 2 + STEP 3 require profile_id
    if not profile_id:
        return jsonify({"error": "profile_id required"}), 400

    try:
        pid = ObjectId(profile_id)
    except Exception:
        return jsonify({"error": "Invalid profile_id"}), 400

    # STEP 2: update contact
    if step == "contact":
        profiles_col.update_one(
            {"_id": pid},
            {"$set": {
                "email": step_data.get("email"),
                "phone": step_data.get("phone")
            }}
        )
        return jsonify({"status": "ok"})

    # STEP 3: update employment
    if step == "employment":
        profiles_col.update_one(
            {"_id": pid},
            {"$set": {
                "job": step_data.get("job")
            }}
        )
        return jsonify({"status": "ok"})

    return jsonify({"error": "Unhandled case"}), 400


# ------------- JSON Helper -------------
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


# ------------- Admin Auth -------------
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


# ------------- Default Admin Creation -------------
def create_default_admin():
    admin = admins_col.find_one({"username": "admin"})
    if admin:
        stored = admin.get("password")
        # if stored password was accidentally saved as plain string, remove and recreate
        if isinstance(stored, str):
            admins_col.delete_one({"_id": admin["_id"]})
        else:
            return
    pwd = os.environ.get("ADMIN_PWD", "admin123")
    hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
    admins_col.insert_one({"username": "admin", "password": hashed})
    print("Default admin created: username='admin', password='admin123'")


def build_faiss_index():
    if not FAISS_AVAILABLE:
        print(" FAISS not available — using fallback text search.")
        return None

    services = list(services_col.find({}, {"_id": 0}))
    items = []
    texts = []

    # flatten questions → embedding list
    for service in services:
        for sub in service.get("subservices", []):
            for q in sub.get("questions", []):
                full_text = (
                    service.get("name", {}).get("en", "") + " "
                    + sub.get("name", {}).get("en", "") + " "
                    + q.get("q", {}).get("en", "")
                )
                texts.append(full_text)
                items.append({
                    "service": service.get("name", {}).get("en"),
                    "subservice": sub.get("name", {}).get("en"),
                    "question": q.get("q", {}).get("en"),
                    "answer": q.get("answer", {}).get("en")
                })

    model = get_embedding_model()
    vectors = model.encode(texts, convert_to_numpy=True)

    index = faiss.IndexFlatL2(VECTOR_DIM)
    index.add(vectors)

    # save faiss index
    if not INDEX_PATH.parent.exists():
        INDEX_PATH.parent.mkdir(parents=True)
    faiss.write_index(index, str(INDEX_PATH))

    # save metadata
    import json
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

    print("FAISS index built successfully.")
    return index


# AI faiss vector search
@app.route("/api/ai/faiss_search", methods=["POST"])
def api_ai_faiss_search():
    query = (request.json or {}).get("query", "").strip()
    if not query:
        return jsonify({"error": "Query required"}), 400

    if not FAISS_AVAILABLE or not INDEX_PATH.exists():
        return jsonify({"error": "FAISS not installed or index missing"}), 500

    import json
    index = faiss.read_index(str(INDEX_PATH))
    meta = json.load(open(META_PATH))

    model = get_embedding_model()
    q_vec = model.encode([query], convert_to_numpy=True)

    k = 5  # top 5 matches
    distances, ids = index.search(q_vec, k)

    results = [meta[i] for i in ids[0]]
    return jsonify(results)


@app.route("/")
def home():
    try:
        return render_template("main.html")
    except Exception:
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
    except Exception:
        return "Admin Dashboard"


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


# ------------------ PUBLIC APIS ------------------
@app.route("/api/services", methods=["GET"])
def api_services():
    docs = list(services_col.find({}, {"_id": 0}))
    return jsonify(to_jsonable(docs))


@app.route("/api/categories", methods=["GET", "POST"])
def get_categories():
    if request.method == "POST":
        data = request.json
        print("POST data:", data)

        # Validate
        if not data or not data.get("id") or not data.get("name", {}).get("en"):
            return jsonify({"error": "Missing required fields"}), 400

        # Check duplicate
        if categories_col.find_one({"id": data["id"]}):
            return jsonify({"error": "Category ID already exists"}), 400

        categories_col.insert_one(data)
        return jsonify({"message": "Category added successfully"})

    # GET: return categories
    docs = list(categories_col.find({}, {"_id": 0}))
    return jsonify(docs)

@app.route("/api/officers", methods=["GET", "POST"])
def api_officers():
    if request.method == "POST":
        data = request.json

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        required = ["id", "name", "role", "ministry_id", "email", "phone"]
        for field in required:
            if field not in data or not data[field].strip():
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Insert into Mongo
        officers_col.insert_one(data)
        return jsonify({"message": "Officer added successfully!"}), 201

    # GET = return list
    return jsonify(list(officers_col.find({})))

@app.route("/api/ads", methods=["GET", "POST"])
def api_ads():
    if request.method == "POST":
        data = request.json or {}

        # Validate
        if not data.get("id") or not data.get("title"):
            return jsonify({"error": "Missing required fields (id, title)"}), 400

        # Prevent duplicate ad id
        if ads_col.find_one({"id": data["id"]}):
            return jsonify({"error": "Ad ID already exists"}), 400

        ads_col.insert_one(data)
        return jsonify({"message": "Ad added successfully"}), 201

    # GET all ads
    docs = list(ads_col.find({}, {"_id": 0}))
    return jsonify(docs)








# ------------------ EXPORT CSV ------------------
@app.route("/api/admin/export_engagement_csv", methods=["GET"])
@admin_required
def export_engagement_csv():
    try:
        cursor = eng_col.find()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["user_id", "age", "job", "desires", "question_clicked",
                         "service", "ad", "source", "timestamp"])
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


# ------------------ STARTUP ------------------
if __name__ == "__main__":
    create_default_admin()

    # build FAISS index once at startup (optional)
    if FAISS_AVAILABLE:
        build_faiss_index()

    # run local dev server
    app.run(debug=True, host="127.0.0.1", port=5000)
