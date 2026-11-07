from datetime import datetime
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask, abort, flash, redirect, render_template, request,
    send_from_directory, url_for
)
from flask_login import (
    LoginManager, UserMixin, current_user, login_required,
    login_user, logout_user
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, func, or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if not database_url:
    raise RuntimeError(
        "DATABASE_URL is missing. Copy your original .env file into the "
        "project root and restart the application."
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY is missing from your .env file.")

app.config["UPLOAD_FOLDER"] = str(Path(app.root_path) / "static" / "uploads")
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "info"


# ---------------------------------------------------------------------------
# Existing database models. Column names and table names are intentionally
# retained so this version can use the existing SocialNest database.
# ---------------------------------------------------------------------------

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


class Signup(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    phone = db.Column(db.String(10), unique=True)
    profileimage = db.Column(db.String(500))

    def get_id(self):
        return str(self.user_id)


class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    name = db.Column(db.String(100))
    title = db.Column(db.String(100))
    description = db.Column(db.String(500))
    image = db.Column(db.String(500))
    date = db.Column(db.String(100))
    time = db.Column(db.String(100))
    likes = db.Column(db.Integer, nullable=True, default=0)


class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    comment = db.Column(db.String(500))
    commentedBy = db.Column(db.String(100))
    commentedOn = db.Column(db.String(100))


class Friends(db.Model):
    friends_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)       # request sender
    requested_id = db.Column(db.Integer) # request recipient
    isAccepted = db.Column(db.String(10))


class Contact(db.Model):
    contact_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    description = db.Column(db.String(500))


class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        db.UniqueConstraint("user_id", "post_id", name="unique_like"),
    )


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(Signup, int(user_id))
    except (TypeError, ValueError):
        return None


# Create only missing tables. This does not delete existing rows.
with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def allowed_file(filename):
    return (
        bool(filename)
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def save_image(file_storage):
    """Save an upload with a unique name; return the stored basename."""
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError("Please upload a PNG, JPG, JPEG, GIF, or WEBP image.")

    original = secure_filename(file_storage.filename)
    extension = original.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    file_storage.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return filename


def normalize_upload_name(filename):
    """Support legacy DB values such as name.jpg, uploads/name.jpg,
    and static/uploads/name.jpg without exposing arbitrary file paths."""
    if not filename:
        return None
    normalized = str(filename).replace("\\", "/").strip()
    for prefix in ("static/uploads/", "uploads/"):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    return os.path.basename(normalized) or None


def post_like_count(post_id):
    return Like.query.filter_by(post_id=post_id).count()


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    safe_name = normalize_upload_name(filename)
    if not safe_name:
        abort(404)
    return send_from_directory(app.config["UPLOAD_FOLDER"], safe_name)


@app.context_processor
def inject_image_helpers():
    return {"upload_url": lambda value: (
        url_for("uploaded_file", filename=normalize_upload_name(value))
        if normalize_upload_name(value) else None
    )}


# ---------------------------------------------------------------------------
# Pages and authentication
# ---------------------------------------------------------------------------

@app.route("/")
@login_required
def index():
    data = Posts.query.order_by(Posts.post_id.desc()).all()
    liked_post_ids = {
        row.post_id for row in Like.query.filter_by(user_id=current_user.user_id).all()
    }
    like_counts = {post.post_id: post_like_count(post.post_id) for post in data}
    return render_template(
        "index.html", data=data, liked_post_ids=liked_post_ids,
        like_counts=like_counts
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("fname", "").strip()
        last_name = request.form.get("lname", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("pass1", "")
        confirm_password = request.form.get("pass2", "")

        if not all((first_name, last_name, email, phone, password)):
            flash("Please complete all required fields.", "warning")
            return redirect(url_for("signup"))
        if password != confirm_password:
            flash("Passwords do not match.", "warning")
            return redirect(url_for("signup"))
        if len(phone) != 10 or not phone.isdigit():
            flash("Phone number must be exactly 10 digits.", "warning")
            return redirect(url_for("signup"))
        if Signup.query.filter(func.lower(Signup.email) == email.lower()).first():
            flash("An account with this email already exists.", "warning")
            return redirect(url_for("signup"))
        if Signup.query.filter_by(phone=phone).first():
            flash("An account with this phone number already exists.", "warning")
            return redirect(url_for("signup"))

        user = Signup(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=generate_password_hash(password),
            phone=phone,
        )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("An account with these details already exists.", "warning")
            return redirect(url_for("signup"))

        flash("Your account has been created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("pass1", "")
        user = Signup.query.filter(
            func.lower(Signup.email) == email.lower()
        ).first()

        if user and user.password and check_password_hash(user.password, password):
            login_user(user)
            flash("Welcome back!", "success")
            return redirect(url_for("index"))

        flash("Invalid email or password. Please check your details.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        description = request.form.get("desc", "").strip()
        if not email or not description:
            flash("Please enter your email and message.", "warning")
        else:
            db.session.add(Contact(email=email, description=description))
            db.session.commit()
            flash("Thanks for reaching out. Your message has been received.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")


# ---------------------------------------------------------------------------
# Posts, likes, and comments
# ---------------------------------------------------------------------------

@app.route("/posts", methods=["GET", "POST"])
@login_required
def posts():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        image_file = request.files.get("image")

        if not title or not description:
            flash("Please add a title and description to your post.", "warning")
            return redirect(url_for("posts"))
        if len(title) > 100 or len(description) > 500:
            flash("Your title or description is too long.", "warning")
            return redirect(url_for("posts"))

        try:
            image_name = save_image(image_file) if image_file and image_file.filename else None
        except ValueError as error:
            flash(str(error), "warning")
            return redirect(url_for("posts"))

        now = datetime.now()
        post = Posts(
            email=current_user.email,
            name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip(),
            title=title,
            description=description,
            image=image_name,
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%I:%M %p"),
            likes=0,
        )
        db.session.add(post)
        db.session.commit()
        flash("Your post has been shared.", "success")
        return redirect(url_for("index"))

    return render_template("posts.html")


@app.route("/like/<int:id>", methods=["POST"])
@login_required
def like(id):
    post = db.session.get(Posts, id)
    if not post:
        abort(404)

    existing = Like.query.filter_by(
        user_id=current_user.user_id, post_id=id
    ).first()

    if existing:
        db.session.delete(existing)
        flash("Like removed.", "info")
    else:
        db.session.add(Like(user_id=current_user.user_id, post_id=id))
        flash("You liked this post.", "success")

    try:
        db.session.flush()
        post.likes = post_like_count(id)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Your like could not be saved. Please try again.", "warning")

    return redirect(request.referrer or url_for("index"))


@app.route("/comment/<int:id>", methods=["POST"])
@login_required
def comment(id):
    post = db.session.get(Posts, id)
    if not post:
        abort(404)

    comment_text = request.form.get("comment", "").strip()
    if not comment_text:
        flash("Please write a comment before submitting.", "warning")
    elif len(comment_text) > 500:
        flash("Comments must be 500 characters or fewer.", "warning")
    else:
        author = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip()
        new_comment = Comments(
            post_id=id,
            comment=comment_text,
            commentedBy=author,
            commentedOn=datetime.now().strftime("%b %d, %Y · %I:%M %p"),
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added.", "success")

    return redirect(request.referrer or url_for("index"))


@app.route("/viewcomment/<int:id>")
@login_required
def viewcomment(id):
    post = db.session.get(Posts, id)
    if not post:
        abort(404)
    comments = Comments.query.filter_by(post_id=id).order_by(Comments.comment_id.asc()).all()
    return render_template("comments.html", post=comments, post_item=post)


# ---------------------------------------------------------------------------
# Friend requests. Friends.user_id is the sender and requested_id is receiver.
# ---------------------------------------------------------------------------

@app.route("/connect", methods=["GET"])
@login_required
def connect():
    users = Signup.query.filter(Signup.user_id != current_user.user_id).order_by(
        Signup.first_name.asc()
    ).all()

    statuses = {}
    for user in users:
        relationship = Friends.query.filter(
            or_(
                and_(
                    Friends.user_id == current_user.user_id,
                    Friends.requested_id == user.user_id,
                ),
                and_(
                    Friends.user_id == user.user_id,
                    Friends.requested_id == current_user.user_id,
                ),
            )
        ).first()

        if relationship:
            if relationship.isAccepted == "True":
                statuses[user.user_id] = "connected"
            elif relationship.user_id == current_user.user_id:
                statuses[user.user_id] = "sent"
            else:
                statuses[user.user_id] = "received"
        else:
            statuses[user.user_id] = "none"

    return render_template("connect.html", users=users, statuses=statuses)


@app.route("/connectfriend/<int:user_id>", methods=["POST"])
@login_required
def connectFriends(user_id):
    if user_id == current_user.user_id:
        flash("You cannot send a friend request to yourself.", "warning")
        return redirect(url_for("connect"))

    target = db.session.get(Signup, user_id)
    if not target:
        abort(404)

    existing = Friends.query.filter(
        or_(
            and_(
                Friends.user_id == current_user.user_id,
                Friends.requested_id == user_id,
            ),
            and_(
                Friends.user_id == user_id,
                Friends.requested_id == current_user.user_id,
            ),
        )
    ).first()

    if existing:
        if existing.isAccepted == "True":
            flash("You are already connected.", "info")
        elif existing.user_id == user_id:
            flash("This person has already sent you a request. Accept it from your profile.", "info")
        else:
            flash("Your friend request is already pending.", "info")
        return redirect(url_for("connect"))

    db.session.add(Friends(
        user_id=current_user.user_id,
        requested_id=user_id,
        isAccepted="False",
    ))
    db.session.commit()
    flash(f"Friend request sent to {target.first_name}.", "success")
    return redirect(url_for("connect"))


@app.route("/accept/<int:requester_id>", methods=["POST"])
@login_required
def acceptfriendrequest(requester_id):
    friend_request = Friends.query.filter_by(
        user_id=requester_id,
        requested_id=current_user.user_id,
        isAccepted="False",
    ).first()

    if not friend_request:
        flash("That pending friend request could not be found.", "warning")
    else:
        friend_request.isAccepted = "True"
        db.session.commit()
        flash("Friend request accepted.", "success")

    return redirect(url_for("profile"))


@app.route("/remove/<int:user_id>", methods=["POST"])
@login_required
def remove(user_id):
    relationship = Friends.query.filter(
        or_(
            and_(
                Friends.user_id == current_user.user_id,
                Friends.requested_id == user_id,
                Friends.isAccepted == "False",
            ),
            and_(
                Friends.user_id == user_id,
                Friends.requested_id == current_user.user_id,
                Friends.isAccepted == "False",
            ),
            and_(
                Friends.user_id == current_user.user_id,
                Friends.requested_id == user_id,
                Friends.isAccepted == "True",
            ),
            and_(
                Friends.user_id == user_id,
                Friends.requested_id == current_user.user_id,
                Friends.isAccepted == "True",
            ),
        )
    ).first()

    if relationship:
        db.session.delete(relationship)
        db.session.commit()
        flash("The request or connection has been removed.", "success")
    else:
        flash("No matching request or connection was found.", "info")

    return redirect(request.referrer or url_for("connect"))


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@app.route("/profile")
@login_required
def profile():
    userdata = db.session.get(Signup, current_user.user_id)

    incoming = Friends.query.filter_by(
        requested_id=current_user.user_id,
        isAccepted="False",
    ).all()
    incoming_users = [
        db.session.get(Signup, relation.user_id)
        for relation in incoming
    ]
    incoming_users = [user for user in incoming_users if user is not None]

    getallmypost = Posts.query.filter_by(email=current_user.email).order_by(
        Posts.post_id.desc()
    ).all()

    liked_post_ids = {
        row.post_id for row in Like.query.filter_by(user_id=current_user.user_id).all()
    }
    like_counts = {post.post_id: post_like_count(post.post_id) for post in getallmypost}

    return render_template(
        "profile.html",
        userdata=userdata,
        myids=incoming_users,
        getallmypost=getallmypost,
        liked_post_ids=liked_post_ids,
        like_counts=like_counts,
    )


@app.route("/editprofile/<int:id>", methods=["GET"])
@login_required
def editprofile(id):
    if id != current_user.user_id:
        abort(403)
    return render_template("editprofile.html", userdata=current_user)


@app.route("/updateprofile/<int:id>", methods=["POST"])
@login_required
def updateprofile(id):
    if id != current_user.user_id:
        abort(403)

    userdata = db.session.get(Signup, current_user.user_id)
    first_name = request.form.get("fname", "").strip()
    last_name = request.form.get("lname", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    image_file = request.files.get("profileimage")

    if not first_name or not last_name or not email:
        flash("Please complete your name and email.", "warning")
        return redirect(url_for("editprofile", id=id))
    if len(phone) != 10 or not phone.isdigit():
        flash("Please enter a valid 10-digit phone number.", "warning")
        return redirect(url_for("editprofile", id=id))

    email_owner = Signup.query.filter(
        func.lower(Signup.email) == email.lower(),
        Signup.user_id != current_user.user_id,
    ).first()
    phone_owner = Signup.query.filter(
        Signup.phone == phone,
        Signup.user_id != current_user.user_id,
    ).first()
    if email_owner or phone_owner:
        flash("That email or phone number is already used by another account.", "warning")
        return redirect(url_for("editprofile", id=id))

    try:
        new_image = save_image(image_file) if image_file and image_file.filename else None
    except ValueError as error:
        flash(str(error), "warning")
        return redirect(url_for("editprofile", id=id))

    previous_email = userdata.email
    userdata.first_name = first_name
    userdata.last_name = last_name
    userdata.email = email
    userdata.phone = phone
    if previous_email and previous_email != email:
        Posts.query.filter_by(email=previous_email).update(
            {Posts.email: email}, synchronize_session=False
        )
    if new_image:
        userdata.profileimage = new_image

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Your profile could not be updated because those details are already in use.", "warning")
        return redirect(url_for("editprofile", id=id))

    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
