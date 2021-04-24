from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')
    picture = FileField('Картинка', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')])