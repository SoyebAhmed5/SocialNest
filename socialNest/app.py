from flask import Flask, redirect,render_template, request, url_for
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_manager, UserMixin, LoginManager, login_required, logout_user, current_user, logout_user, LoginManager
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_login import current_user
from dotenv import load_dotenv

load_dotenv()

# import pymysql
# pymysql.install_as_MySQLdb()


local_server = True
app=Flask(__name__)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
# db connection


# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/socialmedia'




app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

app.secret_key = os.getenv("SECRET_KEY")


db = SQLAlchemy(app)




# Configuration for handling files
app.config['UPLOAD_FOLDER']='static/uploads/'
app.config['ALLOWED_EXTENSIONS']={'png','jpg','jpeg','gif'}
app.config['MAX_CONTENT_LENGTH']=16*1024*1024 #16mb max upload size



@login_manager.user_loader
def load_user(user_id):
    return Signup.query.get(int(user_id))

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

# initializing signup model
class Signup(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(255))
    phone = db.Column(db.String(10),unique=True)
    profileimage = db.Column(db.String(500))
    
    def get_id(self):
        return self.user_id
    
# initializing posts model    
class Posts(db.Model):
    post_id= db.Column(db.Integer, primary_key=True)
    email= db.Column(db.String(50))
    name= db.Column(db.String(100))
    title= db.Column(db.String(100))
    description= db.Column(db.String(500))
    image= db.Column(db.String(500))
    date= db.Column(db.String(100))
    time= db.Column(db.String(100))
    likes= db.Column(db.Integer,nullable=True,default=0)


# Initializing the Comments Model
class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    comment = db.Column(db.String(500))
    commentedBy = db.Column(db.String(100))
    commentedOn= db.Column(db.String(100))


class Friends(db.Model):
    friends_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    requested_id = db.Column(db.Integer)
    isAccepted = db.Column(db.String(10))

class Contact(db.Model):
    contact_id = db.Column(db.Integer, primary_key=True)
    email= db.Column(db.String(100))
    description= db.Column(db.String(500))
   
   
class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_like'),
    ) 
    
    
# TEMP
with app.app_context():
    db.create_all()

    
@app.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    data=Posts.query.all()
    return render_template("index.html",data=data)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method=='POST':
        firstName=request.form.get("fname")
        lastName=request.form.get("lname")
        email=request.form.get("email")
        phoneNumber=request.form.get("phone","").strip()
        password=request.form.get("pass1")
        confirmPassword=request.form.get("pass2")
        print(firstName,lastName,email,phoneNumber,password,confirmPassword)
        if password!=confirmPassword:
            flash("Passwords do not match","warning")
            return redirect(url_for('signup'))
        
        fetchemail=Signup.query.filter_by(email=email).first()
        fetchphone=Signup.query.filter_by(phone=phoneNumber).first()
        if fetchemail or fetchphone:
            flash("User already exists","warning")
            return redirect(url_for('signup'))
        
        if len(phoneNumber) != 10 or not phoneNumber.isdigit():
            flash("Phone number must be exactly 10 digits", "warning")
            return redirect(url_for("signup"))
                    
        gen_pass=generate_password_hash(password)    
        new_user = Signup(
                            first_name=firstName,
                            last_name=lastName,
                            email=email,
                            password=gen_pass,
                            phone=phoneNumber
                        )
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful !.", "success")
        return redirect(url_for("login"))
            
    return render_template("signup.html")


@app.route("/contact",methods=['GET','POST'])
def contact():
    if request.method=='POST':
        email=request.form.get("email")
        desc=request.form.get("desc")
        query = Contact(email=email,description=desc)
        db.session.add(query)
        db.session.commit()
        flash("We will get back to you soon")
        return render_template("contact.html") 
    return render_template("contact.html") 


@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get("email")
        password=request.form.get("pass1")
        user = Signup.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful !.","success")
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password","danger")
            return redirect(url_for('login'))
    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Success","primary")
    return redirect(url_for('login'))


@app.route("/test/")
def test():
    try:
        sql_query = "select * from test"
        with db.engine.begin() as conn:
            response = conn.exec_driver_sql(sql_query).all()
            print(response)
            return "Database is connected"
    except Exception as e:
        return f"Database is not Connected, {e}"
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
 
 

    
@app.route("/posts",methods=['GET','POST'])
def posts():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method=="POST":
        email=request.form['email']
        name=request.form['name']
        title=request.form['title']
        description=request.form['description']
        file=request.files['image']
        date=datetime.now()
        datee=date.date()
        time=date.time()
        
        if file and allowed_file(file.filename):
            # save the file in the upload folder
            filename=secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            
            # write the query to save in db
            query=Posts(email=email,name=name,title=title,description=description,image=file.filename,date=datee,time=time,)
            db.session.add(query)
            db.session.commit()
            flash("Post is Uploaded","info")
            return redirect(url_for('index'))
        else:
            flash("Please use 'png', 'jpg', 'jpeg', 'gif' file format","warning")
        
    
    return render_template("posts.html")
    
