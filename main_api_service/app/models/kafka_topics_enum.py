from enum import Enum

class KafkaTopicsEnum(str, Enum):
    account_registered = "account_registered"
    account_confirmed = "account_confirmed"
    change_email = "change_email"
    email_changed = "email_changed"
    change_password = "change_password"
    password_changed = "password_changed"
    reset_password = "reset_password"
    remove_user_business_entity = "remove_user_business_entity"