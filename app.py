"""Flask app for makeup_world app."""

import os
import re
from sqlalchemy import func
import psycopg2  # pip install psycopg2
import psycopg2.extras
import requests
from flask import (Flask, abort, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)

from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf import FlaskForm
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from forms import AddProductForm, EditProductForm
from models import  db, connect_db, Product,RegForm
from flask_bootstrap import Bootstrap


CURR_USER_KEY = "curr_user"

API_BASE_URL = "http://makeup-api.herokuapp.com/"


app = Flask(__name__)

UPLOAD_FOLDER='static/uploads/'

# app.config['SECRET_KEY'] = "abcdef"
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get('DATABASE_URL',"postgresql:///makeup_world")
app.config ['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
app.config['SQLALCHEMY_ECHO'] = False
# redirects must be intercepted for some tests to pass
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SECRET_KEY' ]= os.environ.get('SECRET_KEY', "color330788secret")
app.config ['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS= set (['png','jpg','jpeg','gif'])
toolbar = DebugToolbarExtension(app)


connect_db(app)
db.create_all()


 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS



    
@app.route('/', methods=['GET', 'POST'])
def registration():
    form = RegForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        return  """<body  style="background-color:silver;"> 
        <h1 style="background-color:maroon;" >WELCOME TO MAKEUP WORLD </h1> <form method="POST">
    <a href="buy_product"><b class="btn btn-secondary">Go To Product</b></a><br>
  <a href="/search/product_brand"><b class="btn btn-success">Product-Brand-List </b></a><br>
    <a href="add"><b class="btn btn-primary">Product-Add-Form</b></a><br>
     <a href="favorite"><b class="btn btn-info">Generate-Favorite</b></a><br>

     <button class="btn btn-primary" type="submit">back to create account </button>
 <iframe src="https://giphy.com/embed/TLvVy3zMUFCAaFUv81" width="480" height="480" frameBorder="0" class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/vasanticosmetics-blue-eyeliner-kajal-waterline-big-up-mascara-TLvVy3zMUFCAaFUv81">Makeup Art</a></p>

 <iframe src="https://giphy.com/embed/OODUDx2dvzYZpjOaSO" width="480" height="470" frameBorder="0" class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/younglivingeo-makeup-young-living-OODUDx2dvzYZpjOaSO">Cosmetics</a></p>
</form> </body>"""
    return render_template('registration_custom.html', form=form)
    # return render_template('register.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
 form = RegForm(request.form)
 if request.method == 'POST' and form.validate_on_submit():
    return 'We confirm your login!'
 return render_template('login.html', form=form)


@app.route('/favorite',methods=['GET','POST'])
def favorite():
    """" GENERATE YOUR FAVOURITE PRODUCT """
    return render_template('favorite.html')



@app.route('/',methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file=request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect (request.url)
    if file and allowed_file(file.filename):
        filename =secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        flash('Image successfully uploaded and displayed below')
        return render_template('buy_product.html',filename=filename)
    else:
        flash('Allowed image types are - png,jpg,jpeg,gif')
        return redirect (request.url)
        
@app.route('/display/<filename>')
def display_image(filename):
    return redirect (url_for('static',filename='buy_products/'+ filename),code=301)
    

@app.route('/process', methods=['POST'])
def process():
    # Retrieve the HTTP POST request parameter value from 'request.form' dictionary
    _username = request.form.get('username') 
     # get(attr) returns None if attr is not present
    
    check_password_hash = request.form.get('password')




    # Validate and send response
    if _username :
        return render_template('buy_product.html', username=_username)
  
    else:
        return 'Please go back and enter your name...', 400  # 400 Bad Request
 

@app.route("/search/<product_brand>",methods=["GET","POST"])
def List_product_by_brand(product_brand):
    """List product_brand."""
    res= requests.get(f'http://makeup-api.herokuapp.com/api/v1/products.json?brand={product_brand}')
    

    return render_template("product_brand.html",res=res)

@app.route("/buy_product")
def buy_product():
    """Buy a Product"""
    return render_template("buy_product.html")

######################################


############################################
@app.route("/product_list")
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
        return redirect(url_for('list_product'))

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

if __name__ == "__main__":

    app.run(debug=True)
