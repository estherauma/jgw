def export_buttons_config_list(request):
    inline_questions_export_buttons_config = [
        {'key':'inlineQNs_participation', 'title': 'Participation', 'id': 'exportParticipation'},
        {'key':'inlineQNs_responses', 'title': 'Answers Break-down', 'id': 'exportAnswersBreakdown'}
    ]
    
    preferences_export_buttons_config = [
        {'key':'preferences', 'title': 'Preferences', 'id': 'exportFileBtn'}
    ]
        
    return {
        "inline_questions_export_buttons_config": inline_questions_export_buttons_config,
        "preferences_export_buttons_config": preferences_export_buttons_config
    }