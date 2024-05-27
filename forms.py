from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Email, Length
from flask_ckeditor import CKEditorField
from wtforms import StringField, PasswordField, EmailField, SubmitField, SelectField, TextAreaField, HiddenField, \
    ValidationError
from flask_wtf.file import FileField, FileAllowed


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Length(max=100)])
    profile_pic = FileField('Profile Picture',
                            validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Create Account")

    def validate_profile_pic(self, field):
        if field.data:
            filename = field.data.filename
            if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'png', 'jpeg']):
                raise ValidationError('Invalid file format. Please upload an image file.')


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ForgotPasswordForm(FlaskForm):
    email = EmailField("Enter your Registered Email", validators=[DataRequired()])
    submit = SubmitField("Send")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")


class OtpForm(FlaskForm):
    otp = StringField("Enter OTP", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    recipe_name = StringField("Name of Recipe", validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=200)])
    img_url = FileField('Recipe photo',
                        validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    yt = StringField('Youtube Link (* Optional But Better if you provide)')
    steps = CKEditorField('Process to make the Recipe', validators=[DataRequired()])
    submit = SubmitField('Post')

    def validate_profile_pic(self, field):
        if field.data:
            filename = field.data.filename
            if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'png', 'jpeg']):
                raise ValidationError('Invalid file format. Please upload an image file.')


class CreateCommentForm(FlaskForm):
    content = StringField('Comment', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField("Add Comment")


class FollowUserForm(FlaskForm):
    user_to_follow = SelectField('User to Follow', coerce=int, validators=[DataRequired()])
    submit = SubmitField("Follow")


class LikePostForm(FlaskForm):
    post_id = HiddenField("Post ID", validators=[DataRequired()])
    submit = SubmitField("Like")


class ProfilePP(FlaskForm):
    profile_pic = FileField('New Profile Picture',
                            validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField("Update")

    def validate_profile_pic(self, field):
        if field.data:
            filename = field.data.filename
            if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'png', 'jpeg']):
                raise ValidationError('Invalid file format. Please upload an image file.')


class AiForm(FlaskForm):
    input = StringField('Enter The Ingredients: ', validators=[DataRequired()])
    submit = SubmitField("Enter")



"""
DishDuo

Copyright (C) 2024 Dev Singh

All rights reserved.

This file is part of DishDuo.

DishDuo can not be copied and/or distributed without the express
permission of Dev Singh.
"""