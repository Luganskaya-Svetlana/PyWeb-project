import os.path

from shutil import copy
from flask_login import current_user
from flask import Flask
from flask import redirect, render_template, url_for, request
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, FileField
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, ValidationError

from data import db_session
from data.users import User
from data.desserts import Dessert
from data.map import if_country

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

APP_ROUTE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_USER_AVATAR = "default_user_pic.png"
DEFAULT_DESSERT_AVATAR = "default_des_pic.png"


class DownloadPic(FlaskForm):
    field = FileField("Прикрепите фотографию")
    fin = SubmitField("Отправить")


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


class DessertForm(FlaskForm):
    title = StringField('Название десерта:', validators=[DataRequired()])
    content = TextAreaField('Описание', validators=[DataRequired()])
    country = StringField('Родина десерта:', validators=[DataRequired()])
    submit = SubmitField("Добавить")

    def validate_country(self, field):
        if not if_country(field.data):
            raise ValidationError('Это не страна')


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
        photo = request.files.get("avatar")

        db_sess.add(user)
        db_sess.commit()
        if photo is not None:
            url = url_for('static', filename="img/user_avatars")[1:]
            photo.save(url + f"/{photo.filename}")
            os.rename(url + f"/{photo.filename}", url + f"/{user.id}{photo.filename[photo.filename.find('.'):]}")
        else:
            url = url_for('static', filename=f"img")[1:]
            extension = DEFAULT_USER_AVATAR[DEFAULT_DESSERT_AVATAR.find('.'):]
            copy(url + f"/{DEFAULT_USER_AVATAR}", url + f"/user_avatars/{user.id}{extension}")
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


@app.route("/download_photo", methods=["GET", "POST"])
def pic():
    # form = DownloadPic()
    # if form.validate_on_submit():
    #     print("validation completed")
    #     catalog_name = url_for("static", filename="img/user_avatars")
    #     print(catalog_name)
    #     print(form.field)
    #     f = request.FILES[form.field.name]
    #     with open(catalog_name[1:] + "/1.png", mode='wb') as picfile:
    #         picfile.write(f.read())
    #     # with open(catalog_name[1:] + "/1.png", mode='wb') as picfile:
    #     #     print("file was opened")
    #     #     print(form.field.data)
    #     #     print(form.field)
    #     #     picfile.write(form.field.data)
    #     return redirect("/")
    # return render_template("download_pic.html", title="Загрузить фото", form=form)
    return render_template("download_pic.html")


@app.route("/upload", methods=["POST"])
def upload():
    target = os.path.join(APP_ROUTE, "static/img/")
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)
    return "complete"


# @app.route("/desserts")
# def desserts_main_page():
#     return redirect("/")


@app.route("/profile")
def profile():
    return redirect("/")


@app.route('/desserts', methods=['GET', 'POST'])
@login_required
def add_dessert():
    form = DessertForm()
    if form.validate_on_submit():
        print(1)
        db_sess = db_session.create_session()
        dessert = Dessert()
        dessert.title = form.title.data
        dessert.content = form.content.data
        dessert.country = form.country.data
        dessert.user_id = current_user.id
        print(2)
        current_user.desserts.append(dessert)  # тут все падает
        db_sess.merge(current_user)
        db_sess.commit()
        print(3)
        return redirect('/')
    return render_template('desserts.html', title='Добавление десерта', form=form)


def main():
    db_session.global_init("db/all.db")
    app.run(port=5000, debug=True)


if __name__ == '__main__':
    main()
