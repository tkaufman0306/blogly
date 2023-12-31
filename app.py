"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag
from sqlalchemy import text

app = Flask(__name__)
app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///blogly"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "chickenzarecool21837"
# app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.drop_all()
db.create_all()


# Routes
@app.route("/")
def root():
    """Show recent list of posts, most recent first"""

    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template("posts/homepage.html", posts=posts)


@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page"""

    return render_template("404.html"), 404


# USER ROUTES


@app.route("/users")
def users_index():
    """show all users"""

    users = User.query.order_by(User.last_name, User.first_name).all()
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
    flash(f"User {new_user.full_name} added successfully!")

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
def users_update(user_id):
    """Process the edi form, returning the user to the /users page"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]
    user.image_url = request.form["image_url"] or None

    db.session.add(user)
    db.session.commit()

    flash(f"User {user.full_name} updated successfully!")

    return redirect("/users")


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def users_destroy(user_id):
    """Delete the user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash(f"User {user.full_name} deleted successfully!")

    return redirect("/users")


# POSTS Routes


@app.route("/users/<int:user_id>/posts/new")
def posts_new_form(user_id):
    """Show a form to create a new post for a specific user"""

    user = User.query.get_or_404(user_id)
    return render_template("posts/new.html", user=user)


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def posts_new(user_id):
    """Handle form submissions for creating a new post for a specific user"""

    user = User.query.get_or_404(user_id)
    new_post = Post(
        title=request.form["title"], content=request.form["content"], user=user
    )

    db.session.add(new_post)
    db.session.commit()
    flash(f"Post '{new_post.title}' added successfully!")

    return redirect(f"/users/{user_id}")


@app.route("/posts/<int:post_id>")
def posts_show(post_id):
    """Show a page with info on a specific post"""

    post = Post.query.get_or_404(post_id)
    app.logger.info(post)
    return render_template("posts/show.html", post=post)


@app.route("/posts/<int:post_id>/edit")
def posts_edit(post_id):
    """Show a form to edit an existing post"""

    post = Post.query.get_or_404(post_id)
    return render_template("posts/edit.html", post=post)


@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def posts_update(post_id):
    """Handle form submission for updating a specific post"""

    post = Post.query.get_or_404(post_id)
    post.title = request.form["title"]
    post.content = request.form["content"]

    db.session.add(post)
    db.session.commit()
    flash(f"Post '{post.title}' updated successfully!")

    return redirect(f"/users/{post.user_id}")


@app.route("/posts/<int:post_id>delete", methods=["POST"])
def posts_destroy(post_id):
    """Handle form submission fo rdeleting an existing post"""

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title} deleted successfully!")

    return redirect(f"/users/{post.user_id}")


# TAGS ROUTES#


@app.route("/tags")
def tags_index():
    """Show a page with info on all tags"""

    tags = Tag.query.all()
    return render_template("tags/index.html", tags=tags)


@app.route("/tags/new")
def tags_new_form():
    """Show a form to create a new tag"""

    posts = Post.query.all()
    return render_template("tags/new.html", posts=posts)


@app.route("/tags/new", methods=["POST"])
def tags_new():
    """Handle form submission for creating a new tag"""

    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name=request.form["name"], posts=posts)

    db.session.add(new_tag)
    db.session.commit()
    flash(f"Tag '{new_tag.name}' added.")

    return redirect("/tags")


@app.route("/tags/<int:tag_id>")
def tags_show(tag_id):
    """Show a page with info on a specific tag"""

    tag = Tag.query.get_or_404(tag_id)
    return render_template("tags/show.html", tag=tag)


@app.route("/tags/<int:tag_id>/edit")
def tags_edit_form(tag_id):
    """Show a form to edit an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template("tags/edit.html", tag=tag, posts=posts)


@app.route("/tags/<int:tag_id>/edit", methods=["POST"])
def tags_edit(tag_id):
    """Handle form submission for updating an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form["name"]
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' edited.")

    return redirect("/tags")


@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def tags_destroy(tag_id):
    """Handle form submission for deleting an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' deleted.")

    return redirect("/tags")
