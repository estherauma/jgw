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


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    phone_country_iso = serializers.CharField(required=False, allow_blank=True)


class PasswordResetRequestResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    email = serializers.EmailField(allow_null=True)
    phone_number = serializers.CharField(allow_null=True)
    phone_country_iso = serializers.CharField(allow_null=True)


class PasswordResetVerifyCodeRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    phone_country_iso = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField()


class PasswordResetVerifyCodeResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    user_id = serializers.IntegerField()


class PasswordResetResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    phone_country_iso = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField()
    password = serializers.CharField()


class PasswordResetResetResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    user_id = serializers.IntegerField()


class AccessCodeSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    requires_login = serializers.BooleanField()
    expiry_date = serializers.DateField(allow_null=True)


class WorkGroupSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class OrganizationSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    org_code = serializers.CharField()
    display_name = serializers.CharField(allow_null=True, allow_blank=True)
    user_groups = WorkGroupSummarySerializer(many=True)
    access_codes = AccessCodeSummarySerializer(many=True)


class CurrentUserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField(allow_null=True)
    phone_number = serializers.CharField(allow_null=True)
    phone_country_iso = serializers.CharField(allow_null=True)
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    role = serializers.CharField(allow_null=True, allow_blank=True)
    access_type = serializers.CharField()
    is_active = serializers.BooleanField()
    organisation = OrganizationSummarySerializer(allow_null=True)


class DeleteAccountResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
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
