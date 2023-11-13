from django.core.exceptions import ValidationError


def validate_password_symbol(value, symbols='!@#$%^&*'):
    if not any(char in symbols for char in value):
        raise ValidationError(
            f"Password must contain at least one of the specified symbols: {', '.join(symbols)}",
            code="password_no_symbol",
        )


def validate_password_number(value):
    if not any(char.isdigit() for char in value):
        raise ValidationError(
            "Password must contain at least one number",
            code="password_no_number",
        )


def validate_password_uppercase(value):
    if not any(char.isupper() for char in value):
        raise ValidationError(
            "Password must contain at least one uppercase letter",
            code="password_no_uppercase",
        )


def validate_password_lowercase(value):
    if not any(char.islower() for char in value):
        raise ValidationError(
            "Password must contain at least one lowercase letter",
            code="password_no_lowercase",
        )

