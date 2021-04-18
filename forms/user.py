from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')

class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class EditForm(FlaskForm):
    avatar = FileField(validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')])
    email = EmailField('Почта', validators=[DataRequired()])
    old_password = PasswordField('Старый пароль')
    new_password = PasswordField('Новый пароль')
    name = StringField('Новое имя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Подтвердить')
