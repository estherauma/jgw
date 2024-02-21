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

$('#create-new-user-destinations-id').multiselect({ ... generalMultiSelectConfig });
$('#create-new-user-factory-farms-id').multiselect({ ... generalMultiSelectConfig });
$('#create-new-user-organisations-id').multiselect({ ... generalMultiSelectConfig });
$('#excepted-languages-search-id').multiselect({ ... generalMultiSelectConfig });
$('#create-new-user-excluded-origin-countries-id').multiselect({ ... generalMultiSelectConfig });