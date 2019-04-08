from __main__ import User, Category, Item
from itemcatalog import app, engine, config
from itemcatalog.functions import save_avatar, delete_avatar, check_user
from itemcatalog.functions import save_avatar_by_url
from flask import render_template, redirect, request, url_for, flash
from flask import make_response, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, asc
from itemcatalog.forms import SignUpForm, SignInForm, UpdateProfileForm
from itemcatalog.forms import AddCategoryForm, AddItemForm, EditCategoryForm
from itemcatalog.forms import EditItemForm
from flask_login import current_user, login_user, logout_user, login_required
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime
import json

Session = sessionmaker(bind=engine)
session = Session()


# ------------- [Public routes] -------------
# home page
# this route will show all the categories
@app.route("/")
def main():
    # 1. get all categories and order by category id descending
    # about order_by:
    # https://docs.sqlalchemy.org/en/rel_1_2/orm/query.html#sqlalchemy.orm.query.Query.order_by
    # about desc:
    # https://docs.sqlalchemy.org/en/latest/core/sqlelement.html#sqlalchemy.sql.expression.desc
    categories = session.query(Category).order_by(desc(Category.id))
    # 2. get categories count:
    # https://docs.sqlalchemy.org/en/rel_1_2/orm/tutorial.html#counting
    categories.count = categories.count()
    # 3. render template
    return render_template("index.html", categories=categories)


# category page
# this route will render the items
# from a specific category
@app.route("/category/<int:c_id>/items/")
def category(c_id):
    # 1. get the category
    category = session.query(Category).filter_by(id=c_id).first()
    # 2. if the category exists
    if category:
        # category exists
        # get the items
        items = category.items.order_by(desc(Item.id)).all()
        # render the items
        return render_template("items.html", title=category.name,
                               category=category, items=items)
    else:
        # category does not exists
        # send message to the user
        flash("Category Not Found.", "danger")
        # redirect to the home page
        return redirect(url_for("main"))


# item page
# this route will render the item
@app.route("/category/<int:c_id>/item/<int:t_id>/")
def item(c_id, t_id):
    # 1. get the item from the category
    # note: if the item doesn't exists first will return None
    item = session.query(Item).filter_by(id=t_id, category_id=c_id).first()
    # 2. if the item is not none
    if item:
        # item exists
        # format created at
        created_at = '{0:%Y-%m-%d %H:%M:%S}'.format(item.created_at)
        # render the template
        return render_template("item.html", title="item", item=item,
                               created_at=created_at)
    else:
        # item does not exists
        # send a message to the user
        flash("Item Not Found.", "danger")
        # redirect to the category
        # if the category doesn't
        # exists it'll back to the home page
        return redirect(url_for("category", c_id=c_id))


# registration or sign up
# this route will render and
# handle the registration process
@app.route("/sign-up", methods=["GET", "POST"])
def signUp():
    # 1. if the user logged in redirect to the home page
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    # 2. create instance of SignUpForm
    form = SignUpForm()
    # 3. if all the data are valid
    if form.validate_on_submit():
        # create user instance
        user = User(username=form.username.data, email=form.email.data.lower())
        # hash password
        user.hash_password(form.password.data)
        # add the user to the database
        try:
            session.add(user)
            session.commit()
        except:
            # if the thread close the database by accident
            # rollback
            session.rollback()
        finally:
            # close the session
            session.close()
        # send a message to the user
        flash("Your account has been created! You are now able to sign in",
              "success")
        # redirect to sign in route
        return redirect(url_for("signIn"))
    # render the template
    return render_template("signUp.html", title="Sign Up", form=form)


# login or sign in
# this route will render
# and handle login process
@app.route("/sign-in", methods=["GET", "POST"])
def signIn():
    # 1. if the user is logged in redirect to the home page
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    # 2. create instance of SignInForm
    form = SignInForm()
    # 3. if all the data are valid
    if form.validate_on_submit():
        # get the user
        user = session.query(User).filter_by(
            username=form.username.data).first()
        # if the user exists and the password was correct
        if user and user.verify_password(form.password.data):
            # login using login_user function from flask login
            # about this function:
            # https://flask-login.readthedocs.io/en/latest/#flask_login.login_user
            # login example from flask login:
            # https://flask-login.readthedocs.io/en/latest/#login-example
            login_user(user, remember=form.remember_me.data)
            # send a message to the user
            flash("You logged in Successfully !", "success")
            # since this is a small project
            # i don't need to create safe url function
            next_page = request.args.get("next")
            # redirect to next if exists if not exists to the home page
            return redirect(next_page) if next_page else redirect(
                url_for("main"))
        else:
            # user doesn't exists
            # send this message
            flash(
                "Login Unsuccessful." +
                " please check your username and password",
                "danger")
            # redirect to the home page
            return redirect(url_for("signIn"))

    return render_template("signIn.html", title="Sign In", form=form)


