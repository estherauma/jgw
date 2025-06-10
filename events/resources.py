from import_export import resources
from events.models import BigqueryHomepageEventData, ChaptersFeedbackStandard

class BigqueryHomepageEventDataResource(resources.ModelResource):
    def dehydrate_language(self, obj):
        return obj.language.translated_name if obj.language else None

    def dehydrate_destination(self, obj):
        return obj.destination.name if obj.destination else None

    def dehydrate_preference(self, obj):
        if obj.preference:
            return f"{obj.preference.data_source_id} - {obj.preference.device_id}"
        return None

    def dehydrate_age(self, obj):
        return obj.age.translated_range if obj.age else None

    def dehydrate_gender(self, obj):
        return obj.gender.translated_name if obj.gender else None

    def dehydrate_immigration_status(self, obj):
        return obj.immigration_status.name if obj.immigration_status else None

    def dehydrate_organisation(self, obj):
        return obj.organisation.name if obj.organisation else None

    def dehydrate_org_info(self, obj):
        return obj.org_info.name if obj.org_info else None

    def dehydrate_geo_country(self, obj):
        return obj.geo_country.name if obj.geo_country else None

    class Meta:
        model = BigqueryHomepageEventData
        fields = (
            'event_date', 'device_id', 'app_id', 'language', 'locale', 
            'destination', 'preference', 'age', 'gender', 'immigration_status', 
            'organisation', 'org_info', 'organisation_code', 'geo_city', 'geo_country'
        )
        export_order = fields

class ChaptersFeedbackStandardResource(resources.ModelResource):
    def dehydrate_preference(self, obj):
        if obj.preference:
            return f"{obj.preference.data_source_id} - {obj.preference.device_id}"
        return None

    def dehydrate_gender(self, obj):
        return obj.gender.translated_name if obj.gender else None

    def dehydrate_age(self, obj):
        return obj.age.translated_range if obj.age else None

    def dehydrate_language(self, obj):
        return obj.language.translated_name if obj.language else None

    def dehydrate_origin(self, obj):
        return obj.origin.name if obj.origin else None

    def dehydrate_destination(self, obj):
        return obj.destination.name if obj.destination else None

    def dehydrate_destination_state(self, obj):
        return obj.destination_state.name if obj.destination_state else None

    def dehydrate_immigration_status(self, obj):
        return obj.immigration_status.name if obj.immigration_status else None

    def dehydrate_route(self, obj):
        return obj.route.name if obj.route else None

    def dehydrate_organisation_sector(self, obj):
        return obj.organisation_sector.name if obj.organisation_sector else None

    def dehydrate_factory_farm(self, obj):
        return obj.factory_farm.name if obj.factory_farm else None

    def dehydrate_organisation(self, obj):
        return obj.organisation.name if obj.organisation else None

    def dehydrate_org_info(self, obj):
        return obj.org_info.name if obj.org_info else None

    def dehydrate_sectors_of_work(self, obj):
        return ", ".join([sector.translated_name for sector in obj.sectors_of_work.all()]) if obj.sectors_of_work.exists() else None

    class Meta:
        model = ChaptersFeedbackStandard
        fields = (
            'created_at', 'updated_at', 'api_created_at', 'api_updated_at',
            'data_source_id', 'device_id', 'locale', 'preference', 'feedback_title',
            'documentId', 'gender', 'age', 'language', 'origin', 'destination',
            'destination_state', 'immigration_status', 'route', 'organisation_sector',
            'factory_farm', 'organisation', 'org_info', 'sectors_of_work'
        )
        export_order = fields
