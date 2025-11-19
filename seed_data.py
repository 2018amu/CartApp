from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not set in environment variables")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
services_col = db["services"]

# Clear existing documents
services_col.delete_many({})

# Seed data with translations
docs = [
    {
        "id": "ministry_it",
        "name": {"en": "Ministry of IT & Digital Affairs", "si": "තොරතුරු තාක්ෂණ අමාත්‍යාංශය", "ta": "தகவல் தொழில்நுட்ப அமைச்சு"},
        "subservices": [
            {
                "id": "it_cert",
                "name": {"en": "IT Certificates", "si": "අයිටී සහතික", "ta": "ஐடி சான்றிதழ்கள்"},
                "questions": [
                    {
                        "q": {"en": "How to apply for an IT certificate?", "si": "IT සහතිකය සඳහා ඉල්ලීම් කරන ආකාරය?", "ta": "ஐடி சான்றிதழுக்கு விண்ணப்பிப்பது எப்படி?"},
                        "answer": {"en": "Fill online form and upload NIC.", "si": "ඔන්ලයින් පෝරම පිරවුවොත් NIC උඩුගත කරන්න.", "ta": "ஆன்லைன் படிவத்தை நிரப்பி NIC ஐ பதிவேற்றவும்."},
                        "downloads": ["/static/forms/it_cert_form.pdf"],
                        "location": "https://maps.google.com/?q=Ministry+of+IT",
                        "instructions": "Visit the digital portal, register and submit application."
                    }
                ]
            }
        ]
    },
    {
        "id": "ministry_education",
        "name": {"en": "Ministry of Education", "si": "අධ්‍යාපන අමාත්‍යාංශය", "ta": "கல்வி அமைச்சு"},
        "subservices": [
            {
                "id": "schools",
                "name": {"en": "Schools", "si": "පාසල්", "ta": "பள்ளிகள்"},
                "questions": [
                    {
                        "q": {"en": "How to register a school?", "si": "පාසලක් ලියාපදිංචි කිරීම?", "ta": "பள்ளியை பதிவு செய்வது எப்படி?"},
                        "answer": {"en": "Complete registration form and submit documents.", "si": "ලියාපදිංචි පෝරමය පුරවා ලේඛන සලසන්න.", "ta": "பதிவு படிவத்தை பூர்த்தி செய்து ஆவணங்களை சமர்ப்பிக்கவும்."},
                        "downloads": ["/static/forms/school_reg.pdf"],
                        "location": "https://maps.google.com/?q=Ministry+of+Education",
                        "instructions": "Follow the guidelines on the education portal."
                    }
                ]
            }
        ]
    }
]

# Add remaining ministries with translations
rest = [
    {"id": "ministry_health", "en": "Ministry of Health", "si": "සෞඛ්‍ය අමාත්‍යාංශය", "ta": "சுகாதார அமைச்சு"},
    {"id": "ministry_transport", "en": "Ministry of Transport", "si": "ප්‍රවාහන අමාත්‍යාංශය", "ta": "போக்குவரத்து அமைச்சு"},
    {"id": "ministry_imm", "en": "Ministry of Immigration", "si": "ඉමීග්‍රේෂන් අමාත්‍යාංශය", "ta": "இமிக்ரேஷன் அமைச்சு"},
    {"id": "ministry_foreign", "en": "Ministry of Foreign Affairs", "si": "විදේශ කටයුතු අමාත්‍යාංශය", "ta": "வெளிநாட்டு அமைச்சு"},
    {"id": "ministry_finance", "en": "Ministry of Finance", "si": "මූල්‍ය අමාත්‍යාංශය", "ta": "பணக்காரிய அமைச்சு"},
    {"id": "ministry_labour", "en": "Ministry of Labour", "si": "ශ්‍රම අමාත්‍යාංශය", "ta": "தொழிலாளர் அமைச்சு"},
    {"id": "ministry_public", "en": "Ministry of Public Services", "si": "පොදු සේවා අමාත්‍යාංශය", "ta": "பொது சேவைகள் அமைச்சு"},
    {"id": "ministry_justice", "en": "Ministry of Justice", "si": "යුතුකම් අමාත්‍යාංශය", "ta": "நீதித்துறை அமைச்சு"},
    {"id": "ministry_housing", "en": "Ministry of Housing", "si": "නිවාස අමාත්‍යාංශය", "ta": "வீட்டு அமைச்சு"},
    {"id": "ministry_agri", "en": "Ministry of Agriculture", "si": "කෘෂිකාර්මික අමාත්‍යාංශය", "ta": "விவசாய அமைச்சு"},
    {"id": "ministry_youth", "en": "Ministry of Youth Affairs", "si": "යොවුන් අමාත්‍යාංශය", "ta": "இளைஞர் அமைச்சு"},
    {"id": "ministry_defence", "en": "Ministry of Defence", "si": "ප්‍රතිරක්ෂා අමාත්‍යාංශය", "ta": "பாதுகாப்பு அமைச்சு"},
    {"id": "ministry_tourism", "en": "Ministry of Tourism", "si": " සංචාරක අමාත්‍යාංශය", "ta": "சுற்றுலா அமைச்சு"},
    {"id": "ministry_trade", "en": "Ministry of Trade", "si": "වෙළඳ අමාත්‍යාංශය", "ta": "வணிக அமைச்சு"},
    {"id": "ministry_energy", "en": "Ministry of Energy", "si": "බලශක්ති අමාත්‍යාංශය", "ta": "மின்சாரம் அமைச்சு"},
    {"id": "ministry_water", "en": "Ministry of Water Resources", "si": "ජල සම්පත් අමාත්‍යාංශය", "ta": "நீர் வளங்கள் அமைச்சு"},
    {"id": "ministry_env", "en": "Ministry of Environment", "si": "පරිසර අමාත්‍යාංශය", "ta": "பரப்புரை அமைச்சு"},
    {"id": "ministry_culture", "en": "Ministry of Culture", "si": "සංස්කෘතික අමාත්‍යාංශය", "ta": "கலாச்சார அமைச்சு"}
]

for m in rest:
    docs.append({
        "id": m["id"],
        "name": {"en": m["en"], "si": m["si"], "ta": m["ta"]},
        "subservices": [
            {
                "id": "general",
                "name": {"en": "General Services", "si": "සාමාන්‍ය සේවාවන්", "ta": "பொது சேவைகள்"},
                "questions": [
                    {
                        "q": {
                            "en": "What services are offered?",
                            "si": "ඔබට ලබා දිය හැකි සේවාවන් මොනවාද?",
                            "ta": "எந்த சேவைகள் வழங்கப்படுகின்றன?"
                        },
                        "answer": {
                            "en": "Please check the service list on the portal.",
                            "si": "පෝර්ටලයේ සේවා ලැයිස්තුව බලන්න.",
                            "ta": "போர்ட்டலில் சேவை பட்டியலைப் பார்க்கவும்."
                        },
                        "downloads": [],
                        "location": "",
                        "instructions": "Use contact details to get more info."
                    }
                ]
            }
        ]
    })

# Insert into MongoDB
services_col.insert_many(docs)
print("Seeded services:", services_col.count_documents({}))
