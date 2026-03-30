import json
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'application_tracker_secret_key'

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
    total_companies = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) AS count FROM jobs')
    total_jobs = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) AS count FROM applications')
    total_applications = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) AS count FROM contacts')
    total_contacts = cursor.fetchone()['count']

    cursor.execute(
        'SELECT status, COUNT(*) AS count FROM applications GROUP BY status'
    )
    status_counts = {row['status']: row['count'] for row in cursor.fetchall()}

    cursor.execute('''
        SELECT a.application_id, a.application_date, a.status,
               j.job_title, c.company_name
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY a.application_date DESC
        LIMIT 5
    ''')
    recent_apps = cursor.fetchall()

    conn.close()
    return render_template('dashboard.html',
                           total_companies=total_companies,
                           total_jobs=total_jobs,
                           total_applications=total_applications,
                           total_contacts=total_contacts,
                           status_counts=status_counts,
                           recent_apps=recent_apps)

@app.route('/companies')
def companies_list():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM companies ORDER BY company_name')
    companies = cursor.fetchall()
    conn.close()
    return render_template('companies.html', companies=companies)


@app.route('/companies/add', methods=['GET', 'POST'])
def companies_add():
    if request.method == 'POST':
        name = request.form.get('company_name', '').strip()
        if not name:
            flash('Company name is required.', 'danger')
            return redirect(url_for('companies_add'))

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO companies
               (company_name, industry, website, city, state, notes)
               VALUES (%s, %s, %s, %s, %s, %s)''',
            (name,
             request.form.get('industry', '').strip(),
             request.form.get('website', '').strip(),
             request.form.get('city', '').strip(),
             request.form.get('state', '').strip(),
             request.form.get('notes', '').strip())
        )
        conn.commit()
        conn.close()
        flash('Company added successfully!', 'success')
        return redirect(url_for('companies_list'))

    return render_template('companies.html', form_mode='add')


@app.route('/companies/<int:company_id>/edit', methods=['GET', 'POST'])
def companies_edit(company_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form.get('company_name', '').strip()
        if not name:
            flash('Company name is required.', 'danger')
            return redirect(url_for('companies_edit', company_id=company_id))

        cursor.execute(
            '''UPDATE companies
               SET company_name=%s, industry=%s, website=%s,
                   city=%s, state=%s, notes=%s
               WHERE company_id=%s''',
            (name,
             request.form.get('industry', '').strip(),
             request.form.get('website', '').strip(),
             request.form.get('city', '').strip(),
             request.form.get('state', '').strip(),
             request.form.get('notes', '').strip(),
             company_id)
        )
        conn.commit()
        conn.close()
        flash('Company updated successfully!', 'success')
        return redirect(url_for('companies_list'))

    cursor.execute('SELECT * FROM companies WHERE company_id = %s', (company_id,))
    company = cursor.fetchone()
    conn.close()
    if not company:
        flash('Company not found.', 'danger')
        return redirect(url_for('companies_list'))
    return render_template('companies.html', form_mode='edit', company=company)


@app.route('/companies/<int:company_id>/delete', methods=['POST'])
def companies_delete(company_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM companies WHERE company_id = %s', (company_id,))
    conn.commit()
    conn.close()
    flash('Company deleted.', 'success')
    return redirect(url_for('companies_list'))

if __name__ == '__main__':
    app.run(debug=True)