# this route for google sign in
# also sorry for using google-auth library 😂😂
# there's a couple of reasons to use it:
# 1. the code in the course is for python 2
# and i want to learn python3
# 2. this library: `oauth2client` is now deprecated
# and i hate to work with a deprecated library and too old
# check this if you don't believe that:
# https://oauth2client.readthedocs.io/en/latest/
# 3. google-auth is very easy
# i know its for production apps
# but there's no choice i think 😂
@app.route("/authorized/", methods=["POST"])
def authorized():
    # 1. get the id_token from javascript request
    id_token_client = request.form["id_token"]
    password = None  # this will handle the user password
    # if id_token received
    if id_token:
        # check google docs:
        # https://developers.google.com/identity/sign-in/web/backend-auth
        try:
            id_info = id_token.verify_oauth2_token(
                id_token_client, requests.Request(),
                config["google_oauth2"]["client_id"])

            if id_info['iss'] not in ['accounts.google.com',
                                      'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            if id_info["aud"] != config["google_oauth2"]["client_id"]:
                raise ValueError('Invalid Client ID.')

            user = session.query(User).filter_by(
                email=id_info["email"]).first()
            message = ""  # this will be a message to the user
            given_name = id_info["given_name"]  # first name
            response_code = 200  # if the user new it'll be changed to 201
            # 1. check if the user doesn't exists in the database
            if user is None:
                # register & log in
                password = request.form["password"]  # get password
                # creating User instance
                user = User(username=id_info["given_name"],
                            email=id_info["email"])
                # check functions for more info about this function
                user.avatar = save_avatar_by_url(id_info["picture"])
                # hash password
                user.hash_password(password)
                # add the user
                session.add(user)
                # commit
                session.commit()
                # login using flask login
                login_user(user, remember=True)
                # setting the message
                message = "Welcome {} to our website.".format(
                    given_name)
                # setting the response 201 created
                response_code = 201
            else:
                # login using flask login
                login_user(user, remember=True)
                # setting the message
                message = "Welcome Back {}, logged in successfully!".format(
                    given_name)
            # javascript will use that dictionary
            response_dict = {
                "redirect": url_for("main"),  # redirect
                "message": message,  # message
                "category": "success"  # category
            }
            # create response
            response = make_response(json.dumps(response_dict), response_code)
            # set the headers to json
            response.headers['Content-Type'] = 'application/json'
            # return the response
            return response
        except ValueError as err:
            # any error from google return that as json with 401
            response = make_response(json.dumps(err), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            # if the error was from the session rollback
            session.rollback()
        finally:
            # close the seesion
            session.close()
    else:
        # if did not received id_token return 401
        response = make_response(json.dumps("Invalid id token"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response


# ------------- [Private routes] -------------
# logout
# this route will logout the user from flask login
@app.route("/sign-out")
@login_required
def signOut():
    # https://flask-login.readthedocs.io/en/latest/#flask_login.logout_user
    logout_user()
    flash("Logged out successfully !", "info")
    return redirect(url_for("main"))


# dashboard
# this will render statistics page
# it'll display how many categories
# does the user have
# and how many items
@app.route("/dashboard/")
@login_required
def dashboard():
    items_count = 0
    for category in current_user.categories:
        items_count = items_count + category.items.count()
    return render_template("dashboard/statistics.html", title="Statistics",
                           items_count=items_count)


# profile
# this will render
# and handling the process of update
@app.route("/dashboard/profile/", methods=["GET", "POST"])
@login_required
def profile():
    # 1. create instance of UpdateProfileForm
    form = UpdateProfileForm()
    # get the user from the database
    user = session.query(User).filter_by(id=current_user.id).first()
    # if the request method was POST
    if request.method == "POST":
        fu = form.username.data  # form username short cut
        fm = form.email.data.lower()  # form email short cut
        # i know ugly if statement but this is for pep8 !
        # this will check if the user changed something in the input
        if user.username != fu or user.email != fm or form.avatar.data:
            # validate the edit
            if form.validate_on_submit():
                # check if the user want to add avatar or change avatar
                if form.avatar.data:
                    # if the user has an avatar already
                    if user.avatar != "default.jpg":
                        # delete the old avatar
                        delete_avatar(user, session, False)
                    # save new avatar
                    avatar = save_avatar(form.avatar.data)
                    user.avatar = avatar
                # change the username
                user.username = form.username.data
                # change the email
                user.email = form.email.data
                try:
                    # commit changes
                    session.commit()
                    # send a message success
                    flash("Your account has been updated !", "success")
                except:
                    session.rollback()
                finally:
                    session.close()
                # redirect to the same page
                return redirect(url_for("profile"))
        else:
            # if the user didn't change any thing
            # redirect to the same page
            return redirect(url_for("profile"))
    # GET request
    # set the value of the username to the current username
    form.username.data = current_user.username
    # same thing with email
    form.email.data = current_user.email
    # render the template
    return render_template("dashboard/profile.html", title="Profile",
                           form=form)


# add category
# this route will render and handle the process of add a new category
@app.route("/dashboard/add/category/", methods=["GET", "POST"])
@login_required
def addCategory():
    # 1. create instance of AddCategoryForm
    form = AddCategoryForm()
    # if the request was post
    if request.method == "POST":
        # and the data are vaild
        if form.validate_on_submit():
            try:
                # create instance of Category
                category = Category(
                    name=form.name.data, user_id=current_user.id)
                # add category
                session.add(category)
                # commit
                session.commit()
                # send a message
                flash("Created Category: "+form.name.data,
                      "success")
            except:
                # if there's a problem with the session rollback
                session.rollback()
            finally:
                session.close()
            # redirect to the same page
            return redirect(url_for("addCategory"))
    # GET request render the template
    return render_template("dashboard/add_category.html", title="Add Category",
                           form=form)


# add item
# this route will render and
# handle the process of adding a new item
@app.route("/dashboard/add/item/", methods=["GET", "POST"])
@login_required
def addItem():
    # 1. create instance of AddItemForm
    form = AddItemForm()
    txt = "No Category Selected."  # this will show in select tag
    #  if the user does not have any categories
    if current_user.categories.count() <= 0:
        txt = "There's No Categories yet !"
    # choices is the option tag [(value, text)]
    # <option value="value">text</option
    choices = [(-1, txt)]
    # if the user have categories
    if current_user.categories.count() > 0:
        # update the choices
        # set the old choice + each category
        # and [how many items in the category]
        # and set the latest category at the second position
        choices = choices + [(i.id, "{} - [{}]".format(
            i.name, i.items.count()))
            for i in current_user.categories.order_by(
            desc(Category.id)).all()]
    # add the option tags to the select tag
    form.category.choices = choices

    # if the request was post
    if request.method == "POST":
        # check if the data are valid
        if form.validate_on_submit():
            try:
                # create instance of Item
                item = Item(name=form.name.data,
                            description=form.description.data,
                            category_id=form.category.data)
                # add the item
                session.add(item)
                # commit
                session.commit()
                # send the message to the user
                flash("Item %s Created" % form.name.data, "success")
            except:
                session.rollback()
            finally:
                session.close()
            # redirect to the same page
            return redirect(url_for("addItem"))
    # GET request render the template
    return render_template("dashboard/add_item.html", title="Add Item",
                           form=form)


# categories
# this route will render the categories
# that the user has been created and sorted by the latest category
# he will have three actions: `view`. `edit`, `delete`
# each action has own route
@app.route("/dashboard/categories/")
@login_required
def categories():
    # this variable will be used for the sort
    # the user can sort the categories by the latest or the older
    # by default is set to latest
    sort_by = request.args.get("sort_by") or "latest"
    # get the categories
    categories_list = current_user.categories
    # if the sort is latest
    if sort_by == "latest":
        # order by category id descending
        categories_list = categories_list.order_by(desc(Category.id))
    elif sort_by == "older":
        # order by category id ascending
        categories_list = categories_list.order_by(asc(Category.id))
    else:
        # if the user changed the query parameter
        # to something that doesn't exists
        # sort by latest category
        sort_by = "latest"
        categories_list = categories_list.order_by(desc(Category.id))
    # render the categories
    return render_template("dashboard/categories.html", title="Categories",
                           categories_list=categories_list.all(),
                           sort_by=sort_by)


# edit category
# this route will render and handle
# the process of updating
# a specific category
@app.route("/dashboard/edit/category/<int:c_id>", methods=["GET", "POST"])
@login_required
def editCategoryById(c_id):
    # 1. create instance of EditCategoryForm
    form = EditCategoryForm()
    # get the category by the id
    category = session.query(Category).filter_by(id=c_id).first()

    # if the category doesn't exists
    if category is None:
        # send this message
        flash("Invalid Category", "danger")
        # and redirect to categories
        return redirect(url_for("categories"))

    # if the category was not from the same user
    if category.user_id != current_user.id:
        # send this message
        flash("Invalid Id", "danger")
        # redirect to the categories
        return redirect(url_for("categories"))

    # if the request was POST
    if request.method == "POST":
        # check if the data is valid
        # and the name of the category was changed
        if form.validate_on_submit() and form.name.data != category.name:
            try:
                # change the name
                category.name = form.name.data
                # commit
                session.commit()
                # send message
                flash("Updated to %s !" % form.name.data, "info")
            except:
                session.rollback()
            finally:
                session.close()
            # redirect to the same page
            return redirect(url_for("editCategoryById", c_id=c_id))
        # if the user did not change the data
        else:
            # redirect to the same page
            return redirect(url_for("editCategoryById", c_id=c_id))
    # set the default value category name
    form.name.data = category.name
    # render the template
    return render_template("dashboard/edit_category.html",
                           title="Edit Category", form=form)


# edit item
# this route will render and handle
# the process of updating
# a specific item
@app.route("/dashboard/edit/item/<int:t_id>/<int:c_id>",
           methods=["GET", "POST"])
@login_required
def editItemById(t_id, c_id):
    # 1. create instance of the EditItemForm
    # category is the select tag that
    # have all the categories of the current user
    # category=c_id will set the get the category
    # from the options and select that
    form = EditItemForm(category=c_id)
    # get the item by id
    item = session.query(Item).filter_by(id=t_id).first()
    # if the item doesn't exists
    if item is None:
        # send this message
        flash("Invalid Item", "danger")
        # redirect to the category route with the category id
        return redirect(url_for("category", c_id=c_id))

    # if the item was not from the same user who logged in
    if item.category.user_id != current_user.id:
        # send this message
        flash("Invalid ID", "danger")
        # redirect to the category route with the category id
        return redirect(url_for("category", c_id=c_id))

    # if the item was from anothe category
    if item.category_id != c_id:
        # send this message
        flash("Invalid Category", "danger")
        # redirect to the category route with the category id
        return redirect(url_for("category", c_id=c_id))

    # setting up the choices
    choices = [(-1, "No Category Selected.")]
    # set the old choice + each category
    # and how many items in each category
    # order by latest category
    choices = choices + [(i.id, "{} - [{}]".format(
        i.name, i.items.count()))
        for i in current_user.categories.order_by(
        desc(Category.id)).all()]
    # add the option tags to the select tag
    form.category.choices = choices
    # if the request was post
    if request.method == "POST":
        # 1. get the item name
        name = form.name.data
        # 2. get the item description
        description = form.description.data
        # 3. create copy of the description
        # and replace &nbsp; to "" also replace any whitespace to ""
        # this from the form !!!!!!
        desc1 = str.lstrip(description.replace("&nbsp;", "").replace(" ", ""))
        # this will do the same thing but this description
        # is from the database !!!!!!!
        desc2 = str.lstrip(item.description.replace(
            "&nbsp;", "").replace(" ", ""))
        # 4. get the category
        category = form.category.data

        # 1. check if the item name is not the same name from the database
        # 2. if the len of the form description
        # is not equal the description that in the database
        # 3. the category not equal the one in the database
        if ((name != item.name) or (len(desc1) != len(desc2) or
                                       (category != item.category_id))):
            # if the data are valid
            if form.validate_on_submit():
                try:
                    # set the name
                    item.name = name
                    # set the description
                    item.description = description
                    # set the category
                    item.category_id = category
                    # commit
                    session.commit()
                except:
                    session.rollback()
                finally:
                    session.close()
                # send message
                flash("Item have been Updated !", "success")
                # redirect to the same page
                return redirect(url_for("editItemById", t_id=t_id,
                                        c_id=category))
        else:
            # if there's no change redirect to the same page
            return redirect(url_for("editItemById", t_id=t_id, c_id=c_id))

    form.name.data = item.name
    form.description.data = item.description
    return render_template("dashboard/edit_item.html", title="Edit Item",
                           form=form)


# delete category by id
# this route will delete a specific category by id
@app.route("/dashboard/delete/category/<int:c_id>/")
@login_required
def deleteCategoryById(c_id):
    # 1. get the category
    category = session.query(Category).filter_by(id=c_id).first()
    # if the category doesn't exists
    if category is None:
        # send this message
        flash("Invalid Category", "danger")
        # redirect to categories
        return redirect(url_for("categories"))

    # if the category was not from the same user
    if category.user_id != current_user.id:
        # send this message
        flash("invalid ID", "danger")
        # redirect to categories
        return redirect(url_for("categories"))

    # how many items deleted in the category
    deleted_items = 0
    # if the category have items
    if category.items.count() > 0:
        # delete all the items and this will return how many items
        deleted_items = category.items.delete()

    try:
        # delete the category
        session.delete(category)
        # commit changes
        session.commit()
        # if the category have items
        if deleted_items > 0:
            flash(
                "Category {} have been deleted and items [{}]".format(
                    category.name, deleted_items),
                "info")
        else:
            flash("Category {} have been deleted !".format(
                category.name),
                "info")
    except:
        session.rollback()
    finally:
        session.close()

    return redirect(url_for("categories"))


# delete item by id
# this will delete a specific item by id
@app.route("/dashboard/delete/item/<int:t_id>/<int:c_id>/")
@login_required
def deleteItemById(t_id, c_id):
    # 1. get the ite,
    item = session.query(Item).filter_by(id=t_id).first()

    if item is None:
        flash("Invalid Item", "danger")
        return redirect(url_for("category", c_id=c_id))

    if item.category.user_id != current_user.id:
        flash("Invalid ID", "danger")
        return redirect(url_for("category", c_id=c_id))

    if item.category.id != c_id:
        flash("Invalid Category", "danger")
        return redirect(url_for("category", c_id=c_id))

    try:
        session.delete(item)
        session.commit()
        flash("Item %s have been deleted" % item.name, "info")
    except:
        session.rollback()
    finally:
        session.close()

    return redirect(url_for("category", c_id=c_id))


# delete avatar
# this will delete avatar
@app.route("/dashboard/delete/avatar/")
@login_required
def deleteAvatar():
    # 1. get the user
    user = session.query(User).filter_by(id=current_user.id).first()
    # delete the avatar
    deleted = delete_avatar(user, session)
    # if the avatar deleted successfully
    if deleted:
        # send this message
        flash("Avatar deleted !", "info")
    # redirect to profile
    return redirect(url_for("profile"))


# ------------- [API routes] -------------

# this route will display all the categories
@app.route("/api/main/")
def mainAPI():
    # get the all latest categories
    categories = session.query(Category).order_by(desc(Category.id)).all()
    return jsonify(Category=[i.serialize for i in categories])


# this route will get all the items in a specific category
@app.route("/api/category/<int:c_id>/items/")
def categoryAPI(c_id):
    # get all items
    items = session.query(Item).filter_by(
        category_id=c_id).order_by(desc(Item.id))
    # get category
    category = session.query(Category).filter_by(id=c_id).first()
    return jsonify(Category=category.serialize,
                   Items=[i.serialize for i in items])


# this route will get a specific item
@app.route("/api/category/<int:c_id>/item/<int:t_id>/")
def itemAPI(c_id, t_id):
    # get the item
    item = session.query(Item).filter_by(
        category_id=c_id, id=t_id).first()
    # get the category
    category = session.query(Category).filter_by(id=c_id).first()
    return jsonify(Category=category.serialize, Item=item.serialize,
                   User=category.author.serialize)


# this route will check if the user exists in the database
@app.route("/api/check_user/", methods=["POST"])
def checkUser():
    # 1. get email
    email = request.form["email"]
    # check_user will take the email and the session
    # and it'll return false if the user doesn't exists
    # or true if the user exists
    status = check_user(email, session)

    # if the status true
    if status:
        return jsonify(Exists=True)

    # user doesn't exists
    return jsonify(Exists=False)
