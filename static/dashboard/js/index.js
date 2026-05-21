const generalMultiSelectConfig = {
    maxHeight: 500,
    enableFiltering: true,
}

$('#destination').multiselect({ ... generalMultiSelectConfig, enableClickableOptGroups: true }); 
$('#origin').multiselect({ ... generalMultiSelectConfig, enableClickableOptGroups: true });
$('#organisation').multiselect({ ... generalMultiSelectConfig }); 
$('#factory_farm').multiselect({ ... generalMultiSelectConfig });
$('#inline-question-select-id').multiselect({ ... generalMultiSelectConfig });
$('#messaging-question-select-id').multiselect({ ... generalMultiSelectConfig });
$('#all-inline-question-select-id').multiselect({ ... generalMultiSelectConfig });
$('#immigration_status').multiselect({ ... generalMultiSelectConfig, enableClickableOptGroups: true });
$('#sectors_of_work').multiselect({ ... generalMultiSelectConfig });
// Create User
$('#create-new-user-destinations-id').multiselect({ ... generalMultiSelectConfig });
$('#create-new-user-factory-farms-id').multiselect({ ... generalMultiSelectConfig });
$('#create-new-user-organisations-id').multiselect({ ... generalMultiSelectConfig });
$('#create-new-user-organisation-data-id').multiselect({ ... generalMultiSelectConfig });
$('#excepted-languages-search-id').multiselect({ ... generalMultiSelectConfig });
$('#create-new-user-excluded-origin-countries-id').multiselect({ ... generalMultiSelectConfig });
$('#create-new-user-immigration-status-id').multiselect({ ... generalMultiSelectConfig });

// Edit User
$('#edit-user-destinations-id').multiselect({ ... generalMultiSelectConfig });
$('#edit-user-languages-id').multiselect({ ... generalMultiSelectConfig });
$('#edit-user-organisations-id').multiselect({ ... generalMultiSelectConfig });
$('#edit-user-organisation-data-id').multiselect({ ... generalMultiSelectConfig });
$('#edit-user-factories-id').multiselect({ ... generalMultiSelectConfig });
$('#edit-user-exluded-origin-countries-id').multiselect({ ... generalMultiSelectConfig });
$('#user-groups-id').multiselect({ ... generalMultiSelectConfig });
$('#edit-user-immigration-status-id').multiselect({ ... generalMultiSelectConfig });
