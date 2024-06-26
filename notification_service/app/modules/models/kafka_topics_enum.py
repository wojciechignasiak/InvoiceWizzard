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
    user_business_entity_removed = "user_business_entity_removed"
    remove_external_business_entity = "remove_external_business_entity"
    external_business_entity_removed = "external_business_entity_removed"
    remove_invoice = "remove_invoice"
    invoice_removed = "invoice_removed"
    extract_invoice_data = "extract_invoice_data"
    unable_to_extract_invoice_data = "unable_to_extract_invoice_data"
    extracted_invoice_data = "extracted_invoice_data"