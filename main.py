from flask_login import current_user
from flask import Flask
from flask import redirect, render_template
from data import db_session
from data.users import User
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(FlaskForm):
    email_or_name = StringField("Ник или почта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    email = EmailField("Введите почту: ", validators=[DataRequired()])
    name = StringField("Ваш никнейм: ", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_again = PasswordField("Пароль ещё раз", validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField("Зарегистрироваться")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def default_page():
    return render_template("base.html", title="WorldDessert", current_user=current_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", title="Регистрация", form=form,
                                   message="Введённые пароли не совпадают")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            sec_message = ''
            message = "Пользователь с таким email'ом уже зарегистрирован"
            user = db_sess.query(User).filter(User.name == form.name.data).first()
            if user:
                sec_message = "Пользователь с таким логином уже существует"
            return render_template("register.html", title="Регистрация", form=form,
                                   message=message, sec_message=sec_message)
        user = User()
        user.email = form.email.data
        user.name = form.name.data
        user.set_password(form.password.data)
        user.about = form.about.data
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=True)
        return redirect("/")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email_or_name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        user = db_sess.query(User).filter(User.name == form.email_or_name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template("login.html", title="Авторизация", form=form)


def main():
    db_session.global_init("db/all.db")
    app.run(port=8000, debug=True)


if __name__ == '__main__':
    main()
