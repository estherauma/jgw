def export_buttons_config_list(request):
    inline_questions_export_buttons_config = [
        {'key':'inlineQNs_participation', 'title': 'Participation', 'id': 'exportParticipation'},
        {'key':'inlineQNs_responses', 'title': 'Answers Break-down', 'id': 'exportAnswersBreakdown'}
    ]
    
    preferences_export_buttons_config = [
        {'key':'preferences', 'title': 'Preferences', 'id': 'exportFileBtn'}
    ]
    
    messaging_export_buttons_config = [
        {'key':'messaging', 'title': 'Messaging', 'id': 'exportInline'}
    ]
    
    help_contacts_export_buttons_config = [
        {'key':'help_contacts', 'title': 'Contacts', 'id': 'export-help-contacts-btn'}
    ]
    
    before_you_go_export_buttons_config = [
        {'key':'beforeyougo', 'title': 'Beforeyougo', 'id': 'exportInline'}
    ]
    
    contract_export_buttons_config = [
        {'key':'contract', 'title': 'Contract', 'id': 'exportInline'}
    ]
    
    jobffer_export_buttons_config = [
        {'key':'joboffer', 'title': 'Job Offer', 'id': 'exportInline'}
    ]
    
    visa_checklist_export_buttons_config = [
        {'key':'visa', 'title': 'Visa', 'id': 'exportInline'}
    ]
        
    return {
        "inline_questions_export_buttons_config": inline_questions_export_buttons_config,
        "preferences_export_buttons_config": preferences_export_buttons_config,
        "messaging_export_buttons_config": messaging_export_buttons_config,
        "help_contacts_export_buttons_config": help_contacts_export_buttons_config,
        "before_you_go_export_buttons_config": before_you_go_export_buttons_config,
        "contract_export_buttons_config": contract_export_buttons_config,
        "jobffer_export_buttons_config": jobffer_export_buttons_config,
        "visa_checklist_export_buttons_config": visa_checklist_export_buttons_config
    }