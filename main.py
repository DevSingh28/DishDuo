from flask import Flask, render_template, redirect, url_for, session, request, abort, flash, jsonify, \
    send_from_directory
from flask_bootstrap import Bootstrap5
from forms import RegisterForm, LoginForm, ResetPasswordForm, ForgotPasswordForm, OtpForm, CreateCommentForm, PostForm, \
    ProfilePP, AiForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship, Session, mapped_column, Mapped
from sqlalchemy import Integer, String, ForeignKey, Column, Table, DateTime, desc
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
import requests
import random
from flask_ckeditor import CKEditor
from functools import wraps
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from g4f.client import Client


def extract_video_id(url):
    parsed_url = urlparse(url)

    if parsed_url.netloc == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        if parsed_url.path[:7] == '/embed/':
            return parsed_url.path.split('/')[2]
        if parsed_url.path[:3] == '/v/':
            return parsed_url.path.split('/')[2]
    return None


app = Flask(__name__)

current_directory = os.getcwd()
upload_folder_name = 'uploads_pp'
upload_folder_path = os.path.join(current_directory, upload_folder_name)
if not os.path.exists(upload_folder_path):
    os.makedirs(upload_folder_path)
app.config['UPLOAD_FOLDER'] = upload_folder_path

upload_folder_name2 = 'uploads_post'
upload_folder_path2 = os.path.join(current_directory, upload_folder_name2)
if not os.path.exists(upload_folder_path2):
    os.makedirs(upload_folder_path2)
app.config['UPLOAD_FOLDER_POST'] = upload_folder_path2

Bootstrap5(app)
app.secret_key = os.environ.get("coffee_key")
serializer = URLSafeTimedSerializer(app.secret_key)
ckeditor = CKEditor(app)

author_email = os.environ.get("myemail")
author_password = os.environ.get("gm_pass")
mailersend_api_key = os.environ.get('mailersend_api_key')
sender_email = os.environ.get('owner_gm')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class Base(DeclarativeBase):
    pass


def admin_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(403)
        return f(*args, **kwargs)

    return decorated


def send_mail(recipient, subject, body):
    try:
        response = requests.post(
            'https://api.mailersend.com/v1/email',
            json={
                'to': [{'email': recipient}],
                'subject': subject,
                'text': body,
                'from': {'email': sender_email}
            },
            headers={'Authorization': f'Bearer {mailersend_api_key}'}
        )
        response.raise_for_status()
    except Exception as e:
        pass


def verify_password(user):
    token = serializer.dumps(user.email, salt=os.environ.get('dev_key'))
    reset_url = url_for('reset_password', token=token, _external=True)
    subject = "Password Reset Request"
    body = (
        f"Hello {user.name},\nWe've received a request to reset your password. To proceed, please follow the link below:\n{reset_url}\nIf you didn't request this change, you can safely ignore this message.Best regards,\nDev Singh")
    send_mail(user.email, subject, body)


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI3", "sqlite:///main.db")

db = SQLAlchemy(model_class=Base)
db.init_app(app)


def ai_generator(components):
    client = Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Suggest a recipe using the items listed as available. Make sure you "
                                              f"have a nice name for this recipe listed at the start. Also, "
                                              f"include a funny version of the name of the recipe on the following "
                                              f"line. Then share the recipe in a step-by-step manner. In the end, "
                                              f"write a fun fact about the recipe or any of the items used in the "
                                              f"recipe. Here are the items available: {components}, Haldi, "
                                              f"Chilly Powder, Tomato Ketchup, Water, Garam Masala, Oil"}],
    )
    return response.choices[0].message.content


def generate_otp():
    return str(random.randint(100000, 999999))


followers = Table('followers',
                  Base.metadata,
                  Column('follower_id', Integer, ForeignKey('user.id')),
                  Column('followed_id', Integer, ForeignKey('user.id'))
                  )


