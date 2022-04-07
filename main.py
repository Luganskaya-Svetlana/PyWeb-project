from flask_login import current_user
from flask import Flask, abort
from flask import redirect, render_template, url_for, request
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, FileField
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
import sqlalchemy

from data import db_session
from data.users import User
from data.desserts import Dessert
from data.map import if_country

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


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
    photo = FileField("Ваш аватар")
    submit = SubmitField("Зарегистрироваться")


class DessertForm(FlaskForm):
    title = StringField('Название десерта:', validators=[DataRequired()])
    content = TextAreaField('Описание', validators=[DataRequired()])
    country = StringField('Родина десерта:', validators=[DataRequired()])
    submit = SubmitField("Добавить")

    def validate_country(form, field):
        if not if_country(field.data):
            raise ValidationError(f'{field.data} - не страна')


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
    db_sess = db_session.create_session()
    desserts = db_sess.query(Dessert)[::-1]
    return render_template("index.html", title="Cicero's desserts", current_user=current_user, desserts=desserts)


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
        # photo =
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


@app.route("/download_photo", methods=["GET", "POST"])
def pic():
    form = DownloadPic()
    if form.validate_on_submit():
        print("validation completed")
        catalog_name = url_for("static", filename="img/user_avatars")
        print(catalog_name)
        print(form.field)
        f = request.FILES[form.field.name]
        with open(catalog_name[1:] + "/1.png", mode='wb') as picfile:
            picfile.write(f.read())
        # with open(catalog_name[1:] + "/1.png", mode='wb') as picfile:
        #     print("file was opened")
        #     print(form.field.data)
        #     print(form.field)
        #     picfile.write(form.field.data)
        return redirect("/")
    return render_template("download_pic.html", title="Загрузить фото", form=form)


@app.route("/desserts")
def desserts_main_page():
    return redirect("/")


@app.route("/profile")
def profile():
    return redirect("/")


@app.route('/desserts/add', methods=['GET', 'POST'])
@login_required
def add_dessert():
    form = DessertForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        dessert = Dessert()
        dessert.title = form.title.data
        dessert.content = form.content.data
        dessert.country = form.country.data
        try:
            current_user.desserts.append(dessert)
        except sqlalchemy.orm.exc.DetachedInstanceError:
            return render_template('desserts.html', title='Добавление десерта', form=form,
                                   message='Ой! Что-то пошло не так. Попробуйте снова.') # надеюсь, удалю потом эту строчку
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('desserts.html', title='Добавление десерта', form=form)


@app.route('/desserts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_desserts(id):
    form = DessertForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        dessert = db_sess.query(Dessert).filter(Dessert.id == id, Dessert.user == current_user).first()
        if dessert:
            form.title.data = dessert.title
            form.content.data = dessert.content
            form.country.data = dessert.country
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        dessert = db_sess.query(Dessert).filter(Dessert.id == id, Dessert.user == current_user).first()
        if dessert:
            dessert.title = form.title.data
            dessert.content = form.content.data
            dessert.country = form.country.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('desserts.html', title='Редактирование десерта', form=form)


@app.route('/desserts/delete/<int:id>', methods=['GET'])
@login_required
def delete_dessert(id):
    db_sess = db_session.create_session()
    dessert = db_sess.query(Dessert).filter(Dessert.id == id, Dessert.user == current_user).first()
    if dessert:
        db_sess.delete(dessert)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init("db/all.db")
    app.run(port=8000, debug=True)


if __name__ == '__main__':
    main()
