from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# قاعدة بيانات مؤقتة
users_db = {}

# تصميم واجهة الموقع (HTML)
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خدمة البريد المؤقت</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f4f9; padding: 20px; text-align: center; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
        input { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 95%; }
        button:hover { background: #0056b3; }
        .box { margin-top: 20px; text-align: right; background: #fff; padding: 15px; border-radius: 5px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="card">
        <h2>📧 موقع البريد المؤقت</h2>
        <p>أنشئ حساباً وادخل إليه في أي وقت</p>
        <form action="/create-web" method="POST">
            <input type="text" name="email" placeholder="اسم الإيميل (مثال: test@domain.com)" required>
            <input type="password" name="password" placeholder="كلمة السر" required>
            <button type="submit">إنشاء / تسجيل الدخول</button>
        </form>
        {% if msg %}
            <p style="color: green;">{{ msg }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

@app.route('/create-web', methods=['POST'])
def create_web():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if email not in users_db:
        users_db[email] = {"password": password, "messages": []}
        msg = f"تم إنشاء الحساب بنجاح: {email}"
    else:
        if users_db[email]["password"] == password:
            msg = f"تم تسجيل الدخول بنجاح إلى: {email}"
        else:
            msg = "كلمة السر غير صحيحة!"
            
    return render_template_string(HTML_LAYOUT, msg=msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
