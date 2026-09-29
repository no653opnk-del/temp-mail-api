from flask import Flask, jsonify, request

app = Flask(__name__)

# قاعدة بيانات مؤقتة لتجربة الفكرة
users_db = {}

@app.route('/')
def home():
    return jsonify({"status": "Server is running successfully!"})

# إنشاء حساب بإيميل وباسورد
@app.route('/create-acc', methods=['POST'])
def create_account():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if email in users_db:
        return jsonify({"error": "Email already exists"}), 400
        
    users_db[email] = {"password": password, "messages": []}
    return jsonify({"message": f"Account {email} created successfully!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
