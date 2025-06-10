from import_export import resources
from preference.models import Preference, PreferenceHistory

class PreferenceResource(resources.ModelResource):
    def dehydrate_gender__translated_name(self, obj):
        return obj.gender.translated_name if obj.gender else None

    def dehydrate_age__translated_range(self, obj):
        return obj.age.translated_range if obj.age else None

    def dehydrate_org_info(self, obj):
        return obj.org_info.name if obj.org_info else None

    def dehydrate_immigration_status(self, obj):
        return obj.immigration_status.name if obj.immigration_status else None

    class Meta:
        model = Preference
        fields = (
            'id', 'data_source_id', 'device_id', 'created_at', 'api_created_at',
            'gender__translated_name', 'origin__name', 'destination__name',
            'org_code', 'organisation__name', 'org_info',
            'age__translated_range','organisation_access_code__code', 'immigration_status'
        )
        export_order = fields 


class PreferenceHistoryResource(resources.ModelResource):
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

    def dehydrate_api_destination(self, obj):
        return obj.api_destination.name if obj.api_destination else None

    def dehydrate_destination_state(self, obj):
        return obj.destination_state.name if obj.destination_state else None

    def dehydrate_route(self, obj):
        return obj.route.name if obj.route else None

    def dehydrate_organisation_sector(self, obj):
        return obj.organisation_sector.name if obj.organisation_sector else None

    def dehydrate_immigration_status(self, obj):
        return obj.immigration_status.name if obj.immigration_status else None

    def dehydrate_org_info(self, obj):
        return obj.org_info.name if obj.org_info else None

    def dehydrate_organisation_access_code(self, obj):
        return obj.organisation_access_code.code if obj.organisation_access_code else None

    def dehydrate_factory_farm(self, obj):
        return obj.factory_farm.name if obj.factory_farm else None

    def dehydrate_organisation(self, obj):
        return obj.organisation.name if obj.organisation else None

    def dehydrate_sectors_of_work(self, obj):
        return ", ".join([sector.translated_name for sector in obj.sectors_of_work.all()]) if obj.sectors_of_work.exists() else None

    class Meta:
        model = PreferenceHistory
        fields = (
            'id', 'data_source_id', 'device_id', 'locale', 'app_id',
            'api_created_at', 'api_updated_at',
            'location_of_potential_work', 'gender', 'age', 'language', 'origin',
            'destination', 'api_destination', 'destination_state', 'route',
            'sectors_of_work', 'organisation_sector', 'immigration_status',
            'org_code', 'org_info', 'organisation_access_code'
        )
        export_order = fields
        
        