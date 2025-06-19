from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запам\'ятати мене')
    submit = SubmitField('Увійти')


class RegistrationForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Підтвердіть пароль',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зареєструватися')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Це ім\'я вже використовується. Оберіть інше.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Цей email вже зареєстрований. Оберіть інший.')


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Зміст', validators=[DataRequired()])
    submit = SubmitField('Зберегти')


class CommentForm(FlaskForm):
    content = TextAreaField('Коментар', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Додати коментар')


class UserForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль (залиште порожнім, якщо не змінюєте)')
    is_admin = BooleanField('Права адміністратора')
    submit = SubmitField('Зберегти')