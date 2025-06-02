from flask import Flask, request, redirect, render_template
import sqlite3
import string
import random

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('urls.db')
    conn.execute('CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY AUTOINCREMENT, long_url TEXT, short_code TEXT UNIQUE, clicks INTEGER DEFAULT 0)')
    conn.close()

def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        short_code = generate_short_code()
        conn = sqlite3.connect('urls.db')
        try:
            conn.execute('INSERT INTO urls (long_url, short_code) VALUES (?, ?)', (long_url, short_code))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Short code already exists. Try again."
        conn.close()
        return render_template('index.html', short_url=request.host_url + short_code)
    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_long_url(short_code):
    conn = sqlite3.connect('urls.db')
    cur = conn.cursor()
    cur.execute('SELECT long_url, clicks FROM urls WHERE short_code = ?', (short_code,))
    result = cur.fetchone()
    if result:
        long_url, clicks = result
        cur.execute('UPDATE urls SET clicks = ? WHERE short_code = ?', (clicks + 1, short_code))
        conn.commit()
        conn.close()
        return redirect(long_url)
    conn.close()
    return "URL not found."

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

