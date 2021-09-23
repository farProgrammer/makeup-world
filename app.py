"""Flask app for makeup app."""

from flask import Flask, url_for, render_template, redirect, flash, jsonify

from  flask_debugtoolbar import  DebugToolbarExtension

from  models import  db, connect_db, Product
from  forms import AddProductForm, EditProductForm
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import requests
import os

API_SECRET_KEY = os.environ.get('API_SECRET_KEY')

CURR_USER_KEY = "curr_user"

API_BASE_URL = "http://makeup-api.herokuapp.com/"


app = Flask(__name__)


# app.config['SECRET_KEY'] = "abcdef"

app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get('DATABASE_URL',"postgresql:///makeup")
app.config ['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
app.config['SQLALCHEMY_ECHO'] = False
# redirects must be intercepted for some tests to pass
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "color330788secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

# ******************************







@app.route("/")
def list_products():
    """List all products."""

    products = Product.query.all()
    return render_template("product_list.html",products=products)

@app.route("/add",methods=["GET","POST"])  
def add_product():
    """Add a product."""

    form = AddProductForm()

    if form.validate_on_submit():
        data = {k:v for k,v in form.data.items()if k != "csrf_token"}
        new_product = Product(**data)
        db.session.add(new_product)
        db.session.commit()
        flash(f"{new_product.name}added.")
        return redirect(url_for('list_products'))

    else:
          return render_template("product_add_form.html",form=form)

@app.route("/<int:product_id>",methods=["GET","POST"])
def edit_product(product_id):
    """Edit product."""

    product = Product.query.get_or_404(product_id)
    form = EditProductForm(obj=product)

    if form.validate_on_submit():
       product.review = form.review.data
       product.available = form.available.data
       product.photo_url = form.photo_url.data
       db.session.commit()
       flash(f"{product.name} selected.")
       return redirect(url_for('list_products'))

    else:
        return render_template("product_edit_form.html",form=form,product=product )


@app.route("/api/products/<int:product_id>",methods=['GET'])    
def api_get_product(product_id):
    """Return basic info about product in JSON."""

    product = Product.query.get_or_404(product_id)
    info ={"name":product.name,"price":product.price}

    return jsonify(info)