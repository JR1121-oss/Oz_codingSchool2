import enum

class GenderEnum(str, enum.Enum):
    M = "M"
    F = "F"

class RoleEnum(str, enum.Enum):
    PENDING = "PENDING"
    STAFF = "STAFF"
    ADMIN = "ADMIN"

class DepartmentEnum(str, enum.Enum):
    MEDICAL = "MEDICAL"
    DEV = "DEV"
    RESEARCH = "RESEARCH"
    