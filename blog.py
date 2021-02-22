import datetime
import json
import os
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, session, redirect
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

with open("config.json", "r") as config:
    params = json.load(config)["params"]
local_server = params["local_server"]

app = Flask(__name__)

app.secret_key = 'siderfighter-secret'

app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER=params["mail_server"],
    MAIL_PORT=params["mail_port"],
    MAIL_USE_SSL=bool(params["mail_use_ssl"]),
    MAIL_USERNAME=params["mail_username"],
    MAIL_PASSWORD=params["mail_password"]
)

mail = Mail(app)

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]
db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    message = db.Column(db.String(120), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(50), nullable=True)


@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.datetime.now()

            if sno == '0':
                post = Posts(title=box_title, tagline=tagline, slug=slug, content=content, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.tagline = tagline
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pass')

        if username == params['admin_user'] and password == params['admin_password']:
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)

    return render_template("login.html", params=params)


@app.route('/')
def home():
    posts = Posts.query.filter_by().all()[0:params['no_of_post']]
    return render_template("index.html", params=params, posts=posts)


@app.route('/about')
def about():
    return render_template("about.html", params=params)


@app.route('/post/<string:post_slug>', methods=['GET'])
def post(post_slug):
    posts = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", params=params, post=posts)


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            file = request.files['fileUploadButton']
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            return "Uploaded Successfully"


@app.route("/delete/<string:sno>")
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route("/logout")
def logout():
    session.pop("user")
    return redirect('/dashboard')


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')
        date = datetime.now()

        entry = Contacts(name=name, email=email, phone=phone, message=msg, date=date)
        db.session.add(entry)
        db.session.commit()

        mail.send_message(f"New message from {name} ({email})",
                          sender=email,
                          recipients=[params['mail_username']],
                          body=f"{msg}\n\nContact No - {phone}")

    return render_template("contact.html", params=params)


app.run(debug=True)
