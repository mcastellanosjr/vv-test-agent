from enum import Enum


class ValidationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_RUN = "not_run"