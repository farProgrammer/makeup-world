"""SQLAlchemy models for makeup_world app."""

from datetime import datetime
from wtforms import SubmitField, BooleanField, StringField,IntegerField,  TextAreaField,SelectField, PasswordField, validators
from flask_wtf import Form

from  flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

GENERIC_IMAGE = "https://cdn.pixabay.com/photo/2016/02/19/11/35/makeup-1209798_1280.jpg"

bcrypt = Bcrypt()
db = SQLAlchemy()




class  Product(db.Model):
    """Select product."""

    __tablename__ = "products"

    id = db.Column(db.Integer,primary_key=True)
    brand = db.Column(db.Text,nullable=False)
    name = db.Column(db.Text,nullable=False)
    photo_url =db.Column(db.Text)
    price = db.Column(db.Integer)
    review = db.Column(db.Text)
    available = db.Column(db.Boolean, nullable = False,default= True)

    def image_url(self):
        """Return image for product -- bespoke or generic."""

        return self.photo_url or GENERIC_IMAGE



####################

class RegForm(Form):
    name_first = StringField('First Name', [validators.DataRequired()])
    name_last = StringField('Last Name', [validators.DataRequired()])
    email = StringField('Email Address', [validators.DataRequired(), validators.Email(), validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Submit')

##################




def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

