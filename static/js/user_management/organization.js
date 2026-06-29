(function () {
  function initCreateOrganizationGroupForm() {
    const form = document.getElementById('create-organization-group-form');
    if (!form) {
      return;
    }
    const errorBox = document.getElementById('create-organization-group-form-error');

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
      const submitButton = form.querySelector("button[type='submit']");
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
        window.location.reload();
      } catch (data) {
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
      }
    });
  }

  function initEditOrganizationGroupForm() {
    const form = document.getElementById('edit-organization-group-form');
    if (!form) {
      return;
    }
    const errorBox = document.getElementById(
      'edit-organization-group-form-error',
    );

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
      const submitButton = form.querySelector("button[type='submit']");
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

  function initAttachOrganizationsToGroupForm() {
    const form = document.getElementById('attach-organizations-to-group-form');
    if (!form) {
      return;
    }
    const errorBox = document.getElementById(
      'attach-organizations-to-group-form-error',
    );
    const organizationsField = form.querySelector('[name="organizations"]');
    const submitButton = form.querySelector('[data-attach-organizations-submit]');
    initCustomFormSelects(form);

    function syncAttachSubmitState() {
      if (!organizationsField || !submitButton) {
        return;
      }
      const hasSelectedOrganizations = Array.from(
        organizationsField.selectedOptions || [],
      ).some(function (option) {
        return Boolean(option.value);
      });
      submitButton.classList.toggle('d-none', !hasSelectedOrganizations);
      submitButton.disabled = !hasSelectedOrganizations;
    }

    if (organizationsField) {
      organizationsField.addEventListener('change', syncAttachSubmitState);
    }
    syncAttachSubmitState();

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
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

  function initSyncOrganizationGroupCms() {
    $(document).on('click', '[data-sync-group-cms-btn]', function (event) {
      event.preventDefault();
      var $btn = $(this);
      var syncUrl = $btn.data('sync-url');
      var orgName = $btn.data('org-name') || 'this organization';
      var groupName = $btn.data('group-name') || 'this organization group';

      if (!syncUrl || !window.showDeleteConfirm) {
        console.log('Sync URL or confirmation dialog not available. Cannot sync to CMS.');
        return;
      }

      window.showDeleteConfirm({
        url: syncUrl,
        title: 'Sync to CMS',
        message:
          'This will permanently delete the existing Strapi partner configuration for "' +
          orgName +
          '" and move it to the "' +
          groupName +
          '" organization group partner configuration.',
        warning:
          'This action cannot be reversed. Continue only if you are sure.',
        confirmButtonText: 'Sync to CMS',
        confirmButtonClass: 'um-btn um-btn-blue',
        messageClass: 'um-confirm-warning-message',
        showFullScreenLoader: true,
        onSuccess: function () {
          window.location.reload();
        },
      });
    });
  }

  function initRemoveOrganizationFromGroup() {
    $(document).on('click', '[data-remove-org-group-btn]', function (event) {
      event.preventDefault();
      var $btn = $(this);
      var removeUrl = $btn.data('remove-url');
      var orgName = $btn.data('org-name') || 'this organization';
      var groupName = $btn.data('group-name') || 'this organization group';

      if (!removeUrl || !window.showDeleteConfirm) {
        return;
      }

      window.showDeleteConfirm({
        url: removeUrl,
        title: 'Remove from Group',
        message:
          'This will remove "' +
          orgName +
          '" from the "' +
          groupName +
          '" organization group.',
        warning:
          'If a standalone partner configuration does not exist in CMS, one will be created for the removed organization. This action cannot be reversed automatically.',
        confirmButtonText: 'Remove from group',
        confirmButtonClass: 'um-btn um-btn-danger',
        showFullScreenLoader: true,
        onSuccess: function () {
          window.location.reload();
        },
      });
    });
  }

  function initCreateOrgForm() {
    var form = document.getElementById('create-org-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('create-org-form-error');
    initCustomFormSelects(form);
    initIconPickers(form);
    syncContentCollectionForCustomContent(form);
    bindCustomContentSync(form);
    syncDefaultCollectionLanguageOptions(form);
    bindCollectionLanguageSync(form);

    function resetCreateOrgForm() {
      safeClearFormErrors(form, errorBox);
      form.reset();
      syncContentCollectionForCustomContent(form);
      syncDefaultCollectionLanguageOptions(form);
      refreshCustomFormSelects(form);
      resetIconPickers(form);
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
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
        var homeUrl = window.location.pathname;
        if (data && data.org_id) {
          window.location.href =
            homeUrl + '?selected_org_id=' + encodeURIComponent(data.org_id);
        } else if (homeUrl) {
          window.location.href = homeUrl;
        } else {
          window.location.reload();
        }
      } catch (data) {
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
      }
    });

    $('[data-target="#create-org-modal"]').on('click', function () {
      resetCreateOrgForm();
    });
  }

  function initEditOrgForm() {
    const modal = document.getElementById('edit-org-modal');
    if (!modal) return;

    const form = modal.querySelector('form');
    const errorBox = document.getElementById('edit-org-form-error');
    initCustomFormSelects(form);
    initIconPickers(form);
    syncContentCollectionForCustomContent(form);
    bindCustomContentSync(form);
    syncDefaultCollectionLanguageOptions(form);
    bindCollectionLanguageSync(form);

    const setDisabledFields = (disabled, organisation = null) => {
      ['name', 'org_code'].forEach((fieldName) => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
          field.disabled = disabled;
        }
      });

      const accessCodeField = form.querySelector('[name="access_code"]');
      if (!accessCodeField) {
        return;
      }

      const hasAccessCode = Boolean((organisation?.access_code || '').trim());
      accessCodeField.disabled = disabled && hasAccessCode;
    };

    const setFieldValue = (name, value) => {
      const field = form.querySelector(`[name="${name}"]`);
      if (!field) {
        return;
      }
      if (field.type === 'checkbox') {
        field.checked = value === true || value === 'true';
        return;
      }
      if (field.multiple) {
        const values = Array.isArray(value)
          ? value.map((item) => String(item).trim()).filter(Boolean)
          : String(value || '')
          .split(',')
          .map(function (item) {
            return item.trim();
          })
          .filter(Boolean);
        Array.prototype.forEach.call(field.options, function (option) {
          option.selected = values.indexOf(option.value) !== -1;
        });
        refreshCustomFormSelects(form);
        return;
      }
      if (field.type === 'file') {
        field.value = '';
        return;
      }
      field.value = value || '';
    };

    const populateEditOrgForm = (organisation) => {
      setFieldValue('name', organisation.name);
      setFieldValue('org_code', organisation.org_code);
      setFieldValue('access_code', organisation.access_code);
      setFieldValue('display_name', organisation.display_name);
      setFieldValue('has_custom_content', organisation.has_custom_content);
      setFieldValue('content_collection', organisation.content_collection);
      syncContentCollectionForCustomContent(form);
      setFieldValue('work_sector', organisation.work_sector);
      setFieldValue('custom_type', organisation.custom_type);
      setFieldValue('theme', organisation.theme);
      setFieldValue('collection_languages', organisation.collection_languages);
      syncDefaultCollectionLanguageOptions(form);
      setFieldValue(
        'default_collection_language',
        organisation.default_collection_language,
      );
      setFieldValue(
        'default_report_issue_emails',
        organisation.default_report_issue_emails,
      );
      setFieldValue(
        'default_feedback_emails',
        organisation.default_feedback_emails,
      );
      setFieldValue('big_icon', organisation.big_icon_url);
      setFieldValue('small_icon', organisation.small_icon_url);
      setIconPickerCurrent(form, 'big_icon_file', organisation.big_icon_url);
      setIconPickerCurrent(form, 'small_icon_file', organisation.small_icon_url);
      form.action = `/user-management/organisations/${organisation.id}/edit/`;
      refreshCustomFormSelects(form);
    };

    const loadOrganisationDetails = async ($button) => {
      const detailsUrl = $button.data('org-details-url');
      if (!detailsUrl) {
        throw new Error('Organisation details URL is missing.');
      }

      const response = await fetch(detailsUrl, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });
      const data = await response.json();
      if (!response.ok || !data?.ok || !data.organisation) {
        throw new Error(data?.error || 'Failed to load organisation details.');
      }

      return data.organisation;
    };

    $('[data-edit-btn]').on('click', async function() {
      const $btn = $(this);

      if (errorBox) {
        errorBox.classList.add('d-none');
        errorBox.textContent = '';
      }
      $(form).find('[data-error-for]').text('');
      setDisabledFields(false);

      try {
        const organisation = await loadOrganisationDetails($btn);
        populateEditOrgForm(organisation);
        setDisabledFields(true, organisation);
      } catch (error) {
        if (errorBox) {
          errorBox.textContent = error.message || 'Failed to load organisation details.';
          errorBox.classList.remove('d-none');
        }
      }
    });
  
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      safeClearFormErrors(form, errorBox);
  
      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) submitButton.disabled = true;
      if (window.toggleFullScreenLoader) {
        window.toggleFullScreenLoader(true);
      }
  
      try {
        setDisabledFields(false);
        if (window.postFormJson) {
          await window.postFormJson(form);
        }
        window.location.reload();
      } catch (data) {
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
        if (data && data.errors) {
          Object.keys(data.errors).forEach(function (field) {
            var el = form.querySelector("[data-error-for='" + field + "']");
            if (el) {
              el.textContent = data.errors[field].join(' ');
            }
          });
        }
        if (errorBox) {
          errorBox.textContent = (data && data.error) || 'Please fix the errors and try again.';
          errorBox.classList.remove('d-none');
        }
      } finally {
        setDisabledFields(true);
        if (submitButton) {
          submitButton.disabled = false;
        }
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
      }
    });
  }

  function initOrgSearch() {
    const input = document.querySelector('[data-org-search]');
    if (!input) {
      return;
    }
    const url = input.getAttribute('data-org-search-url');
    const tbody = document.querySelector('[data-org-table-body]');
    const paginationContainer = document.querySelector('[data-org-pagination]');
    
    if (!tbody || !paginationContainer) {
      return;
    }
    
    let debounceTimer = null;
    let controller = null;
    let currentPage = 1;

    function runSearch(value, page) {
      if (controller) {
        controller.abort();
      }
      controller = new AbortController();
      const params = new URLSearchParams();
      if (value) {
        params.set('q', value);
      }
      
      params.set('page', String(page || 1));
      
      fetch(url + (params.toString() ? '?' + params.toString() : ''), {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        signal: controller.signal,
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error('Search failed');
          }
          return response.json();
        })
        .then(function (data) {
          if (data && data.rows_html !== undefined) {
            tbody.innerHTML = data.rows_html;
            paginationContainer.innerHTML = data.pagination_html || '';
            currentPage = page || 1;
          }
        })
        .catch(function (error) {
          if (error.name === 'AbortError') {
            return;
          }
          console.error(error);
        });
    }

    input.addEventListener('input', function (event) {
      const value = (event.target.value || '').trim();
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        runSearch(value, 1);
      }, 250);
    });

    paginationContainer.addEventListener('click', function (event) {
      const trigger = event.target.closest('[data-org-page-link]');
      if (!trigger || trigger.disabled) {
        return;
      }
      event.preventDefault();
      
      const requestedPage = Number(
        trigger.getAttribute('data-page') || currentPage || 1
      );
      const value = (input.value || '').trim();
      
      runSearch(value, requestedPage);
    });
  }

  function initCustomFormSelects(form) {
    if (window.initUmSelects) {
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

  function syncDefaultCollectionLanguageOptions(form) {
    if (!form) {
      return;
    }

    const collectionLanguagesField = form.querySelector('[name="collection_languages"]');
    const defaultLanguageField = form.querySelector('[name="default_collection_language"]');

    if (!collectionLanguagesField || !defaultLanguageField) {
      return;
    }

    const currentDefaultLanguage = defaultLanguageField.value || '';
    const defaultLanguageRoot = defaultLanguageField.closest('[data-um-select]');
    const selectedCollectionLanguageOptions = Array.from(
      collectionLanguagesField.selectedOptions,
    ).filter((option) => option.value);
    defaultLanguageField.replaceChildren(
      (() => {
        const option = document.createElement('option');
        option.value = '';
        option.text = '';
        option.selected = !currentDefaultLanguage;
        return option;
      })(),
      ...selectedCollectionLanguageOptions.map((selectedOption) => {
        const option = document.createElement('option');
        option.value = selectedOption.value;
        option.text = selectedOption.text;
        option.selected = selectedOption.value === currentDefaultLanguage;
        return option;
      }),
    );

    if (
      currentDefaultLanguage &&
      !selectedCollectionLanguageOptions.some(
        (option) => option.value === currentDefaultLanguage,
      )
    ) {
      defaultLanguageField.value = '';
    }

    if (defaultLanguageRoot && window.rebuildUmSelect) {
      window.rebuildUmSelect(defaultLanguageRoot);
    }
  }

  function syncContentCollectionForCustomContent(form) {
    if (!form) {
      return;
    }

    const hasCustomContentField = form.querySelector('[name="has_custom_content"]');
    const contentCollectionField = form.querySelector('[name="content_collection"]');
    if (!hasCustomContentField || !contentCollectionField) {
      return;
    }

    const genericCollectionValue =
      contentCollectionField.getAttribute('data-generic-collection-value') || '';
    const genericCollectionLabel =
      contentCollectionField.getAttribute('data-generic-collection-label') || '';
    const contentCollectionRoot = contentCollectionField.closest('[data-um-select]');
    const currentValue = contentCollectionField.value || '';
    const allOptions = Array.from(contentCollectionField.options).map(function (option) {
      return {
        value: option.value,
        text: option.text,
      };
    });

    if (!contentCollectionField.dataset.allOptions) {
      contentCollectionField.dataset.allOptions = JSON.stringify(allOptions);
    }

    const storedOptions = JSON.parse(contentCollectionField.dataset.allOptions || '[]');
    const hasCustomContent = Boolean(hasCustomContentField.checked);
    const targetOptions = hasCustomContent
      ? storedOptions
      : storedOptions.filter(function (option) {
          return option.value === genericCollectionValue;
        });

    contentCollectionField.replaceChildren(
      ...targetOptions.map(function (option) {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.text = option.text;
        optionElement.selected = option.value === currentValue;
        return optionElement;
      }),
    );

    if (!hasCustomContent && genericCollectionValue) {
      contentCollectionField.value = genericCollectionValue;
    } else if (
      hasCustomContent &&
      Array.from(contentCollectionField.options).some(function (option) {
        return option.value === currentValue;
      })
    ) {
      contentCollectionField.value = currentValue;
    } else if (
      contentCollectionField.value &&
      !Array.from(contentCollectionField.options).some(function (option) {
        return option.value === contentCollectionField.value;
      })
    ) {
      contentCollectionField.value = '';
    }

    if (
      !hasCustomContent &&
      genericCollectionValue &&
      !Array.from(contentCollectionField.options).some(function (option) {
        return option.value === genericCollectionValue;
      })
    ) {
      const genericOption = document.createElement('option');
      genericOption.value = genericCollectionValue;
      genericOption.text = genericCollectionLabel || genericCollectionValue;
      genericOption.selected = true;
      contentCollectionField.appendChild(genericOption);
      contentCollectionField.value = genericCollectionValue;
    }

    if (contentCollectionRoot && window.rebuildUmSelect) {
      window.rebuildUmSelect(contentCollectionRoot);
    }
  }

  function bindCustomContentSync(form) {
    if (!form || form.getAttribute('data-custom-content-sync-ready') === 'true') {
      return;
    }

    const hasCustomContentField = form.querySelector('[name="has_custom_content"]');
    if (!hasCustomContentField) {
      return;
    }

    form.setAttribute('data-custom-content-sync-ready', 'true');
    hasCustomContentField.addEventListener('change', function () {
      syncContentCollectionForCustomContent(form);
      refreshCustomFormSelects(form);
    });
  }

  function bindCollectionLanguageSync(form) {
    if (!form || form.getAttribute('data-default-language-sync-ready') === 'true') {
      return;
    }

    const collectionLanguagesField = form.querySelector(
      '[name="collection_languages"]',
    );

    if (!collectionLanguagesField) {
      return;
    }

    form.setAttribute('data-default-language-sync-ready', 'true');
    collectionLanguagesField.addEventListener('change', () => {
      syncDefaultCollectionLanguageOptions(form);
      refreshCustomFormSelects(form);
    });
  }

  function initIconPickers(form) {
    if (window.initUmImagePickers) {
      window.initUmImagePickers(form);
    }
  }

  function resetIconPickers(form) {
    if (!form) {
      return;
    }
    setIconPickerCurrent(form, 'big_icon_file', '');
    setIconPickerCurrent(form, 'small_icon_file', '');
  }

  function setIconPickerCurrent(form, inputName, currentUrl) {
    if (!form || !window.refreshUmImagePicker) {
      return;
    }

    var input = form.querySelector('[name="' + inputName + '"]');
    var picker = input ? input.closest('[data-image-picker]') : null;
    if (!picker) {
      return;
    }

    window.refreshUmImagePicker(picker, currentUrl || '');
  }

  function initWorkCodeForm() {
    var form = document.getElementById('add-workcode-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('add-workcode-form-error');
    function resetWorkCodeForm() {
      safeClearFormErrors(form, errorBox);
      if (form) {
        form.reset();
      }
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization(
          'add-workcode-form',
          '[data-workcode-org-label]',
        );
      }
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization(
          'add-workcode-form',
          '[data-workcode-org-label]',
        );
      }
      var selectedInput = form.querySelector('[data-selected-org-id]');
      var selectedId = selectedInput ? selectedInput.value || '' : '';
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
        if (data && data.org_id) {
          var homeUrl = window.location.pathname;
          var target =
            homeUrl + '?selected_org_id=' + encodeURIComponent(data.org_id);
          window.location.href = target;
        } else {
          window.location.reload();
        }
      } catch (data) {
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
      }
    });

    $('[data-target="#add-workcode-modal"]').on('click', function () {
      resetWorkCodeForm();
      window.setupFieldReset('add-workcode-form', 'expiry_date');
    });
  }

  function initWorkGroupForm() {
    var form = document.getElementById('add-workgroup-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('add-workgroup-form-error');

    function resetWorkGroupForm() {
      safeClearFormErrors(form, errorBox);
      if (form) {
        form.reset();
      }
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization(
          'add-workgroup-form',
          '[data-workgroup-org-label]',
        );
      }
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization(
          'add-workgroup-form',
          '[data-workgroup-org-label]',
        );
      }
      var selectedInput = form.querySelector('[data-selected-org-id]');
      var selectedId = selectedInput?.value || '';
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
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
      }
    });

    $('[data-target="#add-workgroup-modal"]').on('click', function () {
      resetWorkGroupForm();
    });
  }

  function initDeleteWorkGroup() {
    $(document).on('click', '[data-delete-workgroup-btn]', function() {
      var $btn = $(this);
      var workGroupId = $btn.data('workgroup-id');
      var workGroupName = $btn.data('workgroup-name');

      if (window.showDeleteConfirm) {
        window.showDeleteConfirm({
          url: '/user-management/work-groups/' + workGroupId + '/delete/',
          title: 'Delete Work Group',
          message: 'Are you sure you want to delete the department "' + workGroupName + '"?',
          showFullScreenLoader: true,
          onSuccess: function() {
            window.location.reload();
          }
        });
      }
    });
  }

  function initDeleteWorkCode() {
    $(document).on('click', '[data-delete-workcode-btn]', function() {
      var $btn = $(this);
      var codeId = $btn.data('workcode-id');
      var codeValue = $btn.data('workcode-code');

      if (window.showDeleteConfirm) {
        window.showDeleteConfirm({
          url: '/user-management/work-codes/' + codeId + '/delete/',
          title: 'Delete Work Code',
          message: 'Are you sure you want to delete the work code "' + codeValue + '"?',
          onSuccess: function() {
            window.location.reload();
          }
        });
      }
    });
  }
  function initEditWorkGroupForm() {
    var modal = document.getElementById('edit-workgroup-modal');
    if (!modal) return;
  
    var form = modal.querySelector('form');
    var errorBox = document.getElementById('edit-workgroup-form-error');
  
    $('[data-edit-workgroup-btn]').on('click', function() {
      var $btn = $(this);
      form.querySelector('[name="name"]').value = $btn.data('workgroup-name') || '';
      form.action = '/user-management/work-groups/' + $btn.data('workgroup-id') + '/edit/';
  
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization('edit-workgroup-form', '#edit-workgroup-modal [data-workgroup-org-label]');
      }

      if (errorBox) errorBox.classList.add('d-none');
      $(form).find("[data-error-for]").text("");
    });
  
    form.addEventListener('submit', async function(event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
  
      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) submitButton.disabled = true;
      if (window.toggleFullScreenLoader) {
        window.toggleFullScreenLoader(true);
      }
  
      try {
        if (window.postFormJson) {
          await window.postFormJson(form);
        }
        window.location.reload();
      } catch (data) {
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
      }
    });
  }


  function safeClearFormErrors(form, errorBox) {
    if (window.clearFormErrors) {
      window.clearFormErrors(form, errorBox);
    }
  }

  function initAssignWorkCodeForm() {
    var form = document.getElementById('assign-workcode-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('assign-workcode-form-error');

    function resetAssignForm(codeValue, selectedGroups) {
      safeClearFormErrors(form, errorBox);
      form.reset();
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization(
          'assign-workcode-form',
          '[data-assign-org-label]',
        );
      }
      var codeLabel = form.querySelector('[data-assign-code-label]');
      if (codeLabel) {
        codeLabel.textContent = codeValue;
      }
      if (selectedGroups?.length) {
        const groupInputs = form.querySelectorAll('input[name="work_groups"]');
        groupInputs.forEach(function (input) {
          input.checked = selectedGroups.indexOf(input.value) !== -1;
        });
      }
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization(
          'assign-workcode-form',
          '[data-assign-org-label]',
        );
      }
      var selectedInput = form.querySelector('[data-selected-org-id]');
      var selectedId = selectedInput ? selectedInput.value || '' : '';
      var workCodeInput = form.querySelector('[data-workcode-id]');
      var workCodeId = workCodeInput ? workCodeInput.value || '' : '';
      if (!selectedId) {
        if (errorBox) {
          errorBox.textContent = 'Select an organisation first.';
          errorBox.classList.remove('d-none');
        }
        return;
      }
      if (!workCodeId) {
        if (errorBox) {
          errorBox.textContent = 'Select a work code first.';
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
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
      }
    });

    $(document).on('click', '[data-workcode-assign]', function () {
      var codeValue = this.getAttribute('data-workcode-code') || '';
      var codeId = this.getAttribute('data-workcode-id') || '';
      var groupIds = String(this.getAttribute('data-workcode-groups') || '')
        .split(',')
        .map(function (value) {
          return value.trim();
        })
        .filter(function (value) {
          return value.length > 0;
        });
      resetAssignForm(codeValue, groupIds);
      var workCodeInput = form.querySelector('[data-workcode-id]');
      workCodeInput.value = codeId || '';
      var codeLabel = form.querySelector('[data-assign-code-label]');
      if (codeLabel) {
        codeLabel.textContent = codeValue || '—';
      }
    });
  }

  function initUnassignWorkCodeForm() {
    var form = document.getElementById('unassign-workcode-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('unassign-workcode-form-error');
    var list = form.querySelector('[data-unassign-workgroup-list]');
    var emptyState = form.querySelector('[data-unassign-empty-state]');
    var summary = form.querySelector('[data-unassign-summary]');
    var submitButton = form.querySelector('[data-unassign-submit]');
    var initialGroupIds = [];

    function getWorkGroupNameById(groupId) {
      var input = document.querySelector(
        '#assign-workcode-form input[name="work_groups"][value="' + groupId + '"]',
      );
      if (!input) {
        return 'User group';
      }
      var label = input.closest('label');
      return label ? label.textContent.trim() : 'User group';
    }

    function getSelectedGroupIds() {
      return Array.from(form.querySelectorAll('input[name="work_groups"]')).map(
        function (input) {
          return input.value;
        },
      );
    }

    function getRemovedGroupIds() {
      var remaining = new Set(getSelectedGroupIds());
      return initialGroupIds.filter(function (groupId) {
        return !remaining.has(groupId);
      });
    }

    function syncSubmitState() {
      if (!submitButton) {
        return;
      }
      submitButton.disabled = getRemovedGroupIds().length === 0;
    }

    function syncEmptyState() {
      if (!emptyState || !list) {
        return;
      }
      emptyState.classList.toggle('d-none', getSelectedGroupIds().length > 0);
    }

    function syncSummary() {
      if (!summary) {
        return;
      }
      var removedGroupIds = getRemovedGroupIds();
      if (!removedGroupIds.length) {
        summary.classList.add('d-none');
        summary.textContent = '';
        return;
      }
      var removedGroupNames = removedGroupIds.map(getWorkGroupNameById);
      summary.classList.remove('d-none');
      summary.innerHTML =
        '<strong>Summary:</strong> You are about to unassign ' +
        removedGroupNames.join(', ') +
        ' from this work code.';
    }

    function renderGroupPills(groupIds) {
      if (!list) {
        return;
      }
      list.innerHTML = '';

      groupIds.forEach(function (groupId) {
        var hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'work_groups';
        hiddenInput.value = groupId;
        form.appendChild(hiddenInput);

        var pill = document.createElement('div');
        pill.className = 'um-pill';
        pill.setAttribute('data-group-id', groupId);

        var label = document.createElement('span');
        label.textContent = getWorkGroupNameById(groupId);

        var removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'um-pill-remove';
        removeBtn.setAttribute('data-unassign-remove', groupId);
        removeBtn.setAttribute('aria-label', 'Remove user group');
        removeBtn.textContent = '×';

        pill.appendChild(label);
        pill.appendChild(removeBtn);
        list.appendChild(pill);
      });

      syncEmptyState();
      syncSummary();
      syncSubmitState();
    }

    function resetUnassignForm(codeValue, selectedGroups) {
      safeClearFormErrors(form, errorBox);
      Array.from(form.querySelectorAll('input[name="work_groups"]')).forEach(
        function (input) {
          input.remove();
        },
      );
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization(
          'unassign-workcode-form',
          '[data-unassign-org-label]',
        );
      }
      var codeLabel = form.querySelector('[data-unassign-code-label]');
      if (codeLabel) {
        codeLabel.textContent = codeValue;
      }
      initialGroupIds = (selectedGroups || []).slice();
      var confirmError = form.querySelector('[data-error-for="confirmation"]');
      if (confirmError) {
        confirmError.textContent = '';
      }
      renderGroupPills(selectedGroups || []);
    }

    if (list) {
      list.addEventListener('click', function (event) {
        var removeButton = event.target.closest('[data-unassign-remove]');
        if (!removeButton) {
          return;
        }
        var groupId = removeButton.getAttribute('data-unassign-remove');
        var hiddenInput = form.querySelector(
          'input[name="work_groups"][value="' + groupId + '"]',
        );
        var pill = list.querySelector('[data-group-id="' + groupId + '"]');
        if (hiddenInput) {
          hiddenInput.remove();
        }
        if (pill) {
          pill.remove();
        }
        syncEmptyState();
        syncSummary();
        syncSubmitState();
      });
    }

    $(document).on('click', '[data-workcode-unassign]', function () {
      var codeValue = this.getAttribute('data-workcode-code') || '';
      var codeId = this.getAttribute('data-workcode-id') || '';
      var groupIds = String(this.getAttribute('data-workcode-groups') || '')
        .split(',')
        .map(function (value) {
          return value.trim();
        })
        .filter(Boolean);

      resetUnassignForm(codeValue, groupIds);

      var selectedInput = form.querySelector('[data-selected-org-id]');
      if (selectedInput && window.getSelectedOrgData) {
        var selectedOrg = window.getSelectedOrgData();
        selectedInput.value = selectedOrg && selectedOrg.id ? selectedOrg.id : '';
      }

      var workCodeInput = form.querySelector('[data-workcode-id]');
      if (workCodeInput) {
        workCodeInput.value = codeId;
      }
    });

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);

      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization(
          'unassign-workcode-form',
          '[data-unassign-org-label]',
        );
      }

      var selectedInput = form.querySelector('[data-selected-org-id]');
      var selectedId = selectedInput ? selectedInput.value || '' : '';
      var workCodeInput = form.querySelector('[data-workcode-id]');
      var workCodeId = workCodeInput ? workCodeInput.value || '' : '';
      if (!selectedId) {
        if (errorBox) {
          errorBox.textContent = 'Select an organisation first.';
          errorBox.classList.remove('d-none');
        }
        return;
      }
      if (!workCodeId) {
        if (errorBox) {
          errorBox.textContent = 'Select a work code first.';
          errorBox.classList.remove('d-none');
        }
        return;
      }
      if (getRemovedGroupIds().length === 0) {
        var confirmError = form.querySelector('[data-error-for="confirmation"]');
        if (confirmError) {
          confirmError.textContent = 'Remove at least one user group before continuing.';
        }
        return;
      }

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
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
        if (window.toggleFullScreenLoader) {
          window.toggleFullScreenLoader(false);
        }
      }
    });
  }

  function initEditWorkCodeForm() {
    var modal = document.getElementById('edit-workcode-modal');
    if (!modal) return;
  
    var form = modal.querySelector('form');
    var errorBox = document.getElementById('edit-workcode-form-error');
  
    $('[data-edit-code-btn]').on('click', function() {
      var $btn = $(this);
      var orgIdInput = form.querySelector('[name="selected_org_id"]');
      const orgId = $btn.data('workcode-org-id');
      var orgLabel = modal.querySelector('[data-workcode-org-label]')
      const requiresLogin = $btn.data('workcode-requires-login');
      var codeField = form.querySelector('[name="code"]');
      
      if (orgIdInput) {
        orgIdInput.value = orgId || '';
      }
      if (orgLabel) {
        orgLabel.textContent = $btn.data('workcode-org-name') || 'None selected';
      }
      codeField.value = $btn.data('workcode-code') || '';
      codeField.readOnly = true;
      codeField.classList.add('bg-light', 'text-muted');
      form.querySelector('[name="expiry_date"]').value = $btn.data('workcode-expiry-date') || '';
      form.querySelector('[name="requires_login"]').checked = (String(requiresLogin).toLowerCase() === 'true');
      form.action = '/user-management/work-codes/' + $btn.data('workcode-id') + '/edit/';

      if (errorBox) errorBox.classList.add('d-none');
      $(form).find("[data-error-for]").text("");
      window.setupFieldReset('edit-workcode-form', 'expiry_date');
    });
  
    form.addEventListener('submit', async function(event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
  
      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) submitButton.disabled = true;
  
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
  
  window.addEventListener('load', function () {
    initCreateOrganizationGroupForm();
  });
  window.addEventListener('load', function () {
    initEditOrganizationGroupForm();
  });
  window.addEventListener('load', function () {
    initAttachOrganizationsToGroupForm();
  });
  window.addEventListener('load', function () {
    initSyncOrganizationGroupCms();
  });
  window.addEventListener('load', function () {
    initRemoveOrganizationFromGroup();
  });
  window.addEventListener('load', function () {
    initCreateOrgForm();
  });
  window.addEventListener('load', function () {
    initOrgSearch();
  });
  window.addEventListener('load', function () {
    initWorkCodeForm();
  });
  window.addEventListener('load', function () {
    initWorkGroupForm();
  });
  window.addEventListener('load', function () {
    initAssignWorkCodeForm();
  });
  window.addEventListener('load', function () {
    initUnassignWorkCodeForm();
  });
  window.addEventListener('load', function () {
    initEditOrgForm();
  });
  window.addEventListener('load', ()=>{
    initEditWorkGroupForm();
  });
  window.addEventListener('load', ()=>{
    initDeleteWorkGroup();
  });
  window.addEventListener('load', ()=>{
    initEditWorkCodeForm();
    initDeleteWorkCode();
  });
})();
