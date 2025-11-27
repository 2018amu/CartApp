from pymongo import MongoClient

# MongoDB
MONGO_URI = "mongodb+srv://amushun1992_db_user:PwQge1UbU41Z3Xjs@tm-users.vxuhp3p.mongodb.net/citizen_portal?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]

# Collections
services_col = db["services"]
categories_col = db["categories"]
officers_col = db["officers"]
ads_col = db["ads"]

# Clear old data
services_col.delete_many({})
categories_col.delete_many({})
officers_col.delete_many({})
ads_col.delete_many({})

print("Cleared old data...\n")

# ===============================
# ✅ ALL GOVERNMENT CATEGORIES
# ===============================
categories = [
    {"id": "cat_it", "name": {
        "en": "IT & Digital", "si": "තොරතුරු හා ඩිජිටල්", "ta": "தகவல் மற்றும் டிஜிட்டல்"},
        "ministry_ids": ["ministry_it"]
    },
    {"id": "cat_land", "name": {
        "en": "Land", "si": "භූමි", "ta": "நிலம்"},
        "ministry_ids": ["ministry_land"]
    },
    {"id": "cat_transport", "name": {
        "en": "Transport", "si": "ප්‍රවාහනය", "ta": "போக்குவரத்து"},
        "ministry_ids": ["ministry_transport"]
    },
    {"id": "cat_education", "name": {
        "en": "Education", "si": "අධ්‍යාපන", "ta": "கல்வி"},
        "ministry_ids": ["ministry_education"]
    },
    {"id": "cat_health", "name": {
        "en": "Health", "si": "සෞඛ්‍ය", "ta": "சுகாதாரம்"},
        "ministry_ids": ["ministry_health"]
    },
    {"id": "cat_elections", "name": {
        "en": "Elections", "si": "මැතිවරණ", "ta": "தேர்தல்கள்"},
        "ministry_ids": ["ministry_election"]
    },
    {"id": "cat_water", "name": {
        "en": "Water", "si": "ජල සේවා", "ta": "தண்ணீர்"},
        "ministry_ids": ["ministry_water"]
    },
    {"id": "cat_power", "name": {
        "en": "Power", "si": "විදුලි බලය", "ta": "மின்சாரம்"},
        "ministry_ids": ["ministry_power"]
    },
    {"id": "cat_road", "name": {
        "en": "Road Safety", "si": "මාර්ග ආරක්ෂාව", "ta": "சாலை பாதுகாப்பு"},
        "ministry_ids": ["ministry_road"]
    },
    {"id": "cat_immigration", "name": {
        "en": "Immigration", "si": "ආගමනය", "ta": "குடிவரவு"},
        "ministry_ids": ["ministry_immigration"]
    },
    {"id": "cat_foreign", "name": {
        "en": "Foreign Affairs", "si": "විදේශ කටයුතු", "ta": "வெளிநாட்டு அலுவல்கள்"},
        "ministry_ids": ["ministry_foreign"]
    },
    {"id": "cat_finance", "name": {
        "en": "Finance", "si": "මූල්‍ය", "ta": "நிதி"},
        "ministry_ids": ["ministry_finance"]
    },
    {"id": "cat_labour", "name": {
        "en": "Labour", "si": "කාර්මික", "ta": "தொழில்"},
        "ministry_ids": ["ministry_labour"]
    },
    {"id": "cat_justice", "name": {
        "en": "Justice", "si": "නීතිය", "ta": "நீதி"},
        "ministry_ids": ["ministry_justice"]
    },
    {"id": "cat_housing", "name": {
        "en": "Housing", "si": "නිවාස", "ta": "வீடமைப்பு"},
        "ministry_ids": ["ministry_housing"]
    },
    {"id": "cat_agriculture", "name": {
        "en": "Agriculture", "si": "කෘෂිකර්ම", "ta": "விவசாயம்"},
        "ministry_ids": ["ministry_agriculture"]
    },
    {"id": "cat_youth", "name": {
        "en": "Youth Affairs", "si": "යෞවන කටයුතු", "ta": "இளைஞர் அலுவல்கள்"},
        "ministry_ids": ["ministry_youth"]
    },
    {"id": "cat_defence", "name": {
        "en": "Defence", "si": "රක්ෂණ", "ta": "பாதுகாப்பு"},
        "ministry_ids": ["ministry_defence"]
    },
    {"id": "cat_tourism", "name": {
        "en": "Tourism", "si": "සංචාරක", "ta": "சுற்றுலா"},
        "ministry_ids": ["ministry_tourism"]
    },
    {"id": "cat_trade", "name": {
        "en": "Trade", "si": "වණිජය", "ta": "வர்த்தகம்"},
        "ministry_ids": ["ministry_trade"]
    },
    {"id": "cat_environment", "name": {
        "en": "Environment", "si": "පරිසර", "ta": "சூழல்"},
        "ministry_ids": ["ministry_environment"]
    },
    {"id": "cat_culture", "name": {
        "en": "Culture", "si": "සංස්කෘතික", "ta": "கலாச்சாரம்"},
        "ministry_ids": ["ministry_culture"]
    }
]

