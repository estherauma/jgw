from rest_framework import serializers


class AccessCodeStatusResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    requires_login = serializers.BooleanField()


class AccessCodeLookupCollectionLanguageSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField(allow_null=True, allow_blank=True)


class AccessCodeLookupOrganizationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    org_code = serializers.CharField()
    display_name = serializers.CharField(allow_null=True, allow_blank=True)
    has_custom_content = serializers.BooleanField()
    theme = serializers.CharField(allow_null=True, allow_blank=True)
    custom_type = serializers.CharField(allow_null=True, allow_blank=True)
    work_sector = serializers.CharField(allow_null=True, allow_blank=True)
    content_collection = serializers.CharField(allow_null=True, allow_blank=True)
    default_collection_language = serializers.CharField(allow_null=True, allow_blank=True)
    default_feedback_emails = serializers.CharField(allow_null=True, allow_blank=True)
    default_report_issue_emails = serializers.CharField(allow_null=True, allow_blank=True)
    collection_languages = AccessCodeLookupCollectionLanguageSerializer(many=True)
    big_icon_url = serializers.CharField(allow_blank=True)
    small_icon_url = serializers.CharField(allow_blank=True)


class AccessCodeLookupWorkGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class AccessCodeLookupResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    requires_login = serializers.BooleanField()
    expiry_date = serializers.DateField(allow_null=True)
    organization = AccessCodeLookupOrganizationSerializer()
    access_code_user_groups = AccessCodeLookupWorkGroupSerializer(many=True)


class AccessCodeLookupErrorSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=False)
    error = serializers.CharField()
