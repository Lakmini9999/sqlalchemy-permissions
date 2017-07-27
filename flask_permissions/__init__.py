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
                current_user = self.get_user()

                if current_user and current_user.has_ability(desired_ability):
                    return func(*args, **kwargs)
                else:
                    raise Forbidden()

            return inner

        return wrapper

    def user_is(self, role):
        """
        Take a role and returns the function if the user has that role
        Raise a Forbidden exception otherwise
        """

        def wrapper(func):
            @wraps(func)
            def inner(*args, **kwargs):
                desired_role = self.__role_class.query.filter_by(name=role).first()
                current_user = self.get_user()
                if current_user and current_user.has_role(desired_role):
                    return func(*args, **kwargs)
                raise Forbidden()

            return inner

        return wrapper

    def trust_user_has(self, desired_ability):
        current_user = self.get_user()

        if not (current_user and current_user.has_ability(desired_ability)):
            raise Forbidden()
