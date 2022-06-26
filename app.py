import sqlite3

from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from dataWork import Data
import sys

print('This is error output', file=sys.stderr)
print('This is standard output', file=sys.stdout)

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
data_work = Data()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Friends(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user1 = db.Column(db.Integer)
    user2 = db.Column(db.Integer)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    # liked = db.Column(db)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": " ", "class": "input"})

    password = PasswordField(validators=[
        InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": " ", "class": "input"})

    submit = SubmitField('Зареєструватись', render_kw={"class": "submit"})

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": " ", "class": "input"})

    password = PasswordField(validators=[
        InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": " ", "class": "input"})

    submit = SubmitField('Login', render_kw={"class": "submit"})


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    data_work.print_data()
    recommendations = data_work.get_user_friends_recommendations(current_user.id)
    if request.method == 'POST':
        for i in data_work.get_user_friends(current_user.id):
            if request.form.get('delete_' + str(i.id)) == 'Видалити':
                con = sqlite3.connect('database.db')
                cur = con.cursor()
                id1 = current_user.id
                id2 = i.id
                delete = 'DELETE FROM friends WHERE (user1 == {} AND user2 == {}) OR (user2 == {} AND user1 == {})'.format(
                    id1, id2, id1, id2)
                print(delete)
                cur.execute(delete)
                con.commit()
                data_work.print_data()
        for i in recommendations:
            id1 = current_user.id
            id2 = i.id
            if request.form.get('put_' + str(i.id)) == 'Додати':
                con = sqlite3.connect('database.db')
                cur = con.cursor()
                id1 = current_user.id
                id2 = i.id
                put = 'INSERT INTO friends (user1, user2) VALUES ({}, {})'.format(id1, id2)
                print(put)
                cur.execute(put)
                con.commit()
                data_work.print_data()
    return render_template('dashboard.html', username=current_user.username,
                           users=data_work.get_user_friends(current_user.id),
                           recommended_users=recommendations)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
