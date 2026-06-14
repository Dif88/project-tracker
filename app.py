from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from database import get_db_connection, dict_cursor, init_db
import csv
from io import StringIO
import os

app = Flask(__name__)

# Ensure the database is initialized on startup
init_db(force_recreate=False)

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY start_date DESC")
    projects = cursor.fetchall()
    
    # Calculate summary metrics
    total_projects = len(projects)
    total_freelance_earnings = sum(p['earnings'] for p in projects if p['type'] == 'Freelance')
    active_personal_projects = sum(1 for p in projects if p['type'] == 'Personal' and p['status'] == 'In Progress')
    
    conn.close()
    
    return render_template(
        'index.html',
        projects=projects,
        total_projects=total_projects,
        total_freelance_earnings=total_freelance_earnings,
        active_personal_projects=active_personal_projects
    )

@app.route('/add', methods=['POST'])
def add_project():
    title = request.form.get('title', '').strip()
    project_type = request.form.get('type', 'Personal')
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    earnings_raw = request.form.get('earnings', '0')
    status = request.form.get('status', 'Not Started')
    tag = request.form.get('tag', 'Other')
    
    # Simple validation
    if not title or not start_date or not end_date:
        return redirect(url_for('index'))
        
    try:
        earnings = float(earnings_raw) if project_type == 'Freelance' else 0.0
    except ValueError:
        earnings = 0.0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO projects (title, type, start_date, end_date, earnings, status, tag)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, project_type, start_date, end_date, earnings, status, tag))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/edit/<int:project_id>', methods=['POST'])
def edit_project(project_id):
    title = request.form.get('title', '').strip()
    project_type = request.form.get('type', 'Personal')
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    earnings_raw = request.form.get('earnings', '0')
    status = request.form.get('status', 'Not Started')
    tag = request.form.get('tag', 'Other')
    
    if not title or not start_date or not end_date:
        return redirect(url_for('index'))
        
    try:
        earnings = float(earnings_raw) if project_type == 'Freelance' else 0.0
    except ValueError:
        earnings = 0.0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects
        SET title = ?, type = ?, start_date = ?, end_date = ?, earnings = ?, status = ?, tag = ?
        WHERE id = ?
    ''', (title, project_type, start_date, end_date, earnings, status, tag, project_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/export')
def export_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, type, start_date, end_date, earnings, status, tag FROM projects ORDER BY start_date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    si = StringIO()
    cw = csv.writer(si)
    # Write CSV Header
    cw.writerow(['ID', 'Project Title', 'Type', 'Start Date', 'End Date', 'Earnings', 'Status', 'Tag'])
    
    # Write Row Data
    for row in rows:
        cw.writerow([
            row['id'],
            row['title'],
            row['type'],
            row['start_date'],
            row['end_date'],
            row['earnings'],
            row['status'],
            row['tag']
        ])
        
    response = Response(si.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=projects_export.csv'
    return response

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()

    if not project:
        conn.close()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM team_members WHERE project_id = ? ORDER BY name", (project_id,))
    team_members = cursor.fetchall()

    cursor.execute("SELECT * FROM team_activities WHERE project_id = ? ORDER BY activity_date DESC", (project_id,))
    activities = cursor.fetchall()

    cursor.execute("SELECT * FROM project_expenses WHERE project_id = ? ORDER BY expense_date DESC", (project_id,))
    expenses = cursor.fetchall()

    total_expenses = sum(e['amount'] for e in expenses)

    conn.close()

    return render_template(
        'project_detail.html',
        project=project,
        team_members=team_members,
        activities=activities,
        expenses=expenses,
        total_expenses=total_expenses
    )

@app.route('/add-team-member/<int:project_id>', methods=['POST'])
def add_team_member(project_id):
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    role = request.form.get('role', 'Developer').strip()

    if not name:
        return redirect(url_for('project_detail', project_id=project_id))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO team_members (project_id, name, email, role)
        VALUES (?, ?, ?, ?)
    ''', (project_id, name, email, role))
    conn.commit()
    conn.close()

    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/delete-team-member/<int:member_id>/<int:project_id>', methods=['POST'])
