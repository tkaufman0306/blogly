"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash, session

from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from sqlalchemy import text

app = Flask(__name__)
app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///blogly"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "chickenzarecool21837"
# app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.drop_all()
db.create_all()


# Routes
@app.route("/")
def root():
    """Redirect to list of users"""
    return redirect("/users")


@app.route("/users")
def users_index():
    """show all users"""
    users = User.query.order_by(User.last_name, User.first_name).all()
    print(request.method)
    return render_template("users/index.html", users=users)


@app.route("/users/new", methods=["GET"])
def users_new_form():
    """Show an add form for users"""
    return render_template("users/new.html")


@app.route("/users/new", methods=["POST"])
def users_new():
    """Process the add form, adding a new user and going back to /users"""
    new_user = User(
        first_name=request.form["first_name"],
        last_name=request.form["last_name"],
        image_url=request.form["image_url"] or None,
    )

    db.session.add(new_user)
    db.session.commit()

    flash("User added successfully!", "success")
    return redirect("/users")


@app.route("/users/<int:user_id>")
def users_show(user_id):
    """Show information about the given user"""
    user = User.query.get_or_404(user_id)
    return render_template("users/show.html", user=user)


@app.route("/users/<int:user_id>/edit")
def users_edit(user_id):
    """Show the edit page for a user"""
    user = User.query.get_or_404(user_id)
    return render_template("users/edit.html", user=user)


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_user(user_id):
    """Process the edi form, returning the user to the /users page"""
    user = User.query.get_or_404(user_id)

    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]
    user.image_url = request.form["image_url"] or None

    db.session.add(user)
    db.session.commit()

    flash("User updated successfully!", "success")
    return redirect("/users")


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def users_destroy(user_id):
    """Delete the user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully!", "success")
    return redirect("/users")
