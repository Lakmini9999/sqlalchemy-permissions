# SQLAlchemy-Permissions

[![Build Status](https://travis-ci.org/louistrezzini/sqlalchemy-permissions.png?branch=master)](https://travis-ci.org/louistrezzini/sqlalchemy-permissions)

SQLAlchemy-Permissions is a simple Flask permissions extension that works with [SQLAlchemy](https://github.com/zzzeek/sqlalchemy).
It also plays nicely with [Flask-SQLAlchemy](https://github.com/mitsuhiko/flask-sqlalchemy) and [Flask-Login](https://github.com/maxcountryman/flask-login) although they're not a requirement.

## Installation

Installs quickly and easily using PIP:

    pip install SQLAlchemy-Permissions

## Getting Started

1. Import Flask, Flask-SQLAlchemy, and, if you want, Flask-Login.

        from flask import Flask
        from flask.ext.login import LoginManager, current_user
        from flask.ext.sqlalchemy import SQLAlchemy

2. Import the `Permissions` object.

        from sqlalchemy_permissions import Permissions

3. Instantiate the `Permissions` object passing in your User and Role classes, and a proxy for the current user.

        perms = Permissions(User, Role, current_user)

4. Sub-class the SQLAlchemy-Permissions UserMixin and RoleMixin. Call the Mixins' `__init__` in your own `__init__`.

        from app import db
        from sqlalchemy_permissions.models import UserMixin, RoleMixin


        class Role(RoleMixin, db.Model):
            id = Column(Integer, primary_key=True)
            # Add whatever fields you need for your user class here.

            def __init__(self, ...):
                # Do your user init
                RoleMixin.__init__(self, roles)


        class User(UserMixin, db.Model):
            __roleclass__ = Role

            id = Column(Integer, primary_key=True)
            # Add whatever fields you need for your user class here.

            def __init__(self, ...):
                # Do your user init
                UserMixin.__init__(self, roles)

5. Add roles to your users and abilities to your roles. This can be done using convenience methods on the `UserMixin` and `RoleMixin` classes.

    You'll need a role to start adding abilities.

        my_role = Role('admin')

    Add abilities by passing string ability names to `role.add_abilities()`. Add the role to the session and commit when you're done.

        my_role.add_abilities('create_users', 'delete_users', 'bring_about_world_peace')
        db.session.add(my_role)
        db.session.commit()

    Add roles on an instance of your `UserMixin` sub-class.

        my_user = User()

    The `user.add_roles()` expects Role objects that will be assigned to the user. Don't forget to add and commit to the database!

        my_user.add_roles([my_role])
        db.session.add(my_user)
        db.session.commit()

    Similarly to the add methods, the classes also offer remove methods that work in the same way. Pass strings to `role.remove_abilities()` or roles to `user.remove_roles()` to remove those attributes from the objects in question.

6. Put those decorators to work! Decorate any of your views with the `user_is` or `user_has` decorators from the `Permissions` instance to limit access.

    `@user_is` decorator:

        @app.route('/admin', methods=['GET', 'POST'])
        @perms.user_is('admin')
        def admin():
            return render_template('admin.html')

    `@user_has` decorator:

        @app.route('/delete-users', methods=['GET', 'POST'])
        @perms.user_has('delete_users')
        def delete_users():
            return render_template('delete-users.html')

## Example Implementation

This is ripped almost directly from a project I'm working on that implements SQLAlchemy-Permissions. Be sure to check out the code comments for help with what does what.

#### \__init__.py

    # Import Flask, Flask-SQLAlchemy, and maybe Flask-Login
    from flask import Flask
    from flask.ext.login import LoginManager, current_user
    from flask.ext.sqlalchemy import SQLAlchemy

    # Import the Permissions object
    from flask.ext.permissions.core import Permissions

    # Here, you'll initialize your app with Flask and your database with
    # Flask-SQLAlchemy. It might look something like this:
    db = SQLAlchemy()

    app = Flask(__name__)
    app.config.from_object('config')

    db.init_app(app)
    with app.test_request_context():
        db.create_all()

    # If you're using Flask-Login, this would be a good time to set that up.
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Now, initialize a Permissions object. I've assigned it to a variable here,
    # but you don't have to do so.
    perms = Permissions(app, db, current_user)

#### models.py

    # Import your database
    from app import db
    # I'm using these handy functions for my user's password. Flask is dependent
    # on Werkzeug, so you'll have access to these too.
    from werkzeug import generate_password_hash, check_password_hash
    # Import the mixin
    from flask.ext.permissions.models import UserMixin


    class User(UserMixin):
        # Add whatever fields you need for your user class. Here, I've added
        # an email field and a password field
        email = db.Column(db.String(120), unique=True)
        pwdhash = db.Column(db.String(100))

        def __init__(self, email, password, roles=None):
            self.email = email.lower()
            self.set_password(password)
            # Be sure to call the UserMixin's constructor in your class constructor
            UserMixin.__init__(self, roles)

        def set_password(self, password):
            self.pwdhash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.pwdhash, password)

        def __str__(self):
            return self.email

#### views.py

    # Import the decorators
    from flask.ext.permissions.decorators import user_is, user_has

    # Set up your route and decorate it
    @app.route('/admin', methods=['GET', 'POST'])
    # Pass the name of the role you want to test for to the decorator
    @user_is('admin')
    def admin():
        return render_template('admin.html')

    # Here's an example of user_has
    @app.route('/delete-users', methods=['GET', 'POST'])
    # Pass the name of the ability you want to test for to the decorator
    @user_has('delete_users')
    def delete_users():
        return render_template('delete-users.html')

## License

This extension is available under the MIT license. See the LICENSE file for more details.

## Thank You

I hope you will enjoy this project. I built SQLAlchemy-Permissions because I couldn't find a simple yet flexible permissions system for Flask and SQLAlchemy.
This does everything I need and implements ACL, yet the implementation is very easy to understand.

This is my first open source library. Pull requests and comments are welcome and appreciated!
