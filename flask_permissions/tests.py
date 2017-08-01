from flask import Flask
import unittest
from flask_testing import TestCase as FlaskTestCase
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer
from . import Permissions
from werkzeug.exceptions import Forbidden
import os

app = Flask(__name__)
app.config["TESTING"] = True

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app.db")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

perms = Permissions(app, db)

from .models import RoleMixin, UserMixin


class Role(RoleMixin, db.Model):
    id = Column(Integer, primary_key=True)


class User(UserMixin, db.Model):
    __roleclass__ = Role

    id = Column(Integer, primary_key=True)


class DatabaseTests(FlaskTestCase):
    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class ModelsTests(DatabaseTests):
    def test_user(self):
        user = User()
        db.session.add(user)
        db.session.commit()
        self.assertEqual(user.id, 1)

    def test_new_user_with_roles_assigned(self):
        role_names = ["admin", "superadmin"]
        roles = []

        for role_name in role_names:
            new_role = Role(role_name)
            roles.append(new_role)
            db.session.add(new_role)
            db.session.commit()

        user = User(roles=roles)
        db.session.add(user)
        db.session.commit()

        self.assertEqual(user.id, 1)
        self.assertEqual(user.roles, roles)

    def test_new_user_with_a_single_role_assigned(self):
        admin_role = Role("admin")
        db.session.add(admin_role)
        db.session.commit()

        user = User(roles=admin_role)
        db.session.add(user)
        db.session.commit()

        self.assertEqual(user.id, 1)
        self.assertEqual(user.roles, [admin_role])

    def test_role(self):
        role = Role("admin")
        db.session.add(role)
        db.session.commit()
        self.assertEqual(role.id, 1)

    def test_add_roles_with_existing_roles(self):
        role_names = ["admin", "superadmin"]
        roles = []

        for role_name in role_names:
            new_role = Role(role_name)
            roles.append(new_role)
            db.session.add(new_role)
            db.session.commit()

        user = User()
        db.session.add(user)
        db.session.commit()

        user.add_roles(roles)
        db.session.commit()

        user = User.query.get(1)

        self.assertEqual(user.id, 1)
        self.assertEqual(user.roles, roles)

    def test_remove_roles(self):
        role_names = ["admin", "superadmin"]
        roles = []

        for role_name in role_names:
            new_role = Role(role_name)
            roles.append(new_role)
            db.session.add(new_role)
            db.session.commit()

        user = User(roles=roles)
        db.session.add(user)
        db.session.commit()

        user.remove_roles([roles[0]])
        db.session.commit()

        user = User.query.get(1)

        self.assertEqual(user.id, 1)
        self.assertEqual(len(user.roles), 1)
        self.assertEqual(user.roles[0].name, "superadmin")

    def test_add_abilities_with_nonexisting_abilities(self):
        role = Role("admin")
        new_abilities = ["create_users", "set_roles", "set_abilities"]
        role.add_abilities(new_abilities)
        db.session.add(role)
        db.session.commit()
        test_role = Role.query.get(1)
        self.assertEqual(sorted(new_abilities), sorted(test_role.abilities))

    def test_remove_abilities(self):
        role = Role("admin")
        new_abilities = ["create_users", "set_roles", "set_abilities"]
        role.add_abilities(new_abilities)
        db.session.add(role)
        db.session.commit()

        ability_remove_role = Role.query.get(1)
        ability_remove_role.remove_abilities(["set_roles", "set_abilities"])
        db.session.add(ability_remove_role)
        db.session.commit()

        test_role = Role.query.get(1)

        self.assertEqual(sorted(test_role.abilities), sorted(["create_users"]))


# class DecoratorsTests(DatabaseTests):
#
#     def mock_function(self):
#         return True
#
#     def create_user(self):
#         role = Role("admin")
#         new_abilities = ["create_users", "set_roles", "set_abilities"]
#         for ability in new_abilities:
#             new_ability = Ability(ability)
#             db.session.add(new_ability)
#             db.session.commit()
#         role.add_abilities(*new_abilities)
#         db.session.add(role)
#         db.session.commit()
#
#         user = User(roles="admin")
#         db.session.add(user)
#         db.session.commit()
#
#     def return_user(self):
#         user = User.query.get(1)
#         return user
#
#     def setUp(self):
#         super(DecoratorsTests, self).setUp()
#         self.create_user()
#
#     def test_user_has_pass(self):
#         wrapped_function = user_has("create_users", self.return_user)(self.mock_function)
#         self.assertTrue(wrapped_function())
#
#     def test_user_has_fail(self):
#         wrapped_function = user_has("edit", self.return_user)(self.mock_function)
#         self.assertRaises(Forbidden, wrapped_function)
#
#     def test_user_is_pass(self):
#         wrapped_function = user_is("admin", self.return_user)(self.mock_function)
#         self.assertTrue(wrapped_function())
#
#     def test_user_is_fail(self):
#         wrapped_function = user_is("user", self.return_user)(self.mock_function)
#         self.assertRaises(Forbidden, wrapped_function)


if __name__ == "__main__":  # optional, but makes import and reuse easier
    unittest.main()
