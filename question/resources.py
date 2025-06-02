from import_export import resources
from question.models import InlineQuestionStandard, MessagingQuestionStandard

class InlineQuestionResource(resources.ModelResource):
    def dehydrate_route(self, obj):
        return obj.route.name if obj.route else None

    def dehydrate_language(self, obj):
        return obj.language.name if obj.language else None

    def dehydrate_origin(self, obj):
        return obj.origin.name if obj.origin else None

    def dehydrate_destination(self, obj):
        return obj.destination.name if obj.destination else None

    def dehydrate_organisation_sector(self, obj):
        return obj.organisation_sector.name if obj.organisation_sector else None

    def dehydrate_organisation(self, obj):
        return obj.organisation.name if obj.organisation else None

    def dehydrate_question_key(self, obj):
        inline_question = obj.question_standard.first()
        if inline_question:
            return inline_question.question.text if inline_question.question else None
        return None

    def dehydrate_title_text(self, obj):
        inline_question = obj.question_standard.first()
        if inline_question:
            return inline_question.question.title_text if inline_question.question else None
        return None

    def dehydrate_response(self, obj):
        inline_question = obj.question_standard.first()
        if inline_question:
            response = inline_question.inline_question_response.first()
            if response and response.response:
                return response.response.translated_text
        return None

    class Meta:
        model = InlineQuestionStandard
        fields = (
            'api_created_at', 'api_updated_at', 'data_source_id', 'device_id',
            'language', 'origin', 'destination', 'organisation_sector',
            'organisation', 'route'
        )
        export_order = fields


class MessagingQuestionResource(resources.ModelResource):
    def dehydrate_route(self, obj):
        return obj.route.name if obj.route else None

    def dehydrate_language(self, obj):
        return obj.language.name if obj.language else None

    def dehydrate_origin(self, obj):
        return obj.origin.name if obj.origin else None

    def dehydrate_destination(self, obj):
        return obj.destination.name if obj.destination else None

    def dehydrate_organisation_sector(self, obj):
        return obj.organisation_sector.name if obj.organisation_sector else None

    def dehydrate_organisation(self, obj):
        return obj.organisation.name if obj.organisation else None

    def dehydrate_question_key(self, obj):
        messaging_question = obj.question_standard.first()
        if messaging_question:
            return messaging_question.question.text if messaging_question.question else None
        return None

    class Meta:
        model = MessagingQuestionStandard
        fields = (
            'api_created_at', 'api_updated_at', 'data_source_id', 'device_id',
            'language', 'origin', 'destination', 'organisation_sector',
            'organisation', 'route'
        )
        export_order = fields
    