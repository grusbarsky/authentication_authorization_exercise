from flask import Flask, request, jsonify, render_template, redirect, session
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginUserForm, DeleteUserForm, FeedbackForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "12345"

connect_db(app)

@app.route("/")
def root():
    """show homepage"""
    return render_template('base.html')

@app.route("/register")
def show_register_form():
    """show a form that when submitted will create a user"""

    form = RegisterForm()

    if 'username' in session:
        return redirect("/users/{session['username']}")

    else:
        return render_template('User/register.html', form=form)

@app.route("/register", methods=['POST'])
def create_user():
    """handles form submit and creates a user then redirects to users page, else: reload form"""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = User.register(username, password, first_name, last_name, email)

        db.session.commit()
        session['username'] = user.username

        return redirect(f"/users/{user.username}")
    else:
        return render_template("User/register.html", form=form)

@app.route("/users/<username>")
def users_page():
    """a users page"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()
    else:
        user = User.query.get(username)
        form = DeleteForm()
        return render_template("User/user.html", user=user, form=form)

@app.route("/login")
def show_login_form():
    """check if user exists, redirect to userpage if does
        if not, show a form that when submitted will login user
    """

    form = LoginUserForm()
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    else:
        return render_template('User/login.html', form=form)

@app.route("/login", methods=['POST'])
def login_user():
    """handle form submit, authenticate user, and if so redirect to users page"""

    form = LoginUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password."]
            return render_template("User/login.html", form=form)

    return render_template("User/login.html", form=form)

@app.route("/logout")
def logout_user():
    """clear session storage and return to /"""

    session.clear()

    return redirect("/login")

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """delete user and redirect to login"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")

@app.route("/users/<username>/feedback/new")
def show_new_feedback_form(username):
    """Show feedback form"""

    form = FeedbackForm()

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    else:
        return render_template("Feedback/new.html", form=form)

@app.route("/users/<username>/feedback/new", methods=['POST'])
def add_new_feedback(username):
    """handle feedback form submit and add feedback"""

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content=content,
            username=username,
        )

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("Feedback/new.html", form=form)

@app.route("/feedback/<int:feedback_id>/update")
def show_update_feedback_form(feedback_id):
    """Show update-feedback form"""

    feedback = Feedback.query.get(feedback_id)
    form = FeedbackForm(obj=feedback)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    else:
        return render_template("Feedback/edit.html", form=form, feedback=feedback)

@app.route("/feedback/<int:feedback_id>/update")
def update_feedback(feedback_id):
    """update feedback and redirect to feedback, else show edit form"""

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        return redirect(f"/users/{feedback.username}")

    else: 
        return render_template("Feedback/edit.html", form=form, feedback=feedback)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback"""

    feedback = Feedback.query.get(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")