categories_col.insert_many(categories)
print("Categories inserted.")

# ===============================
# OFFICERS
# ===============================
officers = [
    {
        "id": "off_it_01",
        "name": "Ms. Nayana Perera",
        "role": "Director - Digital Services",
        "ministry_id": "ministry_it",
        "contact": {"email": "nayana@it.gov.lk", "phone": "071-xxxxxxx"}
    }
]

officers_col.insert_many(officers)
print("Officers inserted.")

# ===============================
# ADS
# ===============================
ads = [
    {
        "id": "ad_courses_01",
        "title": "Free Digital Skills Course",
        "body": "Enroll now for government digital skills training.",
        "link": "https://spacexp.edu.lk/courses",
        "image": "/static/img/course-card.png"
    }
]

ads_col.insert_many(ads)
print("Ads inserted.")

# ===============================
# SERVICES
# ===============================
services = [
    {
        "id": "ministry_it",
        "category": "cat_it",
        "name": {
            "en": "Ministry of IT & Digital Affairs",
            "si": "තොරතුරු හා ඩිජිටල් කටයුතු",
            "ta": "தகவல் மற்றும் டிஜிட்டல் அலுவல்கள்"
        },
        "subservices": [
            {
                "id": "it_cert",
                "name": {
                    "en": "IT Certificates",
                    "si": "අයිටී සහතික",
                    "ta": "ஐடி சான்றிதழ்"
                },
                "questions": [
                    {
                        "q": {"en": "How to apply for an IT certificate?"},
                        "answer": {"en": "Fill online form and upload NIC."},
                        "downloads": ["/static/forms/it_cert_form.pdf"],
                        "location": "https://maps.google.com/?q=Ministry+of+IT",
                        "instructions": "Visit the digital portal, register and submit application."
                    },
                    {
                        "q": {"en": "Where can I download exam results?"},
                        "answer": {"en": "Visit the official exam results portal at https://exam.gov.lk/results."}
                    },
                    {
                        "q": {"en": "How to register a school?"},
                        "answer": {"en": "Submit school registration forms online through the education ministry portal."}
                    },
                    {
                        "q": {"en": "How to change NIC details?"},
                        "answer": {"en": "Apply at the Department of Registration with old NIC + documents."}
                    },
                    {
                        "q": {"en": "How to apply for a building permit?"},
                        "answer": {"en": "Submit a building permit application at your local municipal council."}
                    },
                    {
                        "q": {"en": "How to renew a passport?"},
                        "answer": {"en": "Fill the online renewal form and upload the required documents."}
                    },
                    {
                        "q": {"en": "How to get a new water connection?"},
                        "answer": {"en": "Apply online or visit the nearest water supply office."}
                    },
                    {
                        "q": {"en": "Where to report a road safety complaint?"},
                        "answer": {"en": "Report through the traffic police portal or nearest station."}
                    },
                    {
                        "q": {"en": "How to register a business?"},
                        "answer": {"en": "Use the official business registration portal."}
                    },
                    {
                        "q": {"en": "What digital training courses are available?"},
                        "answer": {"en": "Visit the government's digital skills training portal."}
                    }
                ]
            }
        ]
    }
]

services_col.insert_many(services)
print("Services inserted.")

print(" SEED COMPLETE — All collections updated successfully!")
