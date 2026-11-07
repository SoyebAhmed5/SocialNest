# SocialNest

SocialNest is a Flask-based social networking application where members can create posts, share images, like and comment on posts, manage their profile, discover members, and send friend requests.

🌐 **Live Demo:** https://socialnest-7eim.onrender.com

## Tech stack

- Python and Flask
- Flask-Login for session-based authentication
- Flask-SQLAlchemy / SQLAlchemy
- PostgreSQL (via `psycopg2-binary`)
- Jinja2 templates, Bootstrap, Bootstrap Icons, and custom responsive CSS

## Features

- User registration and login
- Community feed and post creation
- Optional image uploads for posts
- Profile details and profile picture updates
- Like / unlike posts
- Post comments and conversation view
- Member discovery and friend requests
- Responsive navigation and modern UI

## Project structure

```text
socialNest/
├── app.py
├── .env.example
├── .gitignore
├── requirements.txt
├── Procfile
├── runtime.txt
├── templates/
└── static/
    ├── assets/
    │   ├── css/
    │   ├── js/
    │   ├── img/
    │   └── vendor/
    └── uploads/
        └── .gitkeep
```

## Run locally

### 1. Create and activate a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and set your own database URL and secret key:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/socialnest
SECRET_KEY=replace-with-a-long-random-secret
```

**If you are upgrading an existing SocialNest installation:** use the same `DATABASE_URL` that points to your existing database. Do not create a new database if you want to keep your existing accounts, posts, comments, likes, and friend requests. Keep your existing `SECRET_KEY` when restoring the old installation.

Never commit `.env` to GitHub.

### 4. Restore existing uploaded images when upgrading

The database stores image filenames, while the actual image files are stored on disk in `static/uploads/`.

If you have an existing local SocialNest project, copy its complete:

```text
old-socialNest/static/uploads/
```

folder into the updated project at:

```text
updated-socialNest/static/uploads/
```

Keep the filenames unchanged. This is important because existing profile and post records refer to those filenames. The source ZIP used to prepare this update did not contain the previously uploaded user images, so those files must be copied from your old local project or restored from your own backup.

The app now serves legacy image names as well as newly generated unique filenames. If an old image file is missing, the profile UI shows a fallback image and missing post images are hidden rather than displaying a broken-image icon.

### 5. Start the application

```bash
python app.py
```

Open the local URL printed by Flask (normally `http://127.0.0.1:5000`).

## Database compatibility

This update intentionally retains the existing SQLAlchemy model/table names and column names. It does not drop tables or delete existing records. `db.create_all()` only creates tables that are missing; it is not a database reset or a full schema migration system.

Back up your database before deploying any future schema changes.

## Image uploads

- Accepted extensions: PNG, JPG, JPEG, GIF, WEBP
- Maximum request size: 16 MB
- Uploaded files are stored in `static/uploads/` with unique generated names to avoid filename collisions.
- For production deployments, use persistent disk or object storage. Temporary application filesystems may be cleared during redeploys.

## Security notes

- Keep `.env` private and rotate any credentials that were previously committed or shared.
- Do not print passwords or secrets in logs.
- Use HTTPS in production.
- Configure CSRF protection before exposing write forms publicly.
- Use a production WSGI server (for example, Gunicorn) and disable Flask debug mode in production.

## Important behavior changes in this update

- Like / unlike actions use POST and update the count from the likes table.
- Comment authors are taken from the authenticated session rather than hidden form fields.
- Friend requests are directional: the sender is stored in `Friends.user_id`, and the recipient in `Friends.requested_id`.
- Incoming requests are shown on the recipient's profile; only the recipient can accept them.
- Profile editing is restricted to the logged-in account.
- The About link is visible in the navigation for signed-in and signed-out visitors.

## Troubleshooting

### Existing account cannot log in

1. Confirm the updated project has the correct `.env` file.
2. Confirm `DATABASE_URL` points to the original database.
3. Confirm the original user row still exists in that database.
4. Do not reset the database or delete tables.

### Profile or post images are missing

1. Confirm the old `static/uploads/` folder was copied into the updated project.
2. Keep existing filenames unchanged.
3. Check that the Flask process can read the files.

### PostgreSQL connection errors

- Verify the database is running and reachable.
- Check the host, port, database name, username, and password in `DATABASE_URL`.
- Ensure `psycopg2-binary` is installed.

## License

Add your preferred license before publishing this project publicly.
