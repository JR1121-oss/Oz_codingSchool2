import enum

class GenderEnum(str, enum.Enum):
    M = "male"
    F = "female"

class RoleEnum(str, enum.Enum):
    PENDING = "pending"
    STAFF = "staff"
    ADMIN = "admin"

class DepartmentEnum(str, enum.Enum):
    MEDICAL = "medical team"
    DEV = "developer"
    RESEARCH = "researcher"
    