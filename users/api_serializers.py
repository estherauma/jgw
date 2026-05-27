from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=False)
    error = serializers.CharField()


class FormErrorResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=False)
    errors = serializers.JSONField()


class RegisterUserRequestSerializer(serializers.Serializer):
    access_type = serializers.ChoiceField(
        choices=["app", "dashboard"],
        required=False,
        help_text="Defaults to `app` when omitted.",
    )
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    phone_country_iso = serializers.CharField(required=False, allow_blank=True)
    password1 = serializers.CharField()
    org_code = serializers.CharField(required=False, allow_blank=True)


class RegisterUserResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    user_id = serializers.IntegerField()
    email = serializers.EmailField(allow_null=True)
    phone_number = serializers.CharField(allow_null=True)
    phone_country_iso = serializers.CharField(allow_null=True)


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    phone_country_iso = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()


class RefreshTokenRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class RefreshTokenResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user_id = serializers.IntegerField()


class VerifyRegistrationCodeRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    phone_country_iso = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField()


class VerifyRegistrationCodeResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    user_id = serializers.IntegerField()


class ResendRegistrationCodeRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    phone_country_iso = serializers.CharField(required=False, allow_blank=True)


class ResendRegistrationCodeResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    user_id = serializers.IntegerField()
    email = serializers.EmailField(allow_null=True)
    phone_number = serializers.CharField(allow_null=True)
    phone_country_iso = serializers.CharField(allow_null=True)
