from flask import Flask
import unittest
from flask_testing import TestCase as FlaskTestCase
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer
from . import Permissions
from .models import RoleMixin, UserMixin
from werkzeug.exceptions import Forbidden
import os

app = Flask(__name__)
app.config["TESTING"] = True

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app.db")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


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

    def test_user_create_without_roles(self):
        user = User()
        db.session.add(user)
        db.session.commit()
        self.assertEqual(user.id, 1)
        self.assertEqual(user.roles, [])

    def test_user_create_with_roles(self):
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

    def test_user_create_with_a_single_role(self):
        admin_role = Role("admin")
        db.session.add(admin_role)
        db.session.commit()

        user = User(roles=admin_role)
        db.session.add(user)
        db.session.commit()

        self.assertEqual(user.id, 1)
        self.assertEqual(user.roles, [admin_role])

    def test_role_create(self):
        role = Role("admin")
        db.session.add(role)
        db.session.commit()
        self.assertEqual(role.id, 1)

    def test_user_add_roles(self):
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

    def test_user_remove_roles(self):
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

    def test_user_add_abilities(self):
        user = User()
        new_abilities = ["create_users", "set_roles", "set_abilities"]
        user.add_abilities(new_abilities)
        db.session.add(user)
        db.session.commit()

        test_user = User.query.get(1)
        self.assertEqual(sorted(new_abilities), sorted(test_user.abilities))

    def test_user_remove_abilities(self):
        user = User()
        new_abilities = ["create_users", "set_roles", "set_abilities"]
        user.add_abilities(new_abilities)
        db.session.add(user)
        db.session.commit()

        test_user = User.query.get(1)
        test_user.remove_abilities(["set_roles", "set_abilities"])
        db.session.commit()

        test_user = User.query.get(1)
        self.assertEqual(sorted(test_user.abilities), sorted(["create_users"]))

    def test_role_add_abilities(self):
        role = Role("admin")
        new_abilities = ["create_users", "set_roles", "set_abilities"]
        role.add_abilities(new_abilities)
        db.session.add(role)
        db.session.commit()
        test_role = Role.query.get(1)
        self.assertEqual(sorted(new_abilities), sorted(test_role.abilities))

    def test_role_remove_abilities(self):
        role = Role("admin")
        new_abilities = ["create_users", "set_roles", "set_abilities"]
        role.add_abilities(new_abilities)
        db.session.add(role)
        db.session.commit()

        test_role = Role.query.get(1)
        test_role.remove_abilities(["set_roles", "set_abilities"])
        db.session.add(test_role)
        db.session.commit()

        test_role = Role.query.get(1)

        self.assertEqual(sorted(test_role.abilities), sorted(["create_users"]))

    def test_user_role_ability(self):
        role = Role("admin")
        new_abilities = ["user.list", "roles"]
        role.add_abilities(new_abilities)
        db.session.add(role)
        db.session.commit()

        user = User(roles=role)
        db.session.add(user)
        db.session.commit()

        test_user = User.query.get(1)

        self.assertTrue(test_user.has_ability("user.list"))
        self.assertFalse(test_user.has_ability("user.create"))
        self.assertTrue(test_user.has_ability("roles"))
        self.assertTrue(test_user.has_ability("roles.delete"))

    def test_ability_tree(self):
        role = Role("admin")
        new_abilities = ["user.list", "roles"]
        role.add_abilities(new_abilities)
        db.session.add(role)
        db.session.commit()

        test_role = Role.query.get(1)

        self.assertTrue(test_role.has_ability("user.list"))
        self.assertFalse(test_role.has_ability("user.create"))
        self.assertTrue(test_role.has_ability("roles"))
        self.assertTrue(test_role.has_ability("roles.delete"))

    def test_ability_type(self):
        role = Role('example')
        with self.assertRaises(ValueError):
            role.add_abilities('new_ability')


perms = Permissions(User, Role, user_getter=lambda: User.query.get(1))


class PermissionsTests(DatabaseTests):
    @staticmethod
    def mock_function():
        return True

    @staticmethod
    def create_user():
        role = Role("moderator")
        role.add_abilities(["user.abilities.set"])
        db.session.add(role)
        db.session.commit()

        user = User(roles=role)
        user.add_abilities(["user.list", "roles", "user.update.self"])
        db.session.add(user)
        db.session.commit()

    def setUp(self):
        super(PermissionsTests, self).setUp()
        self.create_user()

    def test_user_has_pass(self):
        wrapped_function = perms.user_has("user.list")(self.mock_function)
        self.assertTrue(wrapped_function())

    def test_user_has_fail(self):
        wrapped_function = perms.user_has("user.update")(self.mock_function)
        self.assertRaises(Forbidden, wrapped_function)

    def test_user_has_self(self):
        wrapped_function = perms.user_has("user.update.7", 7)(self.mock_function)
        self.assertRaises(Forbidden, wrapped_function)

        wrapped_function = perms.user_has("user.update.1", 1)(self.mock_function)
        self.assertTrue(wrapped_function())

    def test_user_is_pass(self):
        wrapped_function = perms.user_is("moderator")(self.mock_function)
        self.assertTrue(wrapped_function())

    def test_user_is_fail(self):
        wrapped_function = perms.user_is("admin")(self.mock_function)
        self.assertRaises(Forbidden, wrapped_function)

    def test_check_user_has_pass(self):
        self.assertEqual(perms.check_user_has("user.list"), None)

    def test_check_user_has_fail(self):
        with self.assertRaises(Forbidden):
            perms.check_user_has("user.update")

    def test_check_user_has_self(self):
        with self.assertRaises(Forbidden):
            perms.check_user_has("user.update.7", 7)

        self.assertEqual(perms.check_user_has("user.update.1", 1), None)


if __name__ == "__main__":  # optional, but makes import and reuse easier
    unittest.main()
