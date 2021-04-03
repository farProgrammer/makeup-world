"""Models for makeup app."""

from  flask_sqlalchemy import SQLAlchemy

GENERIC_IMAGE = "https://cdn.pixabay.com/photo/2016/02/19/11/35/makeup-1209798_1280.jpg"

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


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

