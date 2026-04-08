\# ðŸ§® Data Vault



A complete \*\*Flask-based web application\*\* for managing and analyzing data entries efficiently.

Includes user authentication, admin control, PDF/Excel/CSV exports, and password recovery using OTP verification.



---



\## ðŸš€ Features



\### ðŸ‘¤ User Features

\- Register, Login, Logout

\- Create, view, edit, and delete data entries

\- Export data in \*\*CSV\*\*, \*\*Excel\*\*, and \*\*PDF\*\* formats

\- Profile management and password change

\- Dark mode UI for better accessibility



\### ðŸ§‘â€ðŸ’¼ Admin Features

\- View all registered users and their entry counts

\- Promote users to admin

\- Delete users (and their data)

\- View activity statistics



\### ðŸ” Security

\- Passwords hashed using `werkzeug.security`

\- Session-based authentication

\- OTP-based password reset (demo implementation)

\- SQLite database validation and safe CRUD operations



---



\## ðŸ§° Tech Stack



| Component | Technology |

|------------|-------------|

| \*\*Backend\*\* | Flask (Python) |

| \*\*Frontend\*\* | HTML5, CSS3, Bootstrap 5 |

| \*\*Database\*\* | SQLite |

| \*\*Libraries\*\* | Pandas, ReportLab, OpenPyXL, Gunicorn |

| \*\*Export Formats\*\* | CSV, Excel, PDF |



---



\## âš™ï¸ Project Setup (Local)



\### 1ï¸âƒ£ Clone the Repository

```bash

git clone https://github.com/<your-username>/data-entry-management.git

cd data-entry-management







---

## Deploying on Render

### Recommended Environment Variables

Set these in **Render → Service → Environment**:

| Variable | Description | Example |
|---|---|---|
| `DB_PATH` | Path to the SQLite database file. Use a **Render persistent disk** mount point to survive redeploys. | `/data/oncology_system.db` |
| `DEFAULT_ADMIN_PASSWORD` | Password for the default `admin` account created on first run. **Change this from the default!** | `MyStr0ngP@ssw0rd` |
| `SECRET_KEY` | Flask session secret key. Set a long random string. | `your-secret-key-here` |

### Render Settings

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app_new:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
- **Pre-Deploy Command:** *(leave empty — DB is initialised safely on startup)*

### Persistent Storage (important for SQLite)

Render's default filesystem is **ephemeral** — it is wiped on every redeploy.
To keep your data across deploys:

1. Add a **Persistent Disk** in Render (Disk → Mount Path e.g. `/data`).
2. Set the `DB_PATH` environment variable to a path on that disk, e.g. `/data/oncology_system.db`.

Without a persistent disk, SQLite data will be lost every time the service redeploys.

### Security Notes

- The database initialization (`init_database()`) is **idempotent**: it will never delete existing data and is safe to run on every startup.
- The default admin user is created **only once** (on first run). Subsequent restarts will not reset the admin password.
- Admin credentials are **not printed to logs**. A one-line notice is logged when the admin user is first created.
- Set `DEFAULT_ADMIN_PASSWORD` to a strong password before your first deploy, then log in and change it immediately.
