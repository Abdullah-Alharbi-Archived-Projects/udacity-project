from itemcatalog.models import User, Category, Item
from itemcatalog import app
from urllib.request import urlretrieve
import os
import binascii


# this function will take file name and get the extantion and then
# it'll generate new name within the extantion of the file
def generate_name(filename):
    # 1. generate 50 char
    random = binascii.b2a_hex(os.urandom(50)).decode("utf-8")
    # 2. get the extantion
    fname, ext = os.path.splitext(filename)
    # 3. create the string
    # note: i've tried to use the + sign but i got error
    new_filename = "{}{}".format(random, ext)
    # 4. return the name
    return new_filename


# this function will take file name
# and generate a path within the file name
# parameter: filename
def path(filename):
    # more about join function
    # https://docs.python.org/3.5/library/os.path.html?highlight=os%20path%20join#os.path.join
    return os.path.join(app.root_path, 'static/avatars',
                        filename)


# this function will save an image by the url
# parameter: url
def save_avatar_by_url(url):
    # 1. generate name
    # note: [-1] will get the last element
    file_name = generate_name(url.split("/")[-1])
    # 2. generate path
    avatar_path = path(file_name)
    # 3. save image using urllib
    urlretrieve(
        url, avatar_path)
    #  4. return file name to save it in the database
    return file_name


# this function will handle upload image using the form
# parameter: image file
def save_avatar(form_avatar):
    # 1. generate file name
    file_name = generate_name(form_avatar.filename)
    # 2. generate path
    avatar_path = path(file_name)
    # 3. save the image
    form_avatar.save(avatar_path)
    # 4. return the name to save it in the database
    return file_name


# this function will delete the avatar
# parameters: user_object, session, change default true
def delete_avatar(user, session, change=True):
    # 1. check if the avatar is the default
    if user.avatar == "default.jpg":
        return False

    # 2. if the avatar exists
    if os.path.exists(app.root_path+"/static/avatars/"+user.avatar):
        # remove the file
        os.remove(app.root_path+"/static/avatars/"+user.avatar)
        # if change was true
        if change:
            try:
                # change the avatar to the default image
                user.avatar = "default.jpg"
                session.commit()
            except:
                # if the thread close the database by accident
                # rollback
                session.rollback()
            finally:
                # close
                session.close()

        return True

    # if the avatar doesn't exists return false
    return False


# this function will check if the user
# doesn't exists it'll return false otherwise it'll return true
# parameters: email, session
def check_user(email, session):
    # 1. get the user
    # note: first function will return None if the user doesn't exists
    user = session.query(User).filter_by(email=email).first()
    # if there's no user with that email
    if user is None:
        return False

    return True
