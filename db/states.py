from enum import Enum


class UserStates(Enum):
    CREATED = 'CREATED'
    REGISTERED = 'REGISTERED'
    ORDERING = 'ORDERING'
    JOINED = 'JOINED'
