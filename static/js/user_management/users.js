(function () {
  function initCustomFormSelects(form) {
    if (form && window.initUmSelects) {
      window.initUmSelects(form);
    }
  }

  function refreshCustomFormSelects(form) {
    if (!form || !window.refreshUmSelect) {
      return;
    }
    form.querySelectorAll('[data-um-select]').forEach(function (root) {
      window.refreshUmSelect(root);
    });
  }

  function rebuildCustomFormSelects(form) {
    if (!form) {
      return;
    }
    form.querySelectorAll('[data-um-select]').forEach(function (root) {
      if (window.rebuildUmSelect) {
        window.rebuildUmSelect(root);
      } else if (window.refreshUmSelect) {
        window.refreshUmSelect(root);
      }
    });
  }

  function rebuildCustomSelectForField(field) {
    if (!field) {
      return;
    }
    var root = field.closest('[data-um-select]');
    if (!root) {
      return;
    }
    if (window.rebuildUmSelect) {
      window.rebuildUmSelect(root);
      return;
    }
    if (window.refreshUmSelect) {
      window.refreshUmSelect(root);
    }
  }

  function clearFieldValue(field) {
    if (!field) {
      return;
    }
    if (field.tagName === 'SELECT') {
      if (field.multiple) {
        Array.from(field.options).forEach(function (option) {
          option.selected = false;
        });
      } else {
        field.value = '';
      }
      rebuildCustomSelectForField(field);
      return;
    }
    if (field.type === 'checkbox' || field.type === 'radio') {
      field.checked = false;
      return;
    }
    field.value = '';
  }

  function getSelectedGroupNames(form) {
    var groupsField = form.querySelector('select[name="groups"]');
    if (groupsField) {
      return Array.from(groupsField.selectedOptions).map(function (option) {
        return (option.text || '').trim();
      });
    }
    return Array.from(form.querySelectorAll('input[name="groups"]:checked')).map(
      function (input) {
        return input.value;
      },
    );
  }

  function initDashboardRoleBehavior(form) {
    if (!form) {
      return null;
    }

    var organisationGroupWrapper = form.querySelector(
      '[data-dashboard-org-group-field]',
    );
    var organisationGroupField = form.querySelector('[name="organisation_group"]');
    var hiddenWrappers = Array.from(
      form.querySelectorAll('[data-dashboard-hide-for-org-group-admin]'),
    );
    var fieldsToClear = [
      'organisation_data',
      'scheme',
      'destinations',
      'excluded_origin_countries',
      'user_languages',
      'factories',
      'immigration_status',
      'start_date',
      'end_date',
    ];

    function refresh() {
      var selectedGroupNames = getSelectedGroupNames(form);
      var isOrgGroupAdminSelected =
        selectedGroupNames.indexOf('org_group_admin') !== -1;
      var is58AdminSelected = selectedGroupNames.indexOf('58_admin') !== -1;
      var hideOrgScopedFields = isOrgGroupAdminSelected || is58AdminSelected;

      if (organisationGroupWrapper) {
        organisationGroupWrapper.classList.toggle(
          'd-none',
          !isOrgGroupAdminSelected || is58AdminSelected,
        );
      }
      if (organisationGroupField) {
        organisationGroupField.required = isOrgGroupAdminSelected;
      }
      hiddenWrappers.forEach(function (wrapper) {
        wrapper.classList.toggle('d-none', hideOrgScopedFields);
      });

      if (hideOrgScopedFields) {
        fieldsToClear.forEach(function (fieldName) {
          clearFieldValue(form.querySelector('[name="' + fieldName + '"]'));
        });
        if (is58AdminSelected) {
          clearFieldValue(organisationGroupField);
        }
      }

      refreshCustomFormSelects(form);
    }

    form.addEventListener('change', function (event) {
      if (event.target && event.target.name === 'groups') {
        refresh();
      }
    });

    refresh();
    return { refresh: refresh };
  }

  function getSelectedUserIds() {
    return Array.from(
      document.querySelectorAll('[data-user-select]:checked'),
    ).map(function (input) {
      return input.value;
    });
  }


  function updateAssignButtonState() {
      const assignWorkGroupButton = document.querySelector('[data-users-workgroup-action]');
      const selectedIds = getSelectedUserIds();
      if (assignWorkGroupButton) {
        assignWorkGroupButton.disabled = selectedIds.length === 0;
      }
      const modal = document.getElementById('assign-users-workgroup-modal');
      if (modal) {
        const countLabel = modal.querySelector('[data-selected-users-count]');
        if (countLabel) {
            countLabel.textContent = String(selectedIds.length);
        }
    }
  }

  function initAppUserForm() {
    var form = document.getElementById('add-appuser-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('add-appuser-form-error');
    var phoneInput = form.querySelector('[name="phone_number"]');
    var smsConsentWrapper = form.querySelector('[data-phone-sms-consent-wrapper]');
    var smsConsentInput = form.querySelector('[name="sms_consent_confirmation"]');
    initCustomFormSelects(form);

    function syncSmsConsentVisibility() {
      if (!smsConsentWrapper || !phoneInput) {
        return;
      }
      var hasPhoneNumber = Boolean((phoneInput.value || '').trim());
      smsConsentWrapper.classList.toggle('d-none', !hasPhoneNumber);
      if (!hasPhoneNumber && smsConsentInput) {
        smsConsentInput.checked = false;
      }
    }

    function clearErrors() {
      if (window.clearFormErrors) {
        window.clearFormErrors(form, errorBox);
      }
    }

    function resetAppUserForm() {
      clearErrors();
      form.reset();
      syncSmsConsentVisibility();
      refreshCustomFormSelects(form);
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization('add-appuser-form', '[data-appuser-org-label]');
      }
    }

    if (phoneInput) {
      phoneInput.addEventListener('input', syncSmsConsentVisibility);
      phoneInput.addEventListener('change', syncSmsConsentVisibility);
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      clearErrors();
      syncSmsConsentVisibility();
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization('add-appuser-form', '[data-appuser-org-label]');
      }
      var selectedInput = form.querySelector('[data-selected-org-id]');
      var selectedId =  selectedInput?.value || '';
      if (!selectedId) {
        if (errorBox) {
          errorBox.textContent = 'Select an organisation first.';
          errorBox.classList.remove('d-none');
        }
        return;
      }
      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) {
        submitButton.disabled = true;
      }
      if (window.toggleFullScreenLoader) {
        window.toggleFullScreenLoader(true);
      }
      try {
        var data = null;
        if (window.postFormJson) {
          data = await window.postFormJson(form);
        }
        if (data && data.org_id && !window.isOrgOrGroupAdmin) {
          var homeUrl = window.location.pathname;
          var target =
            homeUrl + '?selected_org_id=' + encodeURIComponent(data.org_id);
          window.location.href = target;
        } else {
          window.location.reload();
        }
      } catch (data) {
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });


    $('[data-target="#add-appuser-modal"]').on('click', function () {
      resetAppUserForm();
    });
    syncSmsConsentVisibility();
  }

  function initDashboardUserForm() {
    var form = document.getElementById('add-dashboard-user-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('add-dashboard-user-form-error');
    initCustomFormSelects(form);
    var roleSelector =
      window.initPrimaryRoleGroupSelector &&
      window.initPrimaryRoleGroupSelector(form);
    var dashboardRoleBehavior = initDashboardRoleBehavior(form);

    function clearErrors() {
      if (window.clearFormErrors) {
        window.clearFormErrors(form, errorBox);
      }
    }

    function resetDashboardForm() {
      clearErrors();
      form.reset();
      refreshCustomFormSelects(form);
      if (roleSelector) {
        roleSelector.refresh();
      }
      if (dashboardRoleBehavior) {
        dashboardRoleBehavior.refresh();
      }
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      clearErrors();
      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) {
        submitButton.disabled = true;
      }
      if (window.toggleFullScreenLoader) {
        window.toggleFullScreenLoader(true);
      }
      try {
        if (window.postFormJson) {
          await window.postFormJson(form);
        }
        $('#add-dashboard-user-modal').modal('hide');
        window.location.reload();
      } catch (data) {
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });

    $('[data-target="#add-dashboard-user-modal"]').on('click', function () {
      resetDashboardForm();
    });
    $(form.closest('.modal')).on('shown.bs.modal', function () {
      rebuildCustomFormSelects(form);
      refreshCustomFormSelects(form);
    });
  }

  function initEditDashboardUserForm() {
    var modal = document.getElementById('edit-dashboard-user-modal');
    if (!modal) {
      return;
    }
    var form = modal.querySelector('form');
    var errorBox = document.getElementById('edit-dashboard-user-form-error');
    initCustomFormSelects(form);
    var roleSelector =
      window.initPrimaryRoleGroupSelector &&
      window.initPrimaryRoleGroupSelector(form);
    var dashboardRoleBehavior = initDashboardRoleBehavior(form);

    function clearErrors() {
      if (window.clearFormErrors) {
        window.clearFormErrors(form, errorBox);
      }
    }

    function renderUserLanguages(selectedIds) {
      var languagesField = form.querySelector('[name="user_languages"]');
      if (!languagesField) {
        return;
      }
      var valueSet = new Set((selectedIds || []).map(String));
      Array.from(languagesField.options).forEach(function (option) {
        option.selected = valueSet.has(String(option.value));
      });
      rebuildCustomSelectForField(languagesField);
    }

    function setSingleValue(name, value) {
      var input = form.querySelector('[name="' + name + '"]');
      if (input) {
        input.value = value || '';
        rebuildCustomSelectForField(input);
      }
    }

    function setCheckboxValue(name, checked) {
      var input = form.querySelector('[name="' + name + '"]');
      if (input) {
        input.checked = Boolean(checked);
      }
    }

    function setMultiValues(name, values) {
      var valueSet = new Set((values || []).map(String));
      var field = form.querySelector('select[name="' + name + '"]');
      if (field) {
        Array.from(field.options).forEach(function (option) {
          option.selected = valueSet.has(String(option.value));
        });
        rebuildCustomSelectForField(field);
        return;
      }
      var inputs = form.querySelectorAll('input[name="' + name + '"]');
      inputs.forEach(function (input) {
        input.checked = valueSet.has(String(input.value));
      });
    }

    function resetForm() {
      clearErrors();
      form.reset();
      refreshCustomFormSelects(form);
      if (roleSelector) {
        roleSelector.refresh();
      }
      if (dashboardRoleBehavior) {
        dashboardRoleBehavior.refresh();
      }
    }

    $('[data-target="#edit-dashboard-user-modal"]').on('click', async function () {
      var $btn = $(this);
      var userId = $btn.data('user-id');
      var editUrl = '/user-management/dashboard-users/' + userId + '/edit/';
      form.action = editUrl;
      resetForm();
      try {
        var response = await fetch(editUrl);
        var data = await response.json();
        if (!data.ok) {
          throw new Error(data.error || 'Failed to fetch user data.');
        }
        var user = data.user || {};
        setSingleValue('email', user.email);
        setSingleValue('first_name', user.first_name);
        setSingleValue('last_name', user.last_name);
        setSingleValue('scheme', user.scheme_id ? String(user.scheme_id) : '');
        setSingleValue('start_date', user.start_date);
        setSingleValue('end_date', user.end_date);
        setSingleValue('password', '');
        setSingleValue('password_confirm', '');
        setCheckboxValue('is_active', user.is_active);
        setMultiValues('groups', user.groups);
        setSingleValue(
          'organisation_group',
          user.organisation_group_id ? String(user.organisation_group_id) : '',
        );
        setMultiValues('organisation_data', user.organisation_data);
        setMultiValues('factories', user.factories);
        setMultiValues('destinations', user.destinations);
        setMultiValues('user_languages', user.user_languages);
        setMultiValues('excluded_origin_countries', user.excluded_origin_countries);
        setMultiValues('immigration_status', user.immigration_status);
        if (roleSelector) {
          roleSelector.refresh();
        }
        if (dashboardRoleBehavior) {
          dashboardRoleBehavior.refresh();
        }
        renderUserLanguages(user.user_languages);
        rebuildCustomFormSelects(form);
        refreshCustomFormSelects(form);
      } catch (err) {
        console.error('Failed to fetch dashboard user data:', err);
      }
    });
    $(modal).on('shown.bs.modal', function () {
      rebuildCustomFormSelects(form);
      refreshCustomFormSelects(form);
    });

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      clearErrors();
      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) {
        submitButton.disabled = true;
      }
      try {
        if (window.postFormJson) {
          await window.postFormJson(form);
        }
        window.location.reload();
      } catch (data) {
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });
  }

  function initEditUserForm() {
    var modal = document.getElementById('edit-appuser-modal');
    if (!modal) return;

    var form = modal.querySelector('form');
    var errorBox = document.getElementById('edit-appuser-form-error');
    initCustomFormSelects(form);

    function clearErrors() {
      if (window.clearFormErrors) {
        window.clearFormErrors(form, errorBox);
      }
    }

    function renderLanguageOptions(languageOptions, selectedIds) {
      var languagesField = form.querySelector('[name="user_languages"]');
      if (!languagesField) {
        return;
      }

      var valueSet = new Set((selectedIds || []).map(String));
      languagesField.innerHTML = '';

      (languageOptions || []).forEach(function (language) {
        var option = document.createElement('option');
        option.value = language.id;
        option.text = language.name;
        option.selected = valueSet.has(String(language.id));
        languagesField.appendChild(option);
      });

      rebuildCustomSelectForField(languagesField);
    }

    function renderWorkGroups(workGroups, selectedIds, workGroupsContainer) {
      var workGroupsField = form.querySelector('[name="work_groups"]');
      if (!workGroupsField) {
        return;
      }
      var valueSet = new Set((selectedIds || []).map(String));
      workGroupsField.innerHTML = '';
      (workGroups || []).forEach(function (group) {
        var option = document.createElement('option');
        option.value = group.id;
        option.text = group.name;
        option.selected = valueSet.has(String(group.id));
        workGroupsField.appendChild(option);
      });
      rebuildCustomSelectForField(workGroupsField);
    }

    function renderRoles(roles, selectedRoleId) {
      var roleSelect = form.querySelector('[name="role"]');

      if (!roleSelect || !Array.isArray(roles)) {
        return;
      }
      var options = ['<option value=\"\">Select role</option>'];
      roles.forEach(function (role) {
        var selected =
          selectedRoleId && String(role.id) === String(selectedRoleId)
            ? ' selected'
            : '';
        options.push(
          '<option value=\"' + role.id + '\"' + selected + '>' + role.name + '</option>',
        );
      });
      roleSelect.innerHTML = options.join('');
      rebuildCustomSelectForField(roleSelect);
    }

    $('[data-target="#edit-appuser-modal"]').on('click', async function () {
      var $btn = $(this);
      var userId = $btn.data('user-id');
      var editUrl = '/user-management/app-users/' + userId + '/edit/';
      
      form.action = editUrl;
      form.reset();
      rebuildCustomFormSelects(form);
      refreshCustomFormSelects(form);
      clearErrors();
      var workGroupsContainer = form.querySelector('[data-work-groups-container]');

      try {
        var response = await fetch(editUrl);
        var data = await response.json();
        
        if (data.ok) {
          var user = data.user;
          form.querySelector('[name="first_name"]').value = user.first_name || '';
          form.querySelector('[name="last_name"]').value = user.last_name || '';
          form.querySelector('[name="email"]').value = user.email || '';
          renderRoles(data.roles, user.role_id);
          form.querySelector('[name="phone_number"]').value = user.phone_local || '';
          var countryField = form.querySelector('[name="phone_country_iso"]');
          if (countryField) {
            countryField.value =
              user.phone_country_iso || countryField.options?.[0]?.value || '';
            rebuildCustomSelectForField(countryField);
          }

          var orgLabel = modal.querySelector('[data-appuser-org-label]');
          if (orgLabel) {
            orgLabel.textContent = user.organisation_name || 'None';
          }

          renderWorkGroups(data.work_groups, user.work_group_ids,workGroupsContainer);
          renderLanguageOptions(data.language_options, user.user_language_ids);
          rebuildCustomFormSelects(form);
          refreshCustomFormSelects(form);
        }
      } catch (err) {
        console.error('Failed to fetch user data:', err);
      }
    });
    $(modal).on('shown.bs.modal', function () {
      rebuildCustomFormSelects(form);
      refreshCustomFormSelects(form);
    });

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      clearErrors(form, errorBox);

      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) submitButton.disabled = true;

      if (window.toggleFullScreenLoader){
        window.toggleFullScreenLoader(true)
      }

      try {
        if (window.postFormJson) {
          await window.postFormJson(form);
        }
        window.location.reload();
      } catch (data) {
        if (window.toggleFullScreenLoader){
          window.toggleFullScreenLoader(false)
        }
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });
  }

  function initUserSearch() {
    const input = document.querySelector('[data-user-search]');
    if (!input) {
      return;
    }
    const url = input.getAttribute('data-user-search-url');
    const tbody = document.querySelector('[data-users-table-body]');
    const paginationContainer = document.querySelector('[data-users-pagination]');
    const filtersContainer = document.querySelector('[data-users-filters]');
    const filtersPanel = document.querySelector('[data-users-filters-panel]');
    const filtersToggle = document.querySelector('[data-users-filters-toggle]');
    const filtersClearButton = document.querySelector('[data-users-filters-clear]');
    const filtersCloseButton = document.querySelector('[data-users-filters-close]');
    const filtersCount = document.querySelector('[data-users-filters-count]');
    if (!url || !tbody || !paginationContainer) {
      return;
    }
    if (filtersContainer && window.initUmSelects) {
      window.initUmSelects(filtersContainer);
    }
    const organisationFilterController =
      window.createAsyncOrganisationPicker &&
      window.createAsyncOrganisationPicker(
        document.querySelector('[data-user-filter-organisation-select]'),
        {
          toggleSelector: '[data-user-filter-organisation-toggle]',
          menuSelector: '[data-user-filter-organisation-menu]',
          searchInputSelector: '[data-user-filter-organisation-search]',
          optionsContainerSelector: '[data-user-filter-organisation-options]',
          hiddenInputSelector: '[data-user-filter-organisation]',
          labelSelector: '[data-user-filter-organisation-label]',
          placeholder: 'All organisations',
        },
      );
    const selectedOrgId =
      (filtersContainer?.getAttribute('data-selected-org-id') || '').trim();
    let debounceTimer = null;
    let controller = null;
    let currentPage = 1;

    function getFilterValues() {
      const statusFilter = document.querySelector('[data-user-filter-status]');
      const roleFilter = document.querySelector('[data-user-filter-role]');
      const workGroupFilter = document.querySelector(
        '[data-user-filter-workgroup]',
      );
      return {
        organisationId: organisationFilterController?.getValue() || '',
        status: (statusFilter?.value || '').trim(),
        role: (roleFilter?.value || '').trim(),
        workGroupId: (workGroupFilter?.value || '').trim(),
      };
    }

    function getAppliedFilterCount() {
      const filters = getFilterValues();
      return Object.values(filters).filter(Boolean).length;
    }

    function syncFilterUiState() {
      const appliedCount = getAppliedFilterCount();
      const panelIsOpen = !!filtersPanel && !filtersPanel.classList.contains('d-none');

      if (filtersToggle) {
        filtersToggle.setAttribute('aria-expanded', panelIsOpen ? 'true' : 'false');
        filtersToggle.classList.toggle('is-open', panelIsOpen);
        filtersToggle.classList.toggle('is-applied', appliedCount > 0);
      }
      if (filtersCount) {
        filtersCount.textContent = String(appliedCount);
        filtersCount.classList.toggle('d-none', appliedCount === 0);
      }
      if (filtersClearButton) {
        filtersClearButton.disabled = appliedCount === 0;
      }
    }

    function setFiltersPanelOpen(open) {
      if (!filtersPanel) {
        return;
      }
      filtersPanel.classList.toggle('d-none', !open);
      syncFilterUiState();
    }

    function clearFilters() {
      if (!filtersContainer) {
        return;
      }
      organisationFilterController?.clear();
      filtersContainer.querySelectorAll('select').forEach(function (select) {
        select.value = '';
        rebuildCustomSelectForField(select);
      });
      syncFilterUiState();
      const value = (input.value || '').trim();
      runSearch(value, 1);
    }

    async function runSearch(value, page) {
      if (controller) {
        controller.abort();
      }
      controller = new AbortController();
      const params = new URLSearchParams();
      if (value) {
        params.set('q', value);
      }
      const filters = getFilterValues();

      if (selectedOrgId) {
        params.set('selected_org_id', selectedOrgId);
      }
      if (!selectedOrgId && filters.organisationId) {
        params.set('organisation_id', filters.organisationId);
      }
      if (filters.status) {
        params.set('status', filters.status);
      }
      if (filters.role) {
        params.set('role', filters.role);
      }
      if (selectedOrgId && filters.workGroupId) {
        params.set('work_group_id', filters.workGroupId);
      }
      params.set('page', String(page || 1));
      try {
        const response = await fetch(
          url + (params.toString() ? '?' + params.toString() : ''),
          {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            signal: controller.signal,
          },
        );
        if (!response.ok) {
          throw new Error('Search failed');
        }
        const data = await response.json();
        if (data?.rows_html !== undefined) {
          tbody.innerHTML = data.rows_html;
          paginationContainer.innerHTML = data.pagination_html || '';
          currentPage = page || 1;
          updateAssignButtonState();
          updateDeleteButton();
          updateDeactivateButtonState();
          updateActivateButtonState();
          updateInviteButtonState();
          syncFilterUiState();
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          return;
        }
        console.error(error);
      }
    }

    input.addEventListener('input', function (event) {
      const value = (event.target.value || '').trim();
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        runSearch(value, 1);
      }, 250);
    });

    if (filtersContainer) {
      filtersContainer.addEventListener('change', function (event) {
        if (
          !event.target.closest('select') &&
          !event.target.matches('[data-user-filter-organisation]')
        ) {
          return;
        }
        const value = (input.value || '').trim();
        syncFilterUiState();
        runSearch(value, 1);
      });
    }

    if (filtersToggle) {
      filtersToggle.addEventListener('click', function () {
        const isOpen = !!filtersPanel && !filtersPanel.classList.contains('d-none');
        setFiltersPanelOpen(!isOpen);
      });
    }

    if (filtersCloseButton) {
      filtersCloseButton.addEventListener('click', function () {
        setFiltersPanelOpen(false);
      });
    }

    if (filtersClearButton) {
      filtersClearButton.addEventListener('click', function () {
        clearFilters();
      });
    }

    paginationContainer.addEventListener('click', function (event) {
      const trigger = event.target.closest('[data-users-page-link]');
      if (!trigger || trigger.disabled) {
        return;
      }
      event.preventDefault();
      const requestedPage = Number(trigger.getAttribute('data-page') || currentPage || 1);
      const value = (input.value || '').trim();
      runSearch(value, requestedPage);
    });

    syncFilterUiState();
  }

  function updateDeleteButton() {
    const deleteButton = document.querySelector('[data-users-delete]');
    if (!deleteButton) {
      return;
    }
    const selectedIds = getSelectedUserIds();
    deleteButton.disabled = selectedIds.length === 0;
  }

  function updateInviteButtonState() {
    const inviteButton = document.querySelector('[data-invite-users]');
    if (!inviteButton) {
      return;
    }
    const selectedIds = getSelectedUserIds();
    inviteButton.disabled = selectedIds.length === 0;
  }

  function updateDeactivateButtonState(){
    const deactivateButton = document.querySelector('[data-deactivate-users]')
    if (!deactivateButton) {
      return;
    }
    const selectedIds = getSelectedUserIds();
    deactivateButton.disabled = selectedIds.length === 0;
  }

  function updateActivateButtonState() {
    const activateButton = document.querySelector('[data-activate-users]');
    if (!activateButton) {
      return;
    }
    const selectedIds = getSelectedUserIds();
    activateButton.disabled = selectedIds.length === 0;
  }

  function initUserSelection() {
    const selectAll = document.querySelector('[data-users-select-all]');
    if (!selectAll) {
      return;
    }

    function updateSelectionState() {
      const selectedIds = getSelectedUserIds();
      const checkboxes = document.querySelectorAll('[data-user-select]');
      if (!checkboxes.length) {
        selectAll.checked = false;
        selectAll.indeterminate = false;
      } else {
        selectAll.checked = selectedIds.length === checkboxes.length;
        selectAll.indeterminate = selectedIds.length > 0 && selectedIds.length < checkboxes.length;
      }
      updateAssignButtonState();
      updateDeactivateButtonState();
      updateActivateButtonState();
      updateInviteButtonState();
    }

    selectAll.addEventListener('change', function (event) {
      const checked = event.target.checked;
      const checkboxes = document.querySelectorAll('[data-user-select]');
      checkboxes.forEach(function (input) {
        input.checked = checked;
      });
      updateSelectionState();
      updateDeleteButton();
      updateDeactivateButtonState();
      updateActivateButtonState();
      updateInviteButtonState();
      
    });

    document.addEventListener('change', function (event) {
      if (event.target && event.target.matches('[data-user-select]')) {
        updateSelectionState();
        updateDeleteButton();
        updateDeactivateButtonState();
        updateActivateButtonState();
        updateInviteButtonState();
      }
    });
  }

  function initDeleteUsers() {
    const deleteBtn = document.querySelector('[data-users-delete]');
    if (!deleteBtn) {
      return;
    }

    deleteBtn.addEventListener('click', function () {
      const checkedBoxes = document.querySelectorAll('[data-user-select]:checked');
      
      if (checkedBoxes.length === 0) {
        alert('Select at least one user to delete.');
        return;
      }

      const selectedUsers = Array.from(checkedBoxes).map(cb => {
        return {
          id: cb.value,
          first_name: cb.getAttribute('data-first-name') || '',
          last_name: cb.getAttribute('data-last-name') || '',
          email: cb.getAttribute('data-email') || ''
        };
      });

      const count = selectedUsers.length;
      let deleteMessage = '';
      let deleteTitle = '';

      if (count === 1) {
        const userDisplayName = getUserDisplayname(selectedUsers[0]);
        deleteTitle = `Delete User`;
        deleteMessage = `Are you sure you want to delete <strong>${userDisplayName}</strong>?`;
      } else {
        const displayNamesList = selectedUsers.map(user => getUserDisplayname(user)).join(", ");
        deleteTitle = `Delete Users`;
        deleteMessage = `Are you sure you want to delete the following users: <strong>${displayNamesList}</strong>?`;
      }

      window.showDeleteConfirm({
        title: deleteTitle,
        message: deleteMessage,
        url: '/user-management/users/delete/',
        method: 'POST',
        body: JSON.stringify({ ids: selectedUsers.map(u => u.id).join(',') }),
        headers: {
          'Content-Type': 'application/json',
          },
        showFullScreenLoader: true,
        onSuccess: function () {
          window.location.reload();
        },
      });
    });
  }

  function initActivateUsers() {
    const activateBtn = document.querySelector('[data-activate-users]');
    if (!activateBtn) return;

    activateBtn.addEventListener('click', function () {
      const checkedBoxes = document.querySelectorAll('[data-user-select]:checked');
      if (checkedBoxes.length === 0) {
        alert('Select at least one user to activate.');
        return;
      }

      const selectedUsers = Array.from(checkedBoxes).map(cb => {
        return {
          id: cb.value,
          first_name: cb.getAttribute('data-first-name') || '',
          last_name: cb.getAttribute('data-last-name') || '',
          email: cb.getAttribute('data-email') || ''
        };
      });

      const count = selectedUsers.length;
      let activateMessage = '';
      let activateTitle = '';

      if (count === 1) {
        const userDisplayName = getUserDisplayname(selectedUsers[0]);
        activateTitle = `Activate User`;
        activateMessage = `Are you sure you want to activate <strong>${userDisplayName}</strong>?`;
      } else {
        const displayNamesList = selectedUsers.map(user => getUserDisplayname(user)).join(", ");
        activateTitle = `Activate Users`;
        activateMessage = `Are you sure you want to activate the following users: <strong>${displayNamesList}</strong>?`;
      }

      window.showDeleteConfirm({
        title: activateTitle,
        message: activateMessage,
        warning: 'Activated users will be able to access the system immediately.',
        url: '/user-management/users/activate/',
        method: 'POST',
        body: JSON.stringify({ ids: selectedUsers.map(u => u.id).join(','), action: 'activate' }),
        headers: {
          'Content-Type': 'application/json',
        },
        confirmButtonText: 'Activate',
        confirmButtonClass: 'um-btn um-btn-lime',
        showFullScreenLoader: true,
        onSuccess: function () {
          window.location.reload();
        },
      });
    });
  }

  function initDeleteUser() {
    const deleteBtn = document.querySelector('[data-delete-user]');
    if (!deleteBtn) {
      return;
    }

    deleteBtn.addEventListener('click', function () {
      const userId = deleteBtn.getAttribute('data-user-id');

      window.showDeleteConfirm({
        title: 'Delete User',
        message: `Are you sure you want to delete this user?`,
        url: '/user-management/users/delete/',
        method: 'POST',
        body: JSON.stringify({ ids: String(userId) }),
        headers: {
          'Content-Type': 'application/json',
        },
        confirmButtonText: 'Delete',
        confirmButtonClass: 'um-btn um-btn-danger',
        showFullScreenLoader: true,
        onSuccess: function () {
          window.location.href = document.referrer || '/user-management/';
        },
      });
    });
  }
  function getUserDisplayname(user){
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim();
    if (fullName) {
      return fullName;
    }
    if (user.email) {
      return user.email;
    }
    if (user.phone_number) {
      return user.phone_number;
    }
    return `ID: ${user.id}`;
  }

  function initInviteUsers() {
    const inviteBtn = document.querySelector('[data-invite-users]');
    if (!inviteBtn) {
      return;
    }

    inviteBtn.addEventListener('click', function () {
      const checkedBoxes = document.querySelectorAll('[data-user-select]:checked');
      if (checkedBoxes.length === 0) {
        alert('Select at least one user to invite.');
        return;
      }

      const selectedUsers = Array.from(checkedBoxes).map(cb => {
        return {
          id: cb.value,
          first_name: cb.getAttribute('data-first-name') || '',
          last_name: cb.getAttribute('data-last-name') || '',
          email: cb.getAttribute('data-email') || '',
          phone_number: cb.getAttribute('data-phone-number') || '',
        };
      });

      const count = selectedUsers.length;
      const displayNamesList = selectedUsers
        .map(user => getUserDisplayname(user))
        .join(', ');

      const emailTargets = selectedUsers
        .filter(user => user.email)
        .map(user => user.email);
      const smsTargets = selectedUsers
        .filter(user => !user.email && user.phone_number)
        .map(user => user.phone_number);

      const emailList = emailTargets.length
        ? `<div><strong>Email invitations</strong>: ${emailTargets.join(', ')}</div>`
        : '<div><strong>Email invitations</strong>: None</div>';
      const smsList = smsTargets.length
        ? `<div><strong>SMS invitations</strong>: ${smsTargets.join(', ')}</div>`
        : '<div><strong>SMS invitations</strong>: None</div>';

      const title = count === 1 ? 'Invite User' : 'Invite Users';
      const message =
        count === 1
          ? `Send an invitation to <strong>${displayNamesList}</strong>?${emailList}${smsList}`
          : `The following invitations will be sent: <strong>${displayNamesList}</strong>?${emailList}${smsList}`;

      window.showDeleteConfirm({
        title: title,
        message: message,
        warning: 'SMS invitations will only be sent when no email is available.',
        url: '/user-management/users/invite/',
        method: 'POST',
        body: JSON.stringify({ ids: selectedUsers.map(u => u.id).join(',') }),
        headers: {
          'Content-Type': 'application/json',
        },
        confirmButtonText: 'Send invite',
        confirmButtonClass: 'um-btn um-btn-lime',
        showFullScreenLoader: true,
        onSuccess: function () {
          window.location.reload();
        },
      });
    });
  }

  function initDeactivateUsers() {
    const deactivateBtn = document.querySelector('[data-deactivate-users]');
    if (!deactivateBtn) return;
  
    deactivateBtn.addEventListener('click', function () {
      const checkedBoxes = document.querySelectorAll('[data-user-select]:checked');
      
      if (checkedBoxes.length === 0) {
        alert('Select at least one user to deactivate.');
        return;
      }
  
      const selectedUsers = Array.from(checkedBoxes).map(cb => {
        return {
          id: cb.value,
          first_name: cb.getAttribute('data-first-name') || '',
          last_name: cb.getAttribute('data-last-name') || '',
          email: cb.getAttribute('data-email') || ''
        };
      });
  
      const count = selectedUsers.length;
      let deactivateMessage = '';
      let deactivateTitle = '';
  
      if (count === 1) {
        const userDisplayName = getUserDisplayname(selectedUsers[0]);
        deactivateTitle = `Deactivate User`;
        deactivateMessage = `Are you sure you want to deactivate <strong>${userDisplayName}</strong>?`;
      } else {
        const displayNamesList = selectedUsers.map(user => getUserDisplayname(user)).join(", ");
        deactivateTitle = `Deactivate Users`;
        deactivateMessage = `Are you sure you want to deactivate the following users: <strong>${displayNamesList}</strong>?`;
      }

      window.showDeleteConfirm({
        title: deactivateTitle,
        message: deactivateMessage,
        warning: 'Deactivated users will lose access to the system. They can be reactivated later if needed.',
        url: '/user-management/users/activate/',
        method: 'POST',
        body: JSON.stringify({ ids: selectedUsers.map(u => u.id).join(','), action: 'deactivate' }),
        headers: {
          'Content-Type': 'application/json',
        },
        confirmButtonText: 'Deactivate',
        confirmButtonClass: 'um-btn um-btn-danger',
        showFullScreenLoader: true,
        onSuccess: function () {
          window.location.reload();
        },
      });
    });
  }

  function initAssignUsersToWorkGroups() {
    const modal = document.getElementById('assign-users-workgroup-modal');
    const form = document.getElementById('assign-users-workgroup-form');
    const errorBox = document.getElementById('assign-users-workgroup-form-error');
    if (!modal || !form) {
      return;
    }

    $('[data-target="#assign-users-workgroup-modal"]').on('click', function () {
      if (window.clearFormErrors) {
        window.clearFormErrors(form, errorBox);
      }
      const selectedIds = getSelectedUserIds();
      const input = form.querySelector('[data-selected-user-ids]');
      if (input) {
        input.value = selectedIds.join(',');
      }
      const countLabel = modal.querySelector('[data-selected-users-count]');
      if (countLabel) {
        countLabel.textContent = String(selectedIds.length);
      }
    });

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      if (window.clearFormErrors) {
        window.clearFormErrors(form, errorBox);
      }
      const selectedGroups = form.querySelectorAll('input[name="work_groups"]:checked');
      if (!selectedGroups.length) {
        if (errorBox) {
          errorBox.textContent = 'Select at least one department.';
          errorBox.classList.remove('d-none');
        }
        return;
      }
      const submitButton = form.querySelector("button[type='submit']");
      if (submitButton) {
        submitButton.disabled = true;
      }

      if (window.toggleFullScreenLoader){
        window.toggleFullScreenLoader(true);
      }
      try {
        if (window.postFormJson) {
          await window.postFormJson(form);
        }
        window.location.reload();
      } catch (data) {
        if (window.toggleFullScreenLoader){
          window.toggleFullScreenLoader(false)
        }
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });
  }

  function initUpdateUserStatus() {
    const updateStatusBtn = document.querySelector('[data-update-user-status]');
    if (!updateStatusBtn) {
      return;
    }
    updateStatusBtn.addEventListener('click', function (event) {
      const button = event.currentTarget;
      const userId = button.getAttribute('data-user-id');
      const action = button.getAttribute('data-action') || 'activate';
      const isDeactivateAction = action === 'deactivate';
      const title = isDeactivateAction ? 'Deactivate User' : 'Activate User';
      const message = `Are you sure you want to <strong>${action}</strong> this user?`;
      const warning = isDeactivateAction ? 'Deactivated users will lose access to the system. They can be reactivated later if needed.'
        : 'Activated users will be able to access the system immediately.';
      const endpoint = '/user-management/users/activate/';

      window.showDeleteConfirm({
        title: title,
        message: message,
        warning: warning,
        url: endpoint,
        method: 'POST',
        body: JSON.stringify({ ids: userId, action: action }),
        headers: {
          'Content-Type': 'application/json',
        },
        confirmButtonText: isDeactivateAction ? 'Deactivate' : 'Activate',
        confirmButtonClass: isDeactivateAction ? 'um-btn um-btn-danger' : 'um-btn um-btn-lime',
        showFullScreenLoader: true,
        onSuccess: function () {
          window.location.reload();
        },
      });
    });
  }

  function initInviteUser() {
    const inviteBtn = document.querySelector('[data-invite-user]');
    if (!inviteBtn) {
      return;
    }

    inviteBtn.addEventListener('click', function () {
      const user = {
        id: inviteBtn.getAttribute('data-user-id') || '',
        first_name: inviteBtn.getAttribute('data-first-name') || '',
        last_name: inviteBtn.getAttribute('data-last-name') || '',
        email: inviteBtn.getAttribute('data-email') || '',
        phone_number: inviteBtn.getAttribute('data-phone-number') || '',
      };
      const displayName = getUserDisplayname(user);
      const message = `Send an invitation to <strong>${displayName}</strong>?`;

      window.showDeleteConfirm({
        title: 'Invite User',
        message: message,
        warning: 'SMS invitations will only be sent when no email is available.',
        url: '/user-management/users/invite/',
        method: 'POST',
        body: JSON.stringify({ ids: String(user.id) }),
        headers: {
          'Content-Type': 'application/json',
        },
        confirmButtonText: 'Send invite',
        confirmButtonClass: 'um-btn um-btn-lime',
        showFullScreenLoader: true,
        onSuccess: function () {
          window.location.reload();
        },
      });
    });
  }
  window.addEventListener('load', function () {
    initAppUserForm();
    initDashboardUserForm();
    initEditDashboardUserForm();
    initEditUserForm();
    initUserSearch();
    initUserSelection();
    initAssignUsersToWorkGroups();
    initDeleteUsers();
    initDeleteUser();
    initDeactivateUsers();
    initActivateUsers();
    initInviteUsers();
    initUpdateUserStatus();
    initInviteUser();
  });
})();
