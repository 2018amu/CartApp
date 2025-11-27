# gdpr_addons.py
from flask import request, jsonify, render_template
from datetime import datetime, timedelta

def register_gdpr_routes(app, eng_col):
    """
    Registers GDPR/privacy endpoints to your existing Flask app.
    eng_col: MongoDB collection for engagements
    """

    # -------------------
    # 1️⃣ Privacy Policy Page
    # -------------------
    @app.route("/privacy")
    def privacy_policy():
        return render_template("privacy.html")  # create templates/privacy.html

    # -------------------
    # 2️⃣ User Data Deletion
    # -------------------
    @app.route("/api/user/delete", methods=["POST"])
    def delete_user_data():
        payload = request.get_json() or {}
        user_id = payload.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        # Delete engagement records
        eng_col.delete_many({"user_id": user_id})

        # Add other personal data deletion if needed (ads, profiles, etc.)
        # e.g., ads_col.delete_many({"user_id": user_id})

        return jsonify({"status": "deleted"})

    # -------------------
    # 3️⃣ Automatic Retention (call periodically)
    # -------------------
    def delete_old_engagements():
        cutoff = datetime.utcnow() - timedelta(days=365)  # 1 year
        deleted_count = eng_col.delete_many({"timestamp": {"$lt": cutoff}}).deleted_count
        return deleted_count

    # -------------------
    # 4️⃣ Consent / Opt-Out for Ads
    # -------------------
    # Wrap your existing engagement endpoint or provide a new one
    @app.route("/api/engagement/consent", methods=["POST"])
    def api_engagement_with_consent():
        payload = request.get_json() or {}
        consent_ads = payload.get("consent_ads", True)  # default True

        doc = {
            "user_id": payload.get("user_id"),
            "age": int(payload.get("age")) if payload.get("age") else None,
            "job": payload.get("job"),
            "desires": payload.get("desires") if consent_ads else [],
            "ad": payload.get("ad") if consent_ads else None,
            "source": payload.get("source"),
            "timestamp": datetime.utcnow(),
        }
        eng_col.insert_one(doc)
        return jsonify({"status": "ok"})

    # Return utility function for retention
    return delete_old_engagements
