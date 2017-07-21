from sqlalchemy import Column, Integer, Table, ForeignKey, String, Text
from sqlalchemy.orm import relationship, validates, object_session
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy


class RoleMixin:
    """
    Subclass this for your roles
    """
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    abilities_text = Column(Text())

    def __init__(self, name=None):
        if name:
            self.name = name.lower()

    @property
    def abilities(self):
        return set(self.abilities_text.split("\n"))

    @abilities.setter
    def abilities(self, new_abilities):
        self.abilities_text = "\n".join(new_abilities)

    def add_abilities(self, new_abilities):
        self.abilities = self.abilities.update(new_abilities)

    def remove_abilities(self, old_abilities):
        self.abilities = self.abilities.difference_update(old_abilities)

    def __str__(self):
        return self.name


class UserMixin:
    """
    Subclass this for your user class
    """
    @declared_attr
    def roles(self):
        users_roles_table = Table(
            "%s_roles" % self.__tablename__,
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("%s_id" % self.__tablename__, Integer, ForeignKey("%s.id" % self.__tablename__)),
            Column("role_id", Integer, ForeignKey("roles.id")),
        )
        return relationship("Role", secondary=users_roles_table, backref="users")

    def __init__(self, roles=None):
        # If only a string is passed for roles, convert it to a list containing
        # that string
        if roles and isinstance(roles, RoleMixin):
            roles = [roles]

        # If a sequence is passed for roles (or if roles has been converted to
        # a sequence), fetch the corresponding database objects and make a list
        # of those.
        if roles and all(isinstance(role, RoleMixin) for role in roles):
            self.roles = roles

    def add_roles(self, roles):
        self.roles.extend([role for role in roles if role not in self.roles])

    def remove_roles(self, roles):
        self.roles = [role for role in self.roles if role not in roles]
