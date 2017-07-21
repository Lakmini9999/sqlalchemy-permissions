from functools import wraps
from werkzeug.exceptions import Forbidden


class Permissions:
    def __init__(self, user_class, role_class, user_getter=None):
        self.__user_class = user_class
        self.__role_class = role_class

        self.user_getter = user_getter

    def get_user(self):
        if self.user_getter:
            return self.user_getter()
        else:
            try:
                from flask.ext.login import current_user
                return current_user
            except ImportError:
                raise ImportError("User argument not passed and Flask-Login current_user could not be imported.")

    def user_has(self, desired_ability):
        """
        Takes an ability (a string name of either a role or an ability) and returns the function if the user has that ability
        """

        def wrapper(func):
            @wraps(func)
            def inner(*args, **kwargs):
                user_abilities = set()
                current_user = self.get_user()

                if current_user:
                    for role in current_user.roles:
                        user_abilities.update(role.abilities)

                if desired_ability in user_abilities:
                    return func(*args, **kwargs)
                else:
                    raise Forbidden()

            return inner

        return wrapper

    def user_is(self, role):
        """
        Takes an role (a string name of either a role or an ability) and returns the function if the user has that role
        """

        def wrapper(func):
            @wraps(func)
            def inner(*args, **kwargs):
                desired_role = self.__role_class.query.filter_by(name=role).first()
                current_user = self.get_user()
                if current_user and desired_role in current_user.roles:
                    return func(*args, **kwargs)
                raise Forbidden()

            return inner

        return wrapper
