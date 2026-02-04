"""
PostHog Analytics Helper Utility

This module provides a centralized way to track events with PostHog.
It handles user identification, event tracking, and error handling.
"""

import logging
import posthog
from typing import Dict, Optional, Any
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def track_event(
    event_name: str,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    request=None,
    distinct_id: Optional[str] = None,
    disable_person_profile: bool = False
) -> bool:
    """
    Track an event with PostHog.
    
    Args:
        event_name: Name of the event to track
        user_id: Optional user ID (will use request.user if available)
        user_email: Optional user email
        properties: Optional dictionary of event properties
        request: Optional Django request object (used to get user info)
        distinct_id: Optional distinct ID for the user
        disable_person_profile: If True, disable person profile processing for this event
        
    Returns:
        bool: True if event was tracked successfully, False otherwise
    """
    try:

        if not distinct_id:
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                distinct_id = str(request.user.id)
            elif user_id:
                distinct_id = str(user_id)
            elif user_email:
                distinct_id = user_email
            else:
                if request and hasattr(request, 'session'):
                    distinct_id = request.session.session_key
        
        if not distinct_id:
            logger.warning(f"PostHog: No distinct_id available for event '{event_name}'")
            return False

        event_properties = properties or {}

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            event_properties.update({
                'user_email': user.email,
                'user_role': getattr(user, 'role', None),
                'is_staff': user.is_staff,
            })
        elif user_email:
            event_properties['user_email'] = user_email

        if request:
            event_properties.update({
                'path': request.path,
                'method': request.method,
            })
            if hasattr(request, 'META'):
                event_properties['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
                event_properties['ip_address'] = request.META.get('REMOTE_ADDR', '')
        
        if disable_person_profile:
            event_properties['$process_person_profile'] = False
        
        posthog.capture(
            distinct_id=distinct_id,
            event=event_name,
            properties=event_properties
        )
        return True
        
    except ImportError:
        logger.warning("PostHog: posthog package not installed")
        return False
    except Exception as e:
        logger.error(f"PostHog: Error tracking event '{event_name}': {str(e)}")
        return False


def identify_user(
    user_id: str,
    user_email: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    request=None
) -> bool:
    """
    Identify a user with PostHog.
    
    Args:
        user_id: User ID
        user_email: Optional user email
        properties: Optional dictionary of user properties
        request: Optional Django request object
        
    Returns:
        bool: True if user was identified successfully, False otherwise
    """
    try:
        
        user_properties = properties or {}
        
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            user_properties.update({
                'email': user.email,
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'role': getattr(user, 'role', None),
                'is_staff': user.is_staff,
                'is_active': user.is_active,
            })
        elif user_email:
            user_properties['email'] = user_email
        
        posthog.identify(
            distinct_id=str(user_id),
            properties=user_properties
        )
        return True
        
    except ImportError:
        logger.warning("PostHog: posthog package not installed")
        return False
    except Exception as e:
        logger.error(f"PostHog: Error identifying user '{user_id}': {str(e)}")
        return False


def alias_user(previous_id: str, current_id: str) -> bool:
    """
    Alias a user (useful when anonymous user becomes identified).
    
    Args:
        previous_id: Previous distinct ID (e.g., session key)
        current_id: Current distinct ID (e.g., user ID)
        
    Returns:
        bool: True if alias was created successfully, False otherwise
    """
    try:        
        posthog.alias(
            previous_id=previous_id,
            distinct_id=current_id
        )
        return True
        
    except ImportError:
        logger.warning("PostHog: posthog package not installed")
        return False
    except Exception as e:
        logger.error(f"PostHog: Error aliasing user: {str(e)}")
        return False

