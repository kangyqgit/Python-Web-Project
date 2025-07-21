from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo



class LoginForm(FlaskForm):
    """登录表单模型"""
    username = StringField('用户名：', validators=[DataRequired()])
    password = PasswordField('密 码：', validators=[
        DataRequired(),
        Length(min=6, message='密码最少6位')
    ])
    submit = SubmitField('登 录')