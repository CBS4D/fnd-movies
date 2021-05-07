from schemas import ma
from marshmallow import fields, validate, ValidationError
from marshmallow_sqlalchemy import field_for


def password_validation(password):
    if sum(map(str.islower, password)) < 1:
        raise ValidationError(
            "must contain upper case, lower case character and number")
    elif sum(map(str.isupper, password)) < 1:
        raise ValidationError(
            "must contain upper case, lower case character and number")
    elif sum(c.isdigit() for c in password) < 1:
        raise ValidationError(
            "must contain upper case, lower case character and number")


class UserSchema(ma.Schema):

    class Meta:
        fields = ("user_name", "email", "password", "user_type", "admin_key")

    user_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(
        validate=[validate.Length(min=6), password_validation], required=True)
    admin_key = fields.Str(required=True)


class LoginSchema(ma.Schema):

    class Meta:
        fields = ('user_name', 'password')
        load_only = ('password',)