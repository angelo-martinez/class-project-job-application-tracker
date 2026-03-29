import json
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)

def get_db():
  return mysql.connector.connect(
    host='localhost', user='root',
    password='password', database='job_tracker'
  )

@app.route('/')
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT COUNT(*) AS count FROM companies')
    conn.close()
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
