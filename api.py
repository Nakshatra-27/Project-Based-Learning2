from flask import Flask, request, jsonify 
import mysql.connector

app = Flask(__name__)

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root1234",  # Replace with your password
    database="HealthAssistant1"
)
cursor = db.cursor(dictionary=True)

# API to suggest medicine based on symptoms
@app.route('/suggest-medicine', methods=['POST'])
def suggest_medicine():
    data = request.get_json()
    symptoms = data.get('symptoms', [])

    if not symptoms:
        return jsonify({"error": "No symptoms provided."}), 400

    symptoms_tuple = tuple(symptoms)
    query = """
        SELECT DISTINCT d.DiseaseName, m.MedicineName, m.Dosage, m.Frequency 
        FROM Diseases d
        JOIN Symptoms s ON d.SymptomID = s.SymptomID
        JOIN Medicines m ON s.SymptomID = m.ForSymptomID
        WHERE s.SymptomName IN ({})
    """.format(','.join(['%s'] * len(symptoms)))
    
    cursor.execute(query, symptoms_tuple)
    result = cursor.fetchall()

    return jsonify(result) if result else jsonify({"message": "No suggestions found."}), 404

# API to check doctor availability
@app.route('/check-doctor', methods=['GET'])
def check_doctor():
    specialization = request.args.get('specialization', '')
    query = "SELECT * FROM Doctors WHERE Specialization = %s"
    cursor.execute(query, (specialization,))
    result = cursor.fetchall()
    return jsonify(result) if result else jsonify({"message": "No doctors found."}), 404

# API to fetch user prompt and related symptoms
@app.route('/fetch-prompt-symptoms', methods=['GET'])
def fetch_prompt_symptoms():
    user_prompt = request.args.get('prompt', '')
    query = """
        SELECT u.UserPrompt, s.SymptomName 
        FROM UserPrompts u
        JOIN UserPromptSymptoms ups ON u.PromptID = ups.PromptID
        JOIN Symptoms s ON ups.SymptomID = s.SymptomID
        WHERE u.UserPrompt = %s
       """
    cursor.execute(query, (user_prompt,))
    result = cursor.fetchall()
    return jsonify(result) if result else jsonify({"message": "No data found."}), 404

if __name__ == '__main__':
    app.run(debug=True)
