from decouple import config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from content.models import AggregatedContent
from content.serializers import AggregatedContentSerializer
from drf_yasg.utils import swagger_auto_schema


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
    @swagger_auto_schema(
        operation_summary="Trigger content aggregation",
        tags=["Content"]
    )
    def get(self, request):
        api = ContentAPI()
        documents = api.fetch_content()
        return Response(documents, status.HTTP_200_OK)


class AggregatedContentView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve aggregated content",
        tags=["Content"]
    )
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
