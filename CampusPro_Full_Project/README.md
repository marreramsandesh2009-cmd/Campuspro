# CampusPro — Final-Year Project Management System

A responsive academic project workspace built with **HTML, CSS, Bootstrap Icons, JavaScript, Python Flask and MySQL**. SQLite is included as a convenient local testing option.

## Included features
- Professional responsive landing page and authentication screens
- Role-based Student, Faculty and Admin dashboards
- Student registration (public registration creates Student accounts only)
- Project submission with title, abstract, technology stack, GitHub/demo URL and optional file attachment
- Faculty/Admin project review with status and feedback
- Status workflow: Submitted → Under Review / Approved / Needs Changes
- Student notifications when a review is saved
- Project search and status filtering
- Admin overview and account activation/deactivation
- Responsive navigation for mobile, tablet and desktop
- Password hashing and role-protected routes

## Requirements
- Python 3.10 or newer
- MySQL 8+ (recommended for the final deployment) or SQLite for quick testing
- Windows, macOS or Linux

## Windows setup (XAMPP / MySQL)
1. Extract `CampusPro_Full_Project.zip`.
2. Open the extracted folder in VS Code.
3. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```
4. Install packages:
   ```powershell
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env`.
6. In phpMyAdmin or MySQL, create the database:
   ```sql
   CREATE DATABASE campuspro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
7. Edit `.env` and set your database connection. Example for XAMPP with an empty root password:
   ```env
   SECRET_KEY=replace-with-a-long-random-value
   DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/campuspro?charset=utf8mb4
   ```
   If your MySQL root user has a password, put it after `root:`. If you want to test without MySQL first, keep `DATABASE_URL=sqlite:///campuspro.db`.
8. Create the tables:
   ```powershell
   flask --app app init-db
   ```
9. Create a Faculty account and an Admin account (run the command separately for each):
   ```powershell
   flask --app app create-user
   ```
   Enter role as `faculty` or `admin`. The password is entered securely in the terminal.
10. Start the app:
   ```powershell
   flask --app app run --debug
   ```
11. Open `http://127.0.0.1:5000`.

## First use
- Register a normal Student account from the website.
- Sign in as Faculty to review student submissions.
- Sign in as Admin to see all users/projects and enable or disable accounts.
- Admin and Faculty accounts must be created with the `create-user` terminal command; they cannot be self-selected from public registration.

## MySQL database
A reference SQL schema is provided in `database/schema.sql`. In normal use, Flask-SQLAlchemy creates the same tables with `flask --app app init-db`.

## Project structure
```text
CampusPro_Full_Project/
├── app.py
├── config.py
├── extensions.py
├── models.py
├── requirements.txt
├── .env.example
├── README.md
├── database/schema.sql
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── auth_base.html
│   ├── login.html
│   ├── register.html
│   ├── student_dashboard.html
│   ├── faculty_dashboard.html
│   ├── admin_dashboard.html
│   ├── projects.html
│   ├── project_form.html
│   ├── project_detail.html
│   ├── notifications.html
│   ├── error.html
│   └── _macros.html
└── static/
    ├── css/style.css
    ├── js/app.js
    └── uploads/
```

## Notes before public deployment
This is a functional academic project baseline, not a hardened public production service. Before internet deployment, add CSRF protection, email verification, password reset, rate limiting, audit logging, stricter upload scanning/validation, HTTPS and production server configuration. Keep `.env` private and change `SECRET_KEY`.


## Faculty workflow

Administrators can create faculty accounts from **Admin dashboard → Faculty management**. Add the faculty member's name, email, department and a temporary password (minimum 8 characters). Faculty members sign in through the normal login page and are directed to their faculty dashboard.

The faculty dashboard lists all student project submissions, with submitted and under-review projects shown first. Open a project to inspect its abstract, technology stack, project link and attachment; faculty can then set it to **Under Review**, **Approved** or **Needs Changes** and leave feedback. The student receives an in-app notification when a review is saved.
