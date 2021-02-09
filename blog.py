from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json

with open("config.json", "r") as config:
    params = json.load(config)["params"]
local_server = params["local_server"]

app = Flask(__name__)

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


@app.route('/')
def home():
    return render_template("index.html", params=params)


@app.route('/about')
def about():
    return render_template("about.html", params=params)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')

        entry = Contacts(name=name, email=email, phone=phone, message=msg)
        db.session.add(entry)
        db.session.commit()

        mail.send_message(f"New message from {name} ({email})",
                          sender=email,
                          recipients=[params['mail_username']],
                          body=f"{msg}\n\nContact No - {phone}")

    return render_template("contact.html", params=params)


app.run(debug=True)
