from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired, file_required
from wtforms.validators import DataRequired, Length
from wtforms.validators import Email, EqualTo, ValidationError
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import TextAreaField, SelectField
from sqlalchemy.orm import sessionmaker
from __main__ import engine
from __main__ import User, Category, Item
from flask_login import current_user

Session = sessionmaker(bind=engine)
session = Session()


# Sign up form
# this will be use in sign up route
class SignUpForm(FlaskForm):
    # 1. username: required,
    # length must be greater than 2 and less than 50
    username = StringField("Username", validators=[DataRequired(),
                                                   Length(min=2, max=50)])
    # 2. email: required,
    # Email() will check if it's a valid email
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    # password: required, length must be greater than 6
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=6)])
    # confirm password: required, must be equal to password
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(),
                                                 EqualTo("password")])
    # finally a button
    submit = SubmitField("Sign up")

    # this will check if the username is exists in the database
    def validate_username(self, username):
        # 1. get user by username
        user = session.query(User).filter_by(username=username.data).first()
        # 2. if the user exists
        if user:
            # 3. raise this error
            raise ValidationError(
                'The username is taken! Please choose a different username.')

    # this will check if the email is exists
    def validate_email(self, email):
        # 1. get user by email
        user = session.query(User).filter_by(email=email.data).first()
        # 2. if user exists
        if user:
            # 3. raise this error
            raise ValidationError('The email is already exists !')


# Sign in form
# this will be use in sign in route
class SignInForm(FlaskForm):
    # 1. username: required,
    # length must be greater than 2 and less than 50
    username = StringField("Username", validators=[DataRequired(),
                                                   Length(min=2, max=50)])
    # password: required, length must be greater than 6
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=6)])
    # remember me check box
    remember_me = BooleanField("Remember Me")
    # button sign in
    # note: sign in with google button
    # is rendered from the platform.js
    submit = SubmitField("Sign in")

# profile form
# this will be use in profile route


class UpdateProfileForm(FlaskForm):
    # 1. username: required,
    # length must be greater than 2 and less than 50
    username = StringField("Username", validators=[DataRequired(),
                                                   Length(min=2, max=50)])
    # 2. email: required,
    # Email() will check if it's a valid email
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    # 3. avatar: not required
    avatar = FileField('avatar', validators=[FileAllowed(['jpg', 'png'])])
    # 4. submit
    submit = SubmitField("Save")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = session.query(User).filter_by(
                username=username.data).first()
            if user:
                raise ValidationError(
                    'The username is taken! Please choose a different username'
                )

    def validate_email(self, email):
        if email.data != current_user.email:
            user = session.query(User).filter_by(
                email=email.data).first()
            if user:
                raise ValidationError('The email is already exists !')


# add category
# this wil be use in the add category route
class AddCategoryForm(FlaskForm):
    # 1. name: required,
    # length must be greater than 2 and less than 50
    name = StringField("Category Name:", validators=[
                       DataRequired(), Length(min=2, max=50)])
    # 2. submit
    submit = SubmitField("Create !")

    # this will check if the category name is exists
    def validate_name(self, name):
        # 1. get the category by name
        category = session.query(Category.name).filter_by(
            name=name.data).first()
        # 2. if exists
        if category:
            # raise error
            raise ValidationError("The Category is already exists !")


# add item
# this wil be use in the add item route
class AddItemForm(FlaskForm):
    # 1. name: required,
    # length must be greater than 2 and less than 50
    name = StringField("Item Name:", validators=[
                       DataRequired(), Length(min=2, max=50)])
    # 2. textarea: required
    description = TextAreaField("Description:", validators=[DataRequired()])
    # 3. category: required,
    # value of option must be integer
    category = SelectField("Category:", validators=[
                           DataRequired()], coerce=int)
    # submit
    submit = SubmitField("Create !")

    # this will check if the item name is already exists
    def validate_name(self, name):
        # 1. get the item by name
        item = session.query(Item).filter_by(name=name.data).first()
        # 2. if that item exists
        if item:
            # raise error
            raise ValidationError("The item is already exists")

    # this will check if the category exists and the id is valid
    def validate_category(self, category):
        # 1. the default option value is -1
        # so that's mean the user didn't select any category
        if category.data == -1:
            raise ValidationError("Please select a category !")

        # 2. if the user select a category
        # get that category
        category_check = session.query(
            Category).filter_by(id=category.data).first()

        # 2. make sure the category is exists
        if category_check is None:
            raise ValidationError("invalid Category !")
        # 3. and also the category created by the same user who logged in !
        if category_check.user_id != current_user.id:
            raise ValidationError("invalid ID !")


# edit category
# this wil be use in the edit category route
class EditCategoryForm(FlaskForm):
    # 1. name: required,
    # length must be greater than 2 and less than 50
    name = StringField("Category Name:", validators=[
                       DataRequired(), Length(min=2, max=50)])
    # 2. submit
    submit = SubmitField("Save")


# edit item
# this wil be use in the edit item route
class EditItemForm(FlaskForm):
    # 1. name: required,
    # length must be greater than 2 and less than 50
    name = StringField("Item Name:", validators=[
                       DataRequired(), Length(min=2, max=50)])
    # 2. description: required
    description = TextAreaField("Description:", validators=[DataRequired()])
    # 3. category: required,
    # value of option must be integer
    category = SelectField("Category:", validators=[
                           DataRequired()], coerce=int)
    # 4. submit
    submit = SubmitField("Save")

    # check category
    def validate_category(self, category):
        if category.data == -1:
            raise ValidationError("Please select a category !")

        category_check = session.query(
            Category).filter_by(id=category.data).first()

        if category_check is None:
            raise ValidationError("invalid Category !")

        if category_check.user_id != current_user.id:
            raise ValidationError("invalid ID !")
