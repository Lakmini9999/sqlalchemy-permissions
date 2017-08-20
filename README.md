# SQLAlchemy-Permissions

[![Build Status](https://travis-ci.org/LouisTrezzini/sqlalchemy-permissions.png?branch=master)](https://travis-ci.org/LouisTrezzini/sqlalchemy-permissions)

SQLAlchemy-Permissions is a simple Flask permissions extension that works with [SQLAlchemy](https://github.com/zzzeek/sqlalchemy).
It also plays nicely with [Flask-SQLAlchemy](https://github.com/mitsuhiko/flask-sqlalchemy) and [Flask-Login](https://github.com/maxcountryman/flask-login) although they're not a requirement.

## Features

- User and Role mixins, which can both be assigned abilities
- **Tree-based ability checking** If you ask for ability `entity.update.37`, this will happen
    1. Merge User and User's roles abilities
    2. If the user has `entity.update.37`, OK
    3. If the user has a parent ability, e.g. `entity.update` or `entity`, OK
    4. It the user has the `entity.update.self` and is the owner of the entity, OK
    5. Otherwise raises a Forbidden exception

## Installation

Installs quickly and easily using PIP:

```bash
pip install SQLAlchemy-Permissions
```

## Getting Started

1. Import Flask, Flask-SQLAlchemy, and, if you want, Flask-Login.

```python
from flask import Flask
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
```

2. Import the `Permissions` object.

```python
from sqlalchemy_permissions import Permissions
```

3. Instantiate the `Permissions` object passing in your User and Role classes, and a proxy for the current user.

```python
perms = Permissions(User, Role, current_user)
```

4. Sub-class the SQLAlchemy-Permissions UserMixin and RoleMixin.
Call the Mixins' `__init__` in your own `__init__`.
Don't forget to add a `__roleclass__` attribute to your User class.

```python
from app import db
from sqlalchemy_permissions.models import UserMixin, RoleMixin


class Role(RoleMixin, db.Model):
    id = Column(Integer, primary_key=True)
    # Add whatever fields you need for your user class here.

    def __init__(self, ...):
        # Do your user init
        RoleMixin.__init__(self, roles)


class User(UserMixin, db.Model):
    # REQUIRED
    __roleclass__ = Role

    id = Column(Integer, primary_key=True)
    # Add whatever fields you need for your user class here.

    def __init__(self, ...):
        # Do your user init
        UserMixin.__init__(self, roles)
```

5. Add roles to your users and abilities to your roles. This can be done using convenience methods on the `UserMixin` and `RoleMixin` classes.

You'll need a role to start adding abilities.

```python
my_role = Role("admin")
```

Add abilities by passing string ability names to `role.add_abilities()`. Add the role to the session and commit when you're done.

```python
my_role.add_abilities(["create_users", "delete_users", "bring_about_world_peace"])
db.session.add(my_role)
db.session.commit()
```

Add roles on an instance of your `UserMixin` sub-class.

```python
my_user = User()
```

The `user.add_roles()` expects Role objects that will be assigned to the user. Don't forget to add and commit to the database!

```python
my_user.add_roles([my_role])
db.session.add(my_user)
db.session.commit()
```

Similarly to the add methods, the classes also offer remove methods that work in the same way. Pass strings to `role.remove_abilities()` or roles to `user.remove_roles()` to remove those attributes from the objects in question.

6. Put those decorators to work! Decorate any of your views with the `user_is` or `user_has` decorators from the `Permissions` instance to limit access.

`@user_is` decorator:

```python
@app.route("/admin", methods=["GET", "POST"])
@perms.user_is("admin")
def admin():
    return render_template("admin.html")
```

`@user_has` decorator:

```python
@app.route("/delete-users", methods=["GET", "POST"])
@perms.user_has("delete_users")
def delete_users():
    return render_template("delete-users.html")
```

## License

This extension is available under the MIT license. See the LICENSE file for more details.

## Thank You

I hope you will enjoy this project. I built SQLAlchemy-Permissions because I couldn't find a simple yet flexible permissions system for Flask and SQLAlchemy.
This does everything I need and implements ACL, yet the implementation is very easy to understand.

This is my first open source library. Pull requests and comments are welcome and appreciated!