class User(Base, UserMixin):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    bio: Mapped[str] = mapped_column(String)
    profile_pic: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String, nullable=False)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    liked_posts = relationship("PostLike", back_populates="user")
    following = relationship('User',
                             secondary=followers,
                             primaryjoin=(followers.c.follower_id == id),
                             secondaryjoin=(followers.c.followed_id == id),
                             backref="followers")

    def is_following(self, user):
        """
        Check if the current user is following the specified user.

        Args:
            user: The user to check if the current user is following.

        Returns:
            bool: True if the current user is following the specified user, False otherwise.
        """
        # Check if the specified user is in the following relationship of the current user
        return user in self.following


class Post(Base):
    __tablename__ = 'post'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)
    yt: Mapped[str] = mapped_column(String, nullable=False, default=None)
    steps: Mapped[str] = mapped_column(String, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    # Define relationships
    author = relationship("User", back_populates="posts")
    likes = relationship("PostLike", back_populates="post")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = 'comment'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('post.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    # Define relationships
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


class PostLike(Base):
    __tablename__ = 'post_like'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('post.id'), primary_key=True)

    # Define relationships
    user = relationship("User", back_populates="liked_posts")
    post = relationship("Post", back_populates="likes")


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    current_user_id = current_user.id if current_user.is_authenticated else None
    loaded_posts = request.args.get('loaded_posts', default=0, type=int)
    posts_per_page = 10
    content = db.session.query(Post).order_by(desc(Post.created_at)).offset(loaded_posts).limit(posts_per_page).all()
    content2 = db.session.execute(db.select(User)).scalars().all()
    content3 = db.session.execute(db.select(PostLike)).scalars().all()
    content4 = db.session.execute(db.select(Comment)).scalars().all()
    user_liked_post_ids = [like.post_id for like in content3 if like.user_id == current_user_id]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('posts.html', data=content, data2=content2, data3=content3, data4=content4,
                               user=current_user_id, user_liked_post_ids=user_liked_post_ids, current_user=current_user)
    else:
        return render_template('index.html', data=content, data2=content2, data3=content3, data4=content4,
                               user=current_user_id, user_liked_post_ids=user_liked_post_ids, current_user=current_user)


@app.route('/search/users', methods=['GET'])
def search_users():
    search_query = request.args.get('query')
    matching_users = db.session.query(User).filter(User.username.ilike(f'%{search_query}%')).all()
    users_json = [{'id': user.id, 'name': user.username} for user in matching_users]
    return jsonify(users=users_json)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/uploads2/<filename>')
def uploaded_file2(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_POST'], filename)


@app.route('/profile')
def user_profile():
    now_user = current_user.id
    user = db.get_or_404(User, now_user)
    followers_count = len(user.followers)
    following_count = len(user.following)
    user_posts = user.posts
    return render_template('profile.html', followers_count=followers_count, following_count=following_count, user=user,
                           user_posts=user_posts)


@app.route('/view_profile/<int:user_id>')
def view_profile(user_id):
    user = db.get_or_404(User, user_id)
    followers_count = len(user.followers)
    following_count = len(user.following)
    user_posts = user.posts
    is_following = current_user.is_authenticated and user in current_user.following
    is_super_admin = current_user.is_authenticated and current_user.email == author_email
    return render_template('profile.html', followers_count=followers_count, following_count=following_count, user=user,
                           user_posts=user_posts, current_user=current_user, is_following=is_following,
                           is_super_admin=is_super_admin)


@app.route('/edit_profile', methods=['POST', 'GET'])
@admin_only
def edit_profile():
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_bio = request.form.get('bio')
        current_user.name = new_name
        current_user.bio = new_bio
        db.session.commit()
        return redirect(url_for('user_profile'))


@app.route('/edit_profile_pic', methods=['POST', 'GET'])
@admin_only
def edit_profile_pic():
    form = ProfilePP()
    if form.validate_on_submit():
        profile_pic = form.profile_pic.data
        filename = secure_filename(profile_pic.filename)
        filename = f"user_{random.randint(10, 999)}_{filename}"
        profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        current_user.profile_pic = filename
        db.session.commit()
        return redirect(url_for('user_profile'))
    return render_template('profile_update.html', form=form)


@app.route("/login", methods=['POST', 'GET'])
def login():
    form = LoginForm()
    form.submit.render_kw = {'onclick': 'showSpinner()'}
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user:
            flash("Sorry, this email doesn't exist. Please register an account to continue.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Entered Password is Incorrect")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form, current_user=current_user)


@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        old_user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if old_user:
            verify_password(old_user)
            flash(
                "An email has been dispatched to your registered email address containing instructions to reset your password.")
            return redirect(url_for('forgot_password'))
        else:
            flash(
                "This email is not registered with us. Please check the email address or consider registering if you are new to our platform.")
            return redirect(url_for('forgot_password'))
    return render_template('forgot.html', form=form)


@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt=os.environ.get("dev_key"), max_age=3600)
        user = old_user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user:
            return redirect(url_for('login'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            new_password = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=8)
            user.password = new_password
            db.session.commit()
            return redirect(url_for('home'))
    except:
        return redirect(url_for('login'))
    return render_template("reset.html", form=form)


@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    form.submit.render_kw = {'onclick': 'showSpinner()'}
    if form.validate_on_submit():
        email_data = form.email.data
        user_username = form.username.data
        user = db.session.execute(db.select(User).where(User.email == email_data)).scalar()
        exist_user = db.session.execute(db.select(User).where(User.username == user_username)).scalar()
        if user:
            flash("The email provided already exists. Please use a different email address.")
            return redirect(url_for('register'))
        elif exist_user:
            flash("The username already exists try different one.")
            return redirect(url_for('register'))
        else:
            profile_pic = form.profile_pic.data
            filename = secure_filename(profile_pic.filename)
            filename = f"user_{random.randint(10, 999)}_{filename}"
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            otp = generate_otp()
            subject = "OTP for Registration"
            body = f"Dear Foodie,\nWe're thrilled to have you join us! Your registration OTP is {otp}.\nRemember to indulge responsibly, and don't forget to wash your hands before enjoying your culinary adventure."
            send_mail(email_data, subject, body)
            session['otp'] = otp
            session['name'] = form.name.data
            session['username'] = form.username.data
            session['email'] = email_data
            session['profile_pic'] = filename
            session['bio'] = form.bio.data
            session['password'] = form.password.data
            return redirect(url_for('verify_otp'))
    return render_template('register.html', form=form, current_user=current_user)


@app.route('/verify_otp', methods=["POST", "GET"])
def verify_otp():
    if 'otp' not in session:
        flash('OTP not found. Please register first.', 'danger')
        return redirect(url_for('register'))

    form = OtpForm()
    attempts_left = session.get('attempts_left', 3)
    if attempts_left == 0:
        session.pop("otp", None)
        session.pop("attempts_left", None)
        session.clear()
        return redirect(url_for('register'))

    if form.validate_on_submit():
        entered_otp = form.otp.data
        created_otp = session.get("otp")

        if entered_otp == created_otp:
            name = session.pop('name', None)
            username = session.pop('username', None)
            email = session.pop('email', None)
            bio = session.pop('bio', None)
            profile_pic = session.pop('profile_pic', None)
            password = session.pop('password', None)

            new_password = generate_password_hash(
                password=password,
                method='pbkdf2:sha256',
                salt_length=8
            )

            new_user = User(name=name, username=username, email=email, bio=bio, profile_pic=profile_pic, password=new_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
        else:
            attempts_left -= 1
            session['attempts_left'] = attempts_left
            flash('Invalid OTP', 'danger')

    return render_template('verify.html', form=form, attempts_left=attempts_left)


@app.route('/create_post', methods=['POST', 'GET'])
@admin_only
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        recipe_picture = form.img_url.data
        filename = secure_filename(recipe_picture.filename)
        filename = f"user_{random.randint(10, 999)}_{filename}"
        recipe_picture.save(os.path.join(app.config['UPLOAD_FOLDER_POST'], filename))
        new_post = Post(
            recipe_name=form.recipe_name.data,
            description=form.description.data,
            img_url=filename,
            yt=form.yt.data,
            steps=form.steps.data,
            author_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)


@app.route('/like/<int:post_id>', methods=['POST'])
@admin_only
def like_post(post_id):
    if current_user.is_authenticated:
        post = db.get_or_404(Post, post_id)
        post_like = db.session.query(PostLike).filter_by(user_id=current_user.id, post_id=post.id).first()
        if post_like:
            db.session.delete(post_like)
        else:
            post_like = PostLike(user_id=current_user.id, post_id=post.id)
            db.session.add(post_like)
        db.session.commit()
        new_like_count = len(post.likes)
        return jsonify({'new_like_count': new_like_count})
    return redirect(request.referrer)


@app.route('/comment/<int:post_id>', methods=['POST'])
@admin_only
def comment_post(post_id):
    if current_user.is_authenticated:
        post = db.get_or_404(Post, post_id)
        content = request.form['content']
        comment = Comment(content=content, author_id=current_user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
    return redirect(request.referrer)


@app.route('/show_post/<int:post_id>', methods=["POST", "GET"])
def post_show(post_id):
    form = CreateCommentForm()
    post = db.get_or_404(Post, post_id)
    total_likes = len(post.likes)
    total_comments = len(post.comments)
    user_id = post.author
    cmnts = db.session.query(Comment).filter_by(post_id=post.id).order_by(desc(Comment.id)).all()
    is_super_admin = current_user.is_authenticated and current_user.email == author_email
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            post_id=post.id,
            author_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(request.referrer)
    return render_template('show_post.html', form=form, post=post, total_likes=total_likes, cmnt=cmnts, user_id=user_id,
                           total_comments=total_comments, current_user=current_user, is_super_admin=is_super_admin,
                           extract_video_id=extract_video_id)


@app.route('/follow_user/<int:user_id>', methods=['POST'])
@admin_only
def follow_user(user_id):
    user_to_follow = db.get_or_404(User, user_id)
    if current_user != user_to_follow:
        if user_to_follow in current_user.following:
            current_user.following.remove(user_to_follow)
            followed = False
        else:
            current_user.following.append(user_to_follow)
            followed = True
        db.session.commit()
        # Calculate the updated follower count for the user being followed
        follower_count = len(user_to_follow.followers)
        return jsonify({'followed': followed, 'follower_count': follower_count})
    return jsonify({'followed': False})


@app.route('/get_follow_status/<int:user_id>')
@login_required
def get_follow_status(user_id):
    user = db.get_or_404(User, user_id)
    is_following = current_user.is_following(user)
    return jsonify({'followed': is_following})


@app.route("/delete_post/<int:post_id>")
@admin_only
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    is_super_admin = current_user.email == author_email
    if current_user == post.author or is_super_admin:
        session = Session.object_session(post)
        session.query(PostLike).filter_by(post_id=post_id).delete()
        session.query(Comment).filter_by(post_id=post_id).delete()
        db.session.delete(post)
        db.session.commit()
        return redirect(request.referrer)


@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@admin_only
def delete_comment(comment_id):
    # Fetch the comment from the database
    comment = db.get_or_404(Comment, comment_id)
    is_super_admin = current_user.email == author_email
    if current_user == comment.author or is_super_admin:
        db.session.delete(comment)
        db.session.commit()
        return redirect(request.referrer)


@app.route('/recipe_ai', methods=["POST", "GET"])
@admin_only
def recipe_ai():
    form = AiForm()
    output = None
    form.submit.render_kw = {'onclick': 'showSpinner()'}
    if form.validate_on_submit():
        components = form.input.data
        output = ai_generator(components)
    return render_template('recipe_maker.html', form=form, output=output)


@app.route("/logout")
def remove_me():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(port=5002)


"""
DishDuo

Copyright (C) 2024 Dev Singh

All rights reserved.

This file is part of DishDuo.

DishDuo can not be copied and/or distributed without the express
permission of Dev Singh.
"""
