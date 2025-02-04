import requests
import re
from typing import List, Dict
from django.conf import settings
from django.db import transaction
from question.models import ActualMessageSent

def make_api_request(url: str, headers: Dict[str, str]) -> Dict:
    """Make API request and return JSON response"""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return {"data": []}

def clean_list_item(list_item: str) -> str:
    """Remove HTML tags and clean list item text"""
    return re.sub('<[^<]+?>', '', list_item).strip()

def process_description(description: List[Dict]) -> List[str]:
    """Process description items and return combined text list"""
    combined_text = []
    
    for desc in description:
        if 'paragraph' in desc:
            if desc['paragraph'].strip():
                combined_text.append(desc['paragraph'])
        elif 'unorderedList' in desc:
            for list_item in desc['unorderedList']:
                clean_text = clean_list_item(list_item)
                if clean_text:
                    combined_text.append(clean_text)
    
    return combined_text

def process_content(content: Dict, message_id: str) -> Dict[str, str]:
    """Process content item and return message dictionary"""
    description = content.get('description', [])
    combined_text = process_description(description)
    final_message = ' '.join(combined_text)
    
    if final_message:
        return {
            'id': message_id,
            'message': final_message
        }
    return {}

def get_message_content() -> List[Dict[str, str]]:
    """Get message content from API and return processed messages"""
    url = f"{settings.MESSAGING_API_BASE_URL}/v1/cms/v2/docs"
    headers = {
        "secret": settings.MESSAGING_API_SECRET
    }
    
    data = make_api_request(url, headers)
    messages = []
    
    for item in data.get('data', []):     
        message_id = item.get('id')
        for content in item.get('pageContent', []):
            if content.get('type') == 'text_area':
                message = process_content(content, message_id)
                if message:
                    messages.append(message)
    
    return messages

@transaction.atomic
def save_messages_to_db():
    """Save processed messages to database"""
    messages = get_message_content()
    
    for message_data in messages:
        ActualMessageSent.objects.update_or_create(
            message_id=message_data['id'],
            defaults={'message': message_data['message']}
        )
