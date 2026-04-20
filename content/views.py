import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from content.models import AggregatedContent
from content.serializers import AggregatedContentSerializer
from content.services.partner_configurations import sync_partner_configuration_item
# from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger(__name__)


class ContentAPI:
    def __init__(self):
        self.api_url = config('JGW_CMS_API_URL')
        self.access_token = config('JGW_CMS_API_TOKEN')
        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        self.languages = []
        self.fetch_content()
        self.documents = {}
    
    def fetch_content(self):
        try:
            response = requests.get(self.api_url, headers=self.headers)
            self.content = response.json()
            self.languages = self.content['locales']
            self.documents = self.start_document_fetch()
        except requests.RequestException as e:
            return {
                "error": str(e)
            }
        except ValueError as e:
            print("Error: ", e)

    def start_document_fetch(self):
        documents = {}
        for language in self.languages:
            url = f"{self.api_url}?locale={language['code']}"
            language_docs = requests.get(url, headers=self.headers).json()
            documents[language['code']] = self.aggregate_content(language_docs)
        aggregated_content = AggregatedContent()
        aggregated_content.content = documents
        aggregated_content.save()
        return documents

    def aggregate_content(self, lang_content):
        aggregated_content = {}
        aggregated_content['languages'] = self.languages

        def aggregate_form_questions(form_qn_data):
            additional_text = []

            aggregated_components = aggregate_components(form_qn_data['dynamic_zone'])
            for comp in aggregated_components:
                if comp['type'] == 'additional_text':
                    additional_text.extend(comp['additional_text'])

            return additional_text

        
        def aggregate_key_value_text(common_text_data):
            common_texts = []
            for item in common_text_data:
                common_texts.append({
                    'key': item['key'],
                    'value': item['value']
                })
            return common_texts
        
        
        def aggregate_components(data, raw_page_data=None):
            agg_result = []
            for item in data:
                component_type = item['__component']
                try:
                    if component_type == 'okolabor.additional-text':
                        result = aggregate_key_value_text(item['repeatable_zone'])
                        additional_text = {
                            'type': 'additional_text',
                            'additional_text': result
                        }
                        agg_result.append(additional_text)
                except Exception as e:
                    print(f'Could not aggregate {component_type} component.', e)
                    return None
            return agg_result
        
        for item in lang_content['data']:
            if item['custom_type'] == 'form_questions':
                additional_text = aggregate_form_questions(item)
                page_data = {
                    'page_id': item['id'],
                    'page_title': item.get('page_title', None),
                    'additional_text': additional_text
                }
                aggregated_content[item['page_id']] = page_data

        return aggregated_content


class StartContentAggregation(APIView):
    # @swagger_auto_schema(
    #     operation_summary="Trigger content aggregation",
    #     tags=["Content"]
    # )
    def get(self, request):
        api = ContentAPI()
        documents = api.fetch_content()
        return Response(documents, status.HTTP_200_OK)


class AggregatedContentView(APIView):
    # @swagger_auto_schema(
    #     operation_summary="Retrieve aggregated content",
    #     tags=["Content"]
    # )
    def get(self, request):
        try:
            latest = AggregatedContent.objects.latest('created_at')
            serializer = AggregatedContentSerializer(latest, many=False)
            return Response({
                'data': [serializer.data],
                'error_messages': []
            }, status.HTTP_200_OK)
        except AggregatedContent.DoesNotExist:
            return Response({}, status.HTTP_200_OK)


class ContentWebhookView(APIView):
    webhook_handlers = {
        "partner-configuration": {
            "handler": sync_partner_configuration_item,
            "events": ["entry.publish"],
        },
    }

    def post(self, request):
        try:
            expected_secret = getattr(settings, "STRAPI_WEBHOOK_SECRET", None)
            received_secret = request.headers.get("X-Secret")

            if not expected_secret or received_secret != expected_secret:
                logger.warning("Unauthorized webhook attempt", extra={"received_secret": received_secret})
                return JsonResponse({"ok": False, "error": "Unauthorized"}, status=403)

            try:
                payload = json.loads(request.body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                logger.warning("Invalid JSON payload received in webhook")
                return JsonResponse({"ok": False, "error": "Invalid JSON payload"}, status=400)

            content_type = payload.get("model")
            data = payload.get("entry")
            event = payload.get("event")

            if not isinstance(data, dict):
                logger.warning("Invalid webhook item payload")
                return JsonResponse({"ok": False, "error": "Invalid webhook item payload"}, status=400)

            handler_config = self.webhook_handlers.get(content_type)
            if not handler_config:
                return JsonResponse(
                    {"ok": False, "error": f"No webhook handler for content type: {content_type}"},
                    status=400,
                )

            allowed_events = handler_config.get("events", [])
            if event not in allowed_events:
                logger.info(f"Ignored event '{event}' for content type: {content_type}")
                return JsonResponse({"ok": True, "message": f"Event '{event}' ignored for '{content_type}'"})

            handler = handler_config.get("handler")
            logger.info(f"Received {event} event for content type: {content_type}, data: {data}")

            result = handler(data)
            return JsonResponse({"ok": True, "data": result})
        except Exception:
            logger.exception("Unexpected error while handling content webhook")
            return JsonResponse({"ok": False, "error": "Failed to process webhook"}, status=500)
