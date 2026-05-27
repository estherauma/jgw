from rest_framework import serializers


class AccessCodeLookupResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    requires_login = serializers.BooleanField()
    expiry_date = serializers.DateField(allow_null=True)
    organization = serializers.SerializerMethodField()
    workgroups = serializers.SerializerMethodField()

    def get_organization(self, obj):
        return obj.get("organization")

    def get_workgroups(self, obj):
        return obj.get("workgroups")


class AccessCodeLookupErrorSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=False)
    error = serializers.CharField()