def delete_team_member(member_id, project_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM team_members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/add-activity/<int:project_id>', methods=['POST'])
def add_activity(project_id):
    member_id = request.form.get('team_member_id')
    member_name = request.form.get('member_name', '').strip()
    task_description = request.form.get('task_description', '').strip()
    activity_date = request.form.get('activity_date', '')
    activity_time = request.form.get('activity_time', '')
    hours_spent = request.form.get('hours_spent', '1')
    logged_by = request.form.get('logged_by', 'System')

    if not task_description or not activity_date:
        return redirect(url_for('project_detail', project_id=project_id))

    try:
        hours = float(hours_spent) if hours_spent else 1.0
    except ValueError:
        hours = 1.0

    if not member_name and member_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM team_members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        member_name = member['name'] if member else 'Unknown'
        conn.close()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO team_activities (project_id, team_member_id, member_name, task_description, activity_date, activity_time, hours_spent, logged_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, member_id, member_name, task_description, activity_date, activity_time, hours, logged_by))
    conn.commit()
    conn.close()

    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/delete-activity/<int:activity_id>/<int:project_id>', methods=['POST'])
def delete_activity(activity_id, project_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM team_activities WHERE id = ?", (activity_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/add-expense/<int:project_id>', methods=['POST'])
def add_expense(project_id):
    amount = request.form.get('amount', '0')
    category = request.form.get('category', 'Other')
    description = request.form.get('description', '').strip()
    expense_date = request.form.get('expense_date', '')
    vendor = request.form.get('vendor', '').strip()

    if not expense_date or not amount:
        return redirect(url_for('project_detail', project_id=project_id))

    try:
        amt = float(amount)
    except ValueError:
        return redirect(url_for('project_detail', project_id=project_id))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO project_expenses (project_id, amount, category, description, expense_date, vendor)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (project_id, amt, category, description, expense_date, vendor))
    conn.commit()
    conn.close()

    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/delete-expense/<int:expense_id>/<int:project_id>', methods=['POST'])
def delete_expense(expense_id, project_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM project_expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/api/data')
def api_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Fetch Freelance projects data for combo chart (individual + cumulative earnings)
    cursor.execute("SELECT title, earnings FROM projects WHERE type = 'Freelance' ORDER BY start_date ASC")
    freelance_rows = cursor.fetchall()

    freelance_labels = []
    freelance_earnings = []
    freelance_cumulative = []
    running_total = 0.0

    for row in freelance_rows:
        freelance_labels.append(row['title'])
        earnings = row['earnings']
        freelance_earnings.append(earnings)
        running_total += earnings
        freelance_cumulative.append(running_total)

    # 2. Fetch Project Types counts (Personal vs Freelance)
    cursor.execute("SELECT type, COUNT(*) as count FROM projects GROUP BY type")
    type_rows = cursor.fetchall()
    type_counts = {"Personal": 0, "Freelance": 0}
    for row in type_rows:
        type_counts[row['type']] = row['count']

    type_labels = list(type_counts.keys())
    type_values = list(type_counts.values())

    # 3. Fetch Timeline Schedule data (all projects, ordered chronologically by start date)
    cursor.execute("SELECT title, start_date, end_date, status, type FROM projects ORDER BY start_date ASC")
    timeline_rows = cursor.fetchall()
    timeline_data = []
    for row in timeline_rows:
        timeline_data.append({
            "title": row['title'],
            "start_date": row['start_date'],
            "end_date": row['end_date'],
            "status": row['status'],
            "type": row['type']
        })

    conn.close()

    return jsonify({
        "freelance_labels": freelance_labels,
        "freelance_earnings": freelance_earnings,
        "freelance_cumulative": freelance_cumulative,
        "type_labels": type_labels,
        "type_values": type_values,
        "timeline_projects": timeline_data
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
