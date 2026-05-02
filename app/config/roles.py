from enum import Enum


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


# Rights granted per role
ROLE_RIGHTS: dict[str, list[str]] = {
    Role.USER: ["getUsers", "manageUsers"],
    Role.ADMIN: ["getUsers", "manageUsers", "deleteUsers", "manageSettings"],
}

ALL_ROLES = [r.value for r in Role]