# Logic for Likes
@app.route('/like/<int:id>',methods=['POST','GET'])
@login_required
def like(id):
    post = Posts.query.filter_by(post_id=id).first()

    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("index"))

    # Check if the current user has already liked this post
    existing_like = Like.query.filter_by(
        user_id=current_user.user_id,
        post_id=id
    ).first()

    if existing_like:
        flash("You already liked this post.", "info")
        return redirect(url_for("index"))

    # Save the user's like
    like = Like(
        user_id=current_user.user_id,
        post_id=id
    )

    db.session.add(like)

    post.likes += 1

    db.session.commit()

    flash("Post liked!", "success")
    return redirect(url_for("index"))

@app.route('/comment/<int:id>',methods=['GET','POST'])
def comment(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method == 'POST':
        comment = request.form['comment']
        commentedBy = request.form['commented']
        commentedOn = datetime.now().strftime("%I:%M %p")
        query = Comments(post_id=id, comment=comment, commentedBy=commentedBy, commentedOn=commentedOn)
        db.session.add(query)
        db.session.commit()
        flash("Comment added successfully","success")
    return redirect(url_for('index'))


@app.route('/viewcomment/<int:id>',methods=['GET','POST'])
def viewcomment(id):
    post = Comments.query.filter_by(post_id=id).all()
    return render_template("comments.html", post=post)


@app.route('/connect',methods=['GET','POST'])
def connect():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    users = Signup.query.filter(Signup.user_id != current_user.user_id).all()
    return render_template("connect.html",users=users)


@app.route("/connectfriend/<path:ids>", methods=['GET'])
def connectFriends(ids):
    print(ids)
    data = ids.split("/")
    print(data)
    users = Signup.query.all()
    d1 = Friends.query.filter_by(user_id=data[1]).first()
    d2 = Friends.query.filter_by(requested_id=data[0]).first()
    if d1 or d2:
        flash("Friend request already sent","primary")
        return render_template("connect.html",users=users)
    query = Friends(user_id=data[1], requested_id=data[0], isAccepted="False")
    db.session.add(query)
    db.session.commit()
    flash("Friend request sent successfully","success")
    return render_template("connect.html",users=users)


@app.route("/remove/<path:ids>", methods=['GET'])
def remove(ids):
    print(ids)
    data = ids.split("/")
    print(data)
    users = Signup.query.all()
    d1 = Friends.query.filter_by(user_id=data[1]).first()
    d2 = Friends.query.filter_by(requested_id=data[0]).first()
    if d1 or d2:
        friend_request = Friends.query.filter_by(user_id=data[1],requested_id=data[0]).first()
        if friend_request:
            db.session.delete(friend_request)
            db.session.commit()
        flash("Request Cancelled", "success")
        return render_template("connect.html", users=users)
     
     
@app.route("/profile",methods=['GET','POST'])
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    userdata = Signup.query.filter_by(email=current_user.email).first()
    friends = Friends.query.filter_by(user_id=current_user.user_id).all()
    getallmypost = Posts.query.filter_by(email=current_user.email).all()
    myids = []
    for i in friends:
        if i.isAccepted == "False":
            signupdata = Signup.query.filter_by(user_id=i.requested_id).first()
            myids.append(signupdata)
    return render_template("profile.html",userdata=userdata,myids=myids,getallmypost=getallmypost)

@app.route("/editprofile/<int:id>",methods=["GET",'POST'])
def editprofile(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    userdata = Signup.query.filter_by(user_id=id).first()
    return render_template("editprofile.html",userdata=userdata)

@app.route("/updateprofile/<int:id>", methods=["GET", "POST"])
def updateprofile(id):
    userdata = Signup.query.filter_by(email=current_user.email).first()

    if request.method == "POST":
        firstName = request.form.get("fname", "").strip()
        lastName = request.form.get("lname", "").strip()
        email = request.form.get("email", "").strip()
        phoneNumber = request.form.get("phone", "").strip()
        file = request.files.get("profileimage")

        if len(phoneNumber) != 10 or not phoneNumber.isdigit():
            flash("Please enter a 10 digit number", "warning")
            return redirect(url_for("profile"))

        # Update basic profile information
        userdata.first_name = firstName
        userdata.last_name = lastName
        userdata.email = email
        userdata.phone = phoneNumber

        # Update profile image if a new one was uploaded
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            userdata.profileimage = filename

        db.session.commit()

        flash("Profile Update Success", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", userdata=userdata) 


@app.route("/accept/<path:ids>", methods=["GET"])
def acceptfriendrequest(ids):
    data = ids.split("/")

    friend_request = Friends.query.filter_by(
        requested_id=data[0],
        user_id=data[1]
    ).first()

    if friend_request:
        friend_request.isAccepted = "True"
        db.session.commit()
        flash("Friend Request Accepted", "success")
    else:
        flash("Friend request not found", "warning")

    return redirect(url_for("profile"))
    


if __name__ == "__main__":
    app.run(debug=True)