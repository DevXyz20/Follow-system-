from flask import Flask, render_template, request
import sqlite3
from instagrapi import Client

app = Flask(__name__)

# إنشاء قاعدة البيانات إذا لم تكن موجودة
def init_db():
    conn = sqlite3.connect('igfollower.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            device_id TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# صفحة التحكم في الحسابات
@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    active_accounts_count = 0

    conn = sqlite3.connect('igfollower.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    active_accounts_count = c.fetchone()[0]

    if request.method == 'POST':
        target_username = request.form['target_username']

        # جلب جميع الحسابات المسجلة
        c.execute("SELECT username, password FROM users")
        accounts = c.fetchall()

        # تنفيذ عملية المتابعة لكل حساب
        for account in accounts:
            ig_username, ig_password = account

            cl = Client()
            try:
                cl.login(ig_username, ig_password)
                cl.user_follow(cl.user_id_from_username(target_username))
                message += f"Account {ig_username} followed {target_username} successfully!<br>"
            except Exception as e:
                message += f"Failed to follow {target_username} with account {ig_username}: {str(e)}<br>"
            finally:
                cl.logout()

    conn.close()

    return render_template('index.html', message=message, active_accounts_count=active_accounts_count)

if __name__ == '__main__':
    app.run(debug=True)
