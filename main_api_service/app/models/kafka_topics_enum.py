from enum import Enum

class KafkaTopicsEnum(str, Enum):
    account_registered = "account_registered"
    account_confirmed = "account_confirmed"
    change_email = "change_email"
    change_password = "change_password"