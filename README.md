# SocialNest

SocialNest is a Flask-based social networking web application where users can create an account, share posts, interact with other users, and build connections. It provides a simple community space for sharing updates and connecting with friends.

🌐 **Live Demo:** https://socialnest-7eim.onrender.com

## Features

- **User authentication** — sign up, log in, and log out.
- **Password security** — passwords are stored using Werkzeug password hashing.
- **Create posts** — publish posts with a title, description, and optional image.
- **Social interactions** — like posts and add/view comments.
- **Friend connections** — discover users, send friend requests, accept requests, and remove connections.
- **User profiles** — view profile information and update profile details or profile pictures.
- **Contact form** — submit a message through the contact page.
- **Responsive interface** — templates styled with Bootstrap and custom SocialNest design system.

## UI Refresh

The interface uses a responsive SocialNest design system with a violet/lavender palette, clean typography, sticky navigation, a refreshed landing hero, community feed cards, modern forms, member discovery cards, and updated profile sections. The existing Flask routes and Jinja form field names are retained.

## Tech Stack

| Area | Technology |
|---|---|
| Backend | Python, Flask |
| Database layer | Flask-SQLAlchemy, SQLAlchemy |
| Authentication | Flask-Login |
| Password hashing | Werkzeug |
| Templates | Jinja2, HTML |
| Styling and UI | Bootstrap, CSS, Bootstrap Icons, AOS |
| Database drivers | PyMySQL, psycopg2-binary |
| Production server | Gunicorn |

## Project Structure

```text
socialNest/
├── app.py                  # Flask application, routes, and database models
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python runtime version
├── Procfile                # Gunicorn startup command for deployment
├── .env                    # Local environment variables (create this yourself)
├── templates/              # Jinja2 HTML templates
│   ├── about.html
│   ├── auth.html
│   ├── base.html
│   ├── comments.html
│   ├── connect.html
│   ├── contact.html
│   ├── editprofile.html
│   ├── index.html
│   ├── login.html
│   ├── messages.html
│   ├── posts.html
│   ├── profile.html
│   └── signup.html
└── static/
    └── assets/
        ├── css/
        ├── img/
        ├── js/
        └── vendor/         # Front-end libraries and plugins
```

Uploaded post and profile images are stored under `static/uploads/` (the application uses this upload directory).

## Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd socialNest
```

Replace `<YOUR_REPOSITORY_URL>` with the URL of your Git repository.

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root. Add your database connection string and a strong secret key:

```env
DATABASE_URL=your_database_connection_url
SECRET_KEY=replace_with_a_long_random_secret
```

`DATABASE_URL` must be a SQLAlchemy-compatible database URL for the database you have configured. For example, a local MySQL connection can use this general format:

```env
DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@HOST:3306/DATABASE_NAME
```

Use the appropriate URL format and driver for your database. Do not commit `.env` or publish database credentials or secret keys.

### 5. Prepare the upload directory

```bash
mkdir -p static/uploads
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force static/uploads
```

Ensure the application has permission to write to this directory.

### 6. Run the application

```bash
python app.py
```

Open the local address printed by Flask in your browser (commonly `http://127.0.0.1:5000/`). The application creates its configured SQLAlchemy tables when it starts, provided the database connection is valid and the database is reachable.

## Running with Gunicorn

The included `Procfile` defines the production start command:

```bash
gunicorn app:app
```

For a local Gunicorn test, run:

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

Then visit `http://127.0.0.1:8000/`.

## Main Application Routes

| Route | Purpose |
|---|---|
| `/` | Main feed / home page |
| `/about` | About SocialNest |
| `/signup` | Create an account |
| `/login` | Log in |
| `/logout` | Log out |
| `/posts` | Create a post |
| `/like/<id>` | Like a post |
| `/comment/<id>` | Add a comment to a post |
| `/viewcomment/<id>` | View comments for a post |
| `/connect` | Discover users and manage connections |
| `/profile` | View your profile and friend requests |
| `/editprofile/<id>` | Open the profile editing page |
| `/updateprofile/<id>` | Update profile information |
| `/contact` | Submit a contact message |

Some actions require an authenticated user. The application may redirect unauthenticated visitors to the login page.

## Database Models

The application defines SQLAlchemy models for the main data entities:

- `Signup` — registered user information and authentication identity.
- `Posts` — post content, image path, author details, timestamp, and like count.
- `Comments` — comments associated with posts.
- `Friends` — friend-request and connection records.
- `Like` — individual user/post likes, with a uniqueness constraint to prevent duplicate like records.
- `Contact` — contact form submissions.

## Upload Notes

- The application allows image extensions `png`, `jpg`, `jpeg`, and `gif`.
- The configured maximum upload size is 16 MB.
- Uploaded files are saved in `static/uploads/`.
- For a production deployment, consider using managed object storage for uploads and validating file content in addition to checking extensions.

## Security and Production Checklist

Before deploying publicly:

- Set a unique, strong `SECRET_KEY` and keep it private.
- Keep `.env` out of version control; never share real credentials.
- Use HTTPS in production.
- Review authorization checks on routes that modify posts, comments, likes, friendships, and profiles.
- Add CSRF protection to forms and use POST requests for state-changing actions.
- Validate uploaded file content and generate collision-resistant filenames.
- Configure database backups and use migrations for future schema changes.
- Review error handling, logging, and production database settings.

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Make and test your changes.
4. Commit your work: `git commit -m "Add your feature"`.
5. Push the branch and open a pull request.

## License

No license information was included with the project files. Add a `LICENSE` file if you intend to distribute or accept contributions under a specific open-source license.
