from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# Temporary in-memory database
users_db = {}

# English HTML Layout
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Temp Mail Service</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, sans-serif; background-color: #f0f2f5; padding: 20px; text-align: center; margin: 0; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 420px; margin: 20px auto; }
        .tabs { display: flex; border-bottom: 2px solid #eee; margin-bottom: 20px; }
        .tab-btn { flex: 1; padding: 10px; border: none; background: none; font-size: 16px; font-weight: bold; cursor: pointer; color: #65670b; }
        .tab-btn.active { border-bottom: 3px solid #007bff; color: #007bff; }
        input { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; }
        button { background: #007bff; color: white; padding: 12px; border: none; border-radius: 6px; cursor: pointer; width: 100%; font-size: 16px; font-weight: bold; margin-top: 10px; }
        button:hover { background: #0056b3; }
        .alert { padding: 10px; border-radius: 6px; margin-top: 15px; font-size: 14px; }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #f8d7da; color: #721c24; }
        .inbox { text-align: left; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 600px; margin: 20px auto; }
        .msg-item { border-bottom: 1px solid #eee; padding: 10px 0; }
        .logout-btn { background: #dc3545; margin-top: 15px; }
    </style>
</head>
<body>

    {% if current_user %}
        <!-- Inbox View -->
        <div class="inbox">
            <h2>📥 Inbox for: {{ current_user }}</h2>
            <hr>
            <h3>Received Messages:</h3>
            {% if messages %}
                {% for msg in messages %}
                    <div class="msg-item">
                        <strong>From:</strong> {{ msg.sender }}<br>
                        <strong>Subject:</strong> {{ msg.subject }}<br>
                        <p>{{ msg.body }}</p>
                    </div>
                {% endfor %}
            {% else %}
                <p style="color: #777;">No new messages yet. Refresh the page to check again.</p>
            {% endif %}
            
            <a href="/"><button class="logout-btn">Log Out</button></a>
        </div>

    {% else %}
        <!-- Sign Up / Login Form -->
        <div class="card">
            <h2>📧 Temp Mail</h2>
            
            <div class="tabs">
                <button class="tab-btn active" onclick="showTab('signup')">Sign Up</button>
                <button class="tab-btn" onclick="showTab('login')">Log In</button>
            </div>

            <!-- Sign Up Form -->
            <form id="signup-form" action="/register" method="POST">
                <input type="text" name="email" placeholder="Email address (e.g. user@domain.com)" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Create Account</button>
            </form>

            <!-- Login Form -->
            <form id="login-form" action="/login" method="POST" style="display: none;">
                <input type="text" name="email" placeholder="Email address" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Log In</button>
            </form>

            {% if msg %}
                <div class="alert {% if error %}alert-error{% else %}alert-success{% endif %}">
                    {{ msg }}
                </div>
            {% endif %}
        </div>

        <script>
            function showTab(tab) {
                const signupForm = document.getElementById('signup-form');
                const loginForm = document.getElementById('login-form');
                const tabs = document.querySelectorAll('.tab-btn');
                
                if (tab === 'signup') {
                    signupForm.style.display = 'block';
                    loginForm.style.display = 'none';
                    tabs[0].classList.add('active');
                    tabs[1].classList.remove('active');
                } else {
                    signupForm.style.display = 'none';
                    loginForm.style.display = 'block';
                    tabs[1].classList.add('active');
                    tabs[0].classList.remove('active');
                }
            }
        </script>
    {% endif %}

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

# 1. Register Route
@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email').strip().lower()
    password = request.form.get('password')
    
    if email in users_db:
        return render_template_string(HTML_LAYOUT, msg="Email already exists! Try another one.", error=True)
    
    users_db[email] = {"password": password, "messages": []}
    return render_template_string(HTML_LAYOUT, msg="Account created successfully! You can now log in.", error=False)

# 2. Login Route
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email').strip().lower()
    password = request.form.get('password')
    
    if email not in users_db:
        return render_template_string(HTML_LAYOUT, msg="Email not found!", error=True)
        
    if users_db[email]["password"] != password:
        return render_template_string(HTML_LAYOUT, msg="Incorrect password!", error=True)
        
    messages = users_db[email]["messages"]
    return render_template_string(HTML_LAYOUT, current_user=email, messages=messages)

# 3. Webhook Route (Receives real incoming emails)
@app.route('/webhook', methods=['POST'])
def receive_email():
    data = request.json or request.form
    
    # Reading incoming mail details
    recipient = (data.get('recipient') or data.get('to') or '').strip().lower()
    sender = data.get('sender') or data.get('from') or 'Unknown Sender'
    subject = data.get('subject') or 'No Subject'
    body = data.get('body-plain') or data.get('text') or data.get('body') or ''

    # Clean email address if it contains extra characters/headers
    if '<' in recipient and '>' in recipient:
        recipient = recipient.split('<')[1].split('>')[0].strip()

    # Save to user's inbox
    if recipient in users_db:
        users_db[recipient]["messages"].append({
            "sender": sender,
            "subject": subject,
            "body": body
        })
        return jsonify({"status": "success"}), 200

    return jsonify({"error": "User email not found in database"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
