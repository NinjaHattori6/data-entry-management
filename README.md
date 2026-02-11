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






