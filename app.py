"""Flask app for makeup app."""

from flask import Flask, url_for,request, render_template, redirect, flash, jsonify, session, g, abort

from  flask_debugtoolbar import  DebugToolbarExtension
from werkzeug.urls import url_encode
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, UserEditForm, LoginForm, MessageForm
from models import db, connect_db, User, Message


from  models import  db, connect_db, Product
from  forms import AddProductForm, EditProductForm
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import requests
import os


CURR_USER_KEY = "curr_user"


app = Flask(__name__)


# app.config['SECRET_KEY'] = "abcdef"

app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get('DATABASE_URL',"postgresql://localhost/makeup")
app.config ['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
app.config['SQLALCHEMY_ECHO'] = False
# redirects must be intercepted for some tests to pass
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "color330788secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

# ******************************


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If there already is a user with that username: flash message
    and re-present form.
    """

    do_logout()

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("Log out was successful.", "success")

    return redirect('/login')








@app.route("/search/<product_brand>",methods=["GET","POST"])
def List_product_by_brand(product_brand):
    """List product_brand."""
    res= request.get(f'http://makeup-api.herokuapp.com/api/v1/products.json?brand={product_brand}')
    

    return render_template("product_brand.html",res=res)

@app.route("/buy_product")
def buy_product():
    """Buy a Product"""
    return render_template("buy_product.html")


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())

    likes = [msg.id for msg in user.likes]

    return render_template('users/show.html', user=user, likes=likes, messages=messages)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/<int:user_id>/likes')
def show_likes(user_id):
    """Show a user's liked messages."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template('users/likes.html', user=user, likes=user.likes)


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    # if there is no logged in user
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)

    # if CSRF token validated
    if form.validate_on_submit():

        # if user is authenticated
        if User.authenticate(user.username, form.password.data):

            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or "/static/images/default-pic.png"
            user.header_image_url = form.header_image_url.data or "/static/images/warbler-hero.jpg"
            user.bio = form.bio.data
            db.session.commit()

            return redirect(f'/users/{user.id}')

        # if user not authenticated
        else:
            flash("Password not recognized", "danger")
            return redirect('/')

    # if CSRF token not validated
    else:
        return render_template('users/edit.html', form=form, user_id=user.id)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get_or_404(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get_or_404(message_id)

    if msg.user_id != g.user.id:
        flash('Access unauthorized.', 'danger')
        return redirect("/")

    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


@app.route('/messages/<int:message_id>/like', methods=["POST"])
def add_like(message_id):
    """Toggle a message's like status for a logged-in user if the user is NOT the author."""

    # unauthorized user
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get_or_404(message_id)

    # if the message was written by logged in user
    if msg.user_id == g.user.id:
        return abort(403)

    # logged in user's set of likes
    user_likes = g.user.likes

    # add like to user's likes
    # or remove it (to unlike the msg) if already there
    if msg in user_likes:
        g.user.likes = [like for like in user_likes if like != msg]
    else:
        g.user.likes.append(msg)

    db.session.commit()

    return redirect("/")


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        following_ids = [user.id for user in g.user.following] or []
        following_ids.append(g.user.id)

        # get 100 messages from user and those the user follows
        messages = (Message
                    .query
                    .filter(Message.user_id.in_(following_ids))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        liked_msg_ids = [msg.id for msg in g.user.likes]

        return render_template('home.html', messages=messages, likes=liked_msg_ids)

    else:
        return render_template('home-anon.html')


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req





@app.route("/product_list")
def list_products():
    """List all products."""

    products = Product.query.all()
    return render_template("product_list.html",products=products)


@app.route("/")
def list_products_by_brand():
    """List all product_brand."""

@app.route("/<string:product_brand>",methods=["GET","POST"])
def List_product_by_brand(product_brand):
    """List product_brand."""

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