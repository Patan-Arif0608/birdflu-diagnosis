from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__, static_folder="static")

# Google API Key (Keep it secure)
GOOGLE_API_KEY = "AIzaSyAZGTjgXWM9RtjA_OP6DEcdXEHLm49lbAg"  # Replace with your valid API key

@app.route('/')
def home():
    return render_template("index.html")

def diagnose_bird_flu(symptoms):
    risk_score = 0
    messages = []

    # Convert "Yes"/"No" to boolean values
    fever = symptoms.get("fever", "No") == "Yes"
    cough = symptoms.get("cough", "No") == "Yes"
    sore_throat = symptoms.get("sore_throat", "No") == "Yes"
    fatigue = symptoms.get("fatigue", "None")  
    difficulty_breathing = symptoms.get("difficulty_breathing", "No") == "Yes"
    travel_history = symptoms.get("travel_history", "No") == "Yes"

    # Assign risk scores
    if fever: risk_score += 3
    if cough: risk_score += 2
    if sore_throat: risk_score += 2
    if fatigue == "Severe": risk_score += 3
    elif fatigue == "Moderate": risk_score += 2
    elif fatigue == "Mild": risk_score += 1
    if difficulty_breathing: risk_score += 4
    if travel_history: risk_score += 3

    # Diagnosis messages
    if risk_score >= 10:
        messages.append("⚠️ High probability of Bird Flu! Please consult a doctor immediately.")
    elif 5 <= risk_score < 10:
        messages.append("⚠️ Moderate probability. Monitor symptoms and take precautions.")
    else:
        messages.append("✅ Low probability. Stay hydrated and rest.")

    # Medicine and home remedies recommendations
    medicines = ["Paracetamol for fever", "Cough syrup", "Vitamin C supplements"]
    if difficulty_breathing:
        medicines.append("Consult a doctor for prescribed antivirals")

    home_remedies = [
        "Drink warm water frequently to stay hydrated",
        "Inhale steam to relieve congestion",
        "Consume honey and ginger to soothe the throat",
        "Drink herbal tea with turmeric and black pepper",
        "Stay in sunlight for vitamin D to boost immunity",
        "Avoid cold beverages and prefer warm soups"
    ]

    return {
        "risk_score": risk_score,
        "messages": messages,
        "medicines": medicines,
        "home_remedies": home_remedies
    }

@app.route("/diagnose", methods=["POST"])
def diagnose():
    data = request.json
    result = diagnose_bird_flu(data)
    return jsonify(result)

@app.route("/nearby_hospitals", methods=["POST"])
def nearby_hospitals():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not latitude or not longitude:
        return jsonify({"error": "Location not provided"}), 400

    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=5000&type=hospital&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    hospitals = response.json()

    hospital_list = []
    if hospitals.get("results"):
        for hospital in hospitals["results"][:5]:  # Get top 5 hospitals
            hospital_list.append({
                "name": hospital.get("name"),
                "address": hospital.get("vicinity"),
                "map_link": f"https://www.google.com/maps/search/?api=1&query={hospital['geometry']['location']['lat']},{hospital['geometry']['location']['lng']}"
            })

    return jsonify(hospital_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
