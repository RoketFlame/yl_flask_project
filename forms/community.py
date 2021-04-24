from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class CommunityForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = StringField('Описание')
    submit = SubmitField('Применить')
    picture = FileField('Картинка', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')])


class CreateNewsByCommunity(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Только для подписчиков")
    submit = SubmitField('Применить')
    picture = FileField('Картинка', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')])
