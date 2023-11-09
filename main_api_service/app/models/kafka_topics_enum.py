from enum import Enum

class KafkaTopicsEnum(str, Enum):
    account_registered = "account_registered"
    account_confirmed = "account_confirmed"