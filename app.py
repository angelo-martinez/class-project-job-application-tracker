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

@app.route('/jobs')
def jobs_list():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT j.*, c.company_name
        FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.company_id
        ORDER BY j.date_posted DESC
    ''')
    jobs = cursor.fetchall()
    for job in jobs:
        if job['requirements']:
            if isinstance(job['requirements'], str):
                job['requirements'] = json.loads(job['requirements'])
        else:
            job['requirements'] = []
    conn.close()
    return render_template('jobs.html', jobs=jobs)

@app.route('/jobs/add', methods=['GET', 'POST'])
def jobs_add():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        title = request.form.get('job_title', '').strip()
        if not title:
            flash('Job title is required.', 'danger')
            return redirect(url_for('jobs_add'))

        reqs_raw = request.form.get('requirements', '').strip()
        reqs_json = json.dumps([r.strip() for r in reqs_raw.split(',') if r.strip()]) if reqs_raw else None

        salary_min = request.form.get('salary_min', '').strip()
        salary_max = request.form.get('salary_max', '').strip()

        cursor.execute(
            '''INSERT INTO jobs
               (company_id, job_title, job_type, salary_min, salary_max,
                job_url, date_posted, requirements)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (request.form.get('company_id') or None,
             title,
             request.form.get('job_type') or None,
             int(salary_min) if salary_min else None,
             int(salary_max) if salary_max else None,
             request.form.get('job_url', '').strip() or None,
             request.form.get('date_posted') or None,
             reqs_json)
        )
        conn.commit()
        conn.close()
        flash('Job added successfully!', 'success')
        return redirect(url_for('jobs_list'))

    cursor.execute('SELECT company_id, company_name FROM companies ORDER BY company_name')
    companies = cursor.fetchall()
    conn.close()
    return render_template('jobs.html', form_mode='add', companies=companies)

@app.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
def jobs_edit(job_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        title = request.form.get('job_title', '').strip()
        if not title:
            flash('Job title is required.', 'danger')
            return redirect(url_for('jobs_edit', job_id=job_id))

        reqs_raw = request.form.get('requirements', '').strip()
        reqs_json = json.dumps([r.strip() for r in reqs_raw.split(',') if r.strip()]) if reqs_raw else None

        salary_min = request.form.get('salary_min', '').strip()
        salary_max = request.form.get('salary_max', '').strip()

        cursor.execute(
            '''UPDATE jobs
               SET company_id=%s, job_title=%s, job_type=%s,
                   salary_min=%s, salary_max=%s, job_url=%s,
                   date_posted=%s, requirements=%s
               WHERE job_id=%s''',
            (request.form.get('company_id') or None,
             title,
             request.form.get('job_type') or None,
             int(salary_min) if salary_min else None,
             int(salary_max) if salary_max else None,
             request.form.get('job_url', '').strip() or None,
             request.form.get('date_posted') or None,
             reqs_json,
             job_id)
        )
        conn.commit()
        conn.close()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('jobs_list'))

    cursor.execute('SELECT * FROM jobs WHERE job_id = %s', (job_id,))
    job = cursor.fetchone()
    if not job:
        conn.close()
        flash('Job not found.', 'danger')
        return redirect(url_for('jobs_list'))

    if job['requirements']:
        if isinstance(job['requirements'], str):
            job['requirements'] = json.loads(job['requirements'])
    else:
        job['requirements'] = []

    cursor.execute('SELECT company_id, company_name FROM companies ORDER BY company_name')
    companies = cursor.fetchall()
    conn.close()
    return render_template('jobs.html', form_mode='edit', job=job, companies=companies)

@app.route('/jobs/<int:job_id>/delete', methods=['POST'])
def jobs_delete(job_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jobs WHERE job_id = %s', (job_id,))
    conn.commit()
    conn.close()
    flash('Job deleted.', 'success')
    return redirect(url_for('jobs_list'))

if __name__ == '__main__':
    app.run(debug=True)
