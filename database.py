import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def dict_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def init_db(force_recreate=False):
    conn = get_db_connection()
    cursor = dict_cursor(conn)

    if force_recreate:
        cursor.execute("DROP TABLE IF EXISTS project_expenses CASCADE")
        cursor.execute("DROP TABLE IF EXISTS team_activities CASCADE")
        cursor.execute("DROP TABLE IF EXISTS team_members CASCADE")
        cursor.execute("DROP TABLE IF EXISTS projects CASCADE")
        conn.commit()
        print("Dropped existing tables.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('Personal', 'Freelance')),
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            earnings REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'Not Started' CHECK(status IN ('Not Started', 'In Progress', 'Completed')),
            tag TEXT NOT NULL DEFAULT 'Other' CHECK(tag IN ('Web Dev', 'Design', 'Writing', 'Consulting', 'Marketing', 'Other'))
        )
    ''')
    conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id SERIAL PRIMARY KEY,
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'Developer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_activities (
            id SERIAL PRIMARY KEY,
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            team_member_id INTEGER REFERENCES team_members(id) ON DELETE SET NULL,
            member_name TEXT NOT NULL,
            task_description TEXT NOT NULL,
            activity_date TEXT NOT NULL,
            activity_time TEXT,
            hours_spent REAL DEFAULT 1.0,
            logged_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_expenses (
            id SERIAL PRIMARY KEY,
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            amount REAL NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('Tools', 'Hosting', 'Software', 'Hardware', 'Services', 'Other')),
            description TEXT,
            expense_date TEXT NOT NULL,
            vendor TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    cursor.execute("SELECT COUNT(*) as count FROM projects")
    count = cursor.fetchone()['count']
    if count == 0:
        sample_projects = [
            ("E-Commerce Web App", "Freelance", "2026-01-10", "2026-03-15", 4500.0, "Completed", "Web Dev"),
            ("Client Portfolio Website", "Freelance", "2026-04-01", "2026-05-20", 1800.0, "Completed", "Web Dev"),
            ("Mobile Booking App Integration", "Freelance", "2026-05-10", "2026-06-30", 3500.0, "In Progress", "Web Dev"),
            ("Marketing Campaign Page", "Freelance", "2026-06-01", "2026-06-15", 1200.0, "Not Started", "Marketing"),
            ("Portfolio redesign", "Personal", "2026-02-15", "2026-03-10", 0.0, "Completed", "Design"),
            ("Smart Recipe Finder API", "Personal", "2026-05-01", "2026-06-15", 0.0, "In Progress", "Web Dev"),
            ("Technical Writing Guide", "Personal", "2026-05-12", "2026-05-28", 0.0, "Completed", "Writing"),
            ("Antigravity Dashboard Extension", "Personal", "2026-05-20", "2026-07-01", 0.0, "In Progress", "Consulting"),
            ("Fitness Tracker App Mockup", "Personal", "2026-07-01", "2026-08-15", 0.0, "Not Started", "Design")
        ]
        cursor.executemany('''
            INSERT INTO projects (title, type, start_date, end_date, earnings, status, tag)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', sample_projects)
        conn.commit()
        print("Database seeded with sample projects.")
    else:
        print("Database already has data. Seeding skipped.")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    init_db(force_recreate=True)
