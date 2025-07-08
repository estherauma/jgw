from rest_framework import serializers
from .models import AggregatedContent

class AggregatedContentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', 
        read_only=True
    )

    class Meta:
        model = AggregatedContent
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']