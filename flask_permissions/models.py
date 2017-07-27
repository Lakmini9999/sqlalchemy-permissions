from sqlalchemy import Column, Integer, Table, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr


class AbilitiesMixin:
    abilities_text = Column(Text(), default="")

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

    def has_ability(self, ability):
        if ability in self.abilities:
            return True

        while "." in ability:
            ability, ability_suffix = ability.split(".", 1)
            if ability in self.abilities:
                return True

        return False


class RoleMixin(AbilitiesMixin):
    """
    Subclass this for your roles
    """
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)

    def __init__(self, name=None):
        if name:
            self.name = name.lower()

    def __str__(self):
        return self.name


class UserMixin(AbilitiesMixin):
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
            UniqueConstraint("%s_id" % self.__tablename__, "role_id"),
        )
        return relationship("Role", secondary=users_roles_table, backref="users")

    def __init__(self, roles=None):
        # If only a string is passed for roles, convert it to a list containing
        # that string
        if roles and isinstance(roles, RoleMixin):
            self.roles = [roles]
            return

        # If a sequence is passed for roles (or if roles has been converted to
        # a sequence), fetch the corresponding database objects and make a list
        # of those.
        if roles and all(isinstance(role, RoleMixin) for role in roles):
            self.roles = roles
            return

        if roles:
            raise ValueError("Invalid roles")

    def add_roles(self, roles):
        if not isinstance(roles, (list, tuple)):
            raise ValueError("Invalid roles")

        self.roles.extend([role for role in roles if role not in self.roles])

    def remove_roles(self, roles):
        if not isinstance(roles, (list, tuple)):
            raise ValueError("Invalid roles")

        self.roles = [role for role in self.roles if role not in roles]

    def has_role(self, role):
        return role in self.roles

    @property
    def abilities(self):
        user_abilities = super().abilities

        for role in self.roles:
            user_abilities.update(role.abilities)

        return user_abilities
