# FiXiT — Home Maintenance Manager

FiXiT is a clean, easy-to-understand web application built with Python, Flask, and PostgreSQL for tracking household assets/appliances and their maintenance schedules.

---

## Features

- **Dashboard**: Overview of total assets, overdue maintenance, due soon, and recently serviced equipment.
- **Assets Directory**: List of all registered household assets with visual status badges.
- **Asset Details & Service History**: View purchase info, next scheduled service date, and past service logs.
- **Add Asset**: Simple form to register new appliances with service intervals.
- **Log Maintenance Record**: Add service dates, service provider details, costs, and notes for any asset.
- **Automatic Status Calculation**: Backend Python logic determines if an asset is *Overdue*, *Due Soon*, or *Up to Date*.

---

## Tech Stack

- **Backend**: Python 3, Flask
- **Database & ORM**: PostgreSQL, Flask-SQLAlchemy
- **Templating**: Jinja2
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Production Server**: Gunicorn

---

## Project Structure

```text
fixit/
├── app/
│   ├── __init__.py           # Flask app factory and extension setup
│   ├── models.py             # SQLAlchemy models (Asset, MaintenanceRecord)
│   ├── routes.py             # Route handlers (Dashboard, Assets, Forms)
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html         # Master layout with navbar and footer
│   │   ├── index.html        # Dashboard
│   │   ├── assets.html       # Asset list page
│   │   ├── asset_detail.html # Asset details and maintenance table
│   │   ├── add_asset.html    # Add asset form
│   │   └── add_maintenance.html # Add maintenance record form
│   └── static/
│       └── css/
│           └── style.css     # Clean styling enhancements for Bootstrap
├── config.py                 # Configuration loader (reads .env)
├── run.py                    # Application entry point & DB table creator
├── seed.py                   # Simple sample data script
├── requirements.txt          # Minimal required dependencies
├── Procfile                  # Start command for Render deployment
├── .env.example              # Sample environment variables
└── README.md
```

---

## Local Setup Instructions

### 1. Clone the repository & navigate to directory
```bash
cd fixit
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create your PostgreSQL database
In PostgreSQL (pgAdmin or psql):
```sql
CREATE DATABASE fixit_db;
```

### 5. Configure environment variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update `.env` with your PostgreSQL username and password:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/fixit_db
SECRET_KEY=my-super-secret-key
```

### 6. Run the application
```bash
python run.py
```
*(Tables are automatically created on application start).*

Open your browser at: **http://127.0.0.1:5000**

---

## Populating Sample Demo Data (Optional)

To insert a few realistic demo assets (Overdue, Due Soon, and Up to Date) with maintenance records:

```bash
python seed.py
```

---

## Deployment on Render

1. **Create a PostgreSQL Database on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com) &rarr; Click **New +** &rarr; **PostgreSQL**.
   - Copy the **Internal Database URL** (or External Database URL).

2. **Create a Web Service on Render**:
   - Click **New +** &rarr; **Web Service** &rarr; Connect your repository.
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`

3. **Configure Environment Variables in Render**:
   - Add `DATABASE_URL`: *(paste the PostgreSQL URL from step 1)*
   - Add `SECRET_KEY`: `your-secure-random-secret-key`

4. **Deploy**:
   - Click **Deploy Web Service**. Render will install dependencies and start the app with Gunicorn.

---

## Understanding the Architecture (Interview Cheatsheet)

- **Application Factory (`create_app`)**: Initializes Flask, loads configuration, and registers SQLAlchemy and blueprints.
- **SQLAlchemy Models (`models.py`)**: `Asset` has a `1-to-many` relationship with `MaintenanceRecord` (`db.relationship(..., backref='asset')`).
- **Status Calculation**: Handled as a Python property (`@property def maintenance_status`) on the `Asset` model by comparing `last_maintenance_date + interval` with `date.today()`.
- **Server-Side Rendering**: Flask routes query the database and pass Python objects into Jinja2 templates via `render_template()`.
- **Form Handling**: Routes validate incoming `POST` requests, insert rows using `db.session.add()` and `db.session.commit()`, and redirect with feedback using Flask's `flash()`.
