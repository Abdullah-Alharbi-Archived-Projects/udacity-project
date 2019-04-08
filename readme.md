# Item Catalog version 9 ?
---
**project start date: Thursday, November 22, 2018<br>
Project deadline: Tuesday, October 30, 2018<br>
Number of attempts: 9**
## 1. Libraries i have used to build this project ??:
#### Front-End:
- [Bootstrap](https://getbootstrap.com/docs/4.1/getting-started/introduction/)
- [Jquery](https://api.jquery.com/)
- [Froala](https://www.froala.com/wysiwyg-editor)
- [Font-awesome](https://fontawesome.com/)
#### Back-End:
- [Flask](http://flask.pocoo.org/)
- [Jinja2](http://jinja.pocoo.org/docs/2.10/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Flask-Wtf](https://flask-wtf.readthedocs.io/en/stable/)
- [Wtforms](https://wtforms.readthedocs.io/en/stable/)
- [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
- [Google-auth](https://google-auth.readthedocs.io/en/latest/)
- [Passlib](https://passlib.readthedocs.io/en/stable/)
#### Others:
- [Integrating Google Sign-In](https://developers.google.com/identity/sign-in/web/sign-in)
## Sections:
1. **[?] setup database**
2. **[?] create forms classes**
3. **[?] create routes**
4. **[?] add sign in with google**
## [Some pictures](https://imgur.com/a/BL2E2Os)
## please install these libraries from vagrant python version is 3.5.2:
**note: flask-wtf will install WTforms**
```python3
pip3 install flask-wtf flask-login google-auth passlib --upgrade --user
```
#### Section 1. setup database:
**I started to create the database first before working with \
anything that was the first step file: `/itemcatalog/models.py`**
##### 1. **[?]  User Model**
**First is the user table and these are the columns in the table:**
1. **id int primary key**
2. **username string(50) unique not null**
3. **email string(120) unique not null**
4. **password string(77) unique not null**
5. **avatar string(50) default "default.jpg" not null**
6. **created_at dateTime default now() not null**
7. **categories relationship with Category**
#### Methods in User model:
**note: password: plain text**
1. **hash_password(string password)**
2. **verify_password(string password)**
##### 2. **[?] Category Model**
1. **id int primary key**
2. **name string(50) unique not null**
3. **user_id int foreign key(User.id) not null**
4. **created_at dateTime default now() not null**
5. **items relationship with Item**

##### 3. **[?] Item Model**
1. **id int primary key**
2. **name string(50) unique not null**
3. **description Text not null**
4. **category_id int foreign key(Category.id) not null**
---
#### Section 2. create forms classes:
**next step was to create the forms as \
i read in flask-wtf and wtforms \
i have to create class for each form \
[create forms](https://flask-wtf.readthedocs.io/en/stable/quickstart.html#creating-forms):
[wtforms](https://wtforms.readthedocs.io/en/stable/forms.html#defining-forms)
each class will generate inputs
file: `/itemcatalog/forms.py`**
1. **Sign up Class**
    * **Username: text**
    * **Email: email**
    * **Password: password**
    * **Confirm Password: password**
    * **Submit**
2. **Sign in Class**
    * **Username: text**
    * **Password: password**
    * **Submit**
3. **Update Profile Class**
    * **Username: text**
    * **Email: text**
    * **Upload Image [`jpg`, `png`]: file**
    * **Submit**
4. **Add Category Class**
    * **Name: text**
    * **Submit**
5. **Add Item Class**
    * **Item name: text**
    * **Description: textarea**
    * **Category: select**
    * **Submit**
6. **Edit Category Class**
    * **Category name: text**
    * **Submit**
7. **Edit Item Class**
    * **Item name: text**
    * **Description: textarea**
    * **Category: select**
    * **Submit**
---
#### Section 3. create routes:
**next the routes i started first to create the public routes, \
then priavte, and finally the endpoints file: `/itemcatalog/routes.py` \
Routes:**
##### Public [6]:
- `main("/")`
- `category("/category/<int:c_id>/items/")`
- `item("/category/<int:c_id>/item/<int:t_id>/")`
- `signUp("/sign-up", methods=["GET", "POST"])`
- `signIn("/sign-in", methods=["GET", "POST"])`
- `authorized("/authorized/", methods=["POST"])`
##### Priavte [11]:
- `signOut("/sign-out")`
- `dashboard("/dashboard/")`
- `profile("/dashboard/profile/")`
- `addCategory("/dashboard/add/category/")`
- `addItem("/dashboard/add/item/", methods=["GET", "POST"])`
- `categories("/dashboard/categories/")`
- `editCategoryById("/dashboard/edit/category/<int:c_id>", methods=["GET", "POST"])`
- `editItemById("/dashboard/edit/item/<int:t_id>/<int:c_id>", methods=["GET", "POST"])`
- `deleteCategoryById("/dashboard/delete/category/<int:c_id>/")`
- `deleteItemById("/dashboard/delete/item/<int:t_id>/<int:c_id>/")`
- `deleteAvatar("/dashboard/delete/avatar/")`
##### API [4]:
- `mainAPI("/api/main/")`
- `categoryAPI("/api/category/<int:c_id>/items/")`
- `itemAPI("/api/category/<int:c_id>/item/<int:t_id>/")`
- `checkUser("/api/check_user/", methods=["POST"])`
