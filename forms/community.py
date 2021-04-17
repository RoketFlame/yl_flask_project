from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class CommunityForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = StringField('Описание')
    submit = SubmitField('Применить')


class CreateNewsByCommunity(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Только для подписчиков")
    submit = SubmitField('Применить')
