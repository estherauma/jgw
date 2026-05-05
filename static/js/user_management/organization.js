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

  function initCreateOrgForm() {
    var form = document.getElementById('create-org-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('create-org-form-error');
    initCustomFormSelects(form);
    initIconPickers(form);
    syncDefaultCollectionLanguageOptions(form);
    bindCollectionLanguageSync(form);

    function resetCreateOrgForm() {
      safeClearFormErrors(form, errorBox);
      form.reset();
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
    syncDefaultCollectionLanguageOptions(form);
    bindCollectionLanguageSync(form);

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
      setFieldValue('work_sector', organisation.work_sector);
      setFieldValue('custom_type', organisation.custom_type);
      setFieldValue('theme', organisation.theme);
      setFieldValue('collection_languages', organisation.collection_languages);
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
      syncDefaultCollectionLanguageOptions(form);
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

      try {
        const organisation = await loadOrganisationDetails($btn);
        populateEditOrgForm(organisation);
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
    if (!tbody) {
      return;
    }
    let debounceTimer = null;
    let controller = null;

    function runSearch(value) {
      if (controller) {
        controller.abort();
      }
      controller = new AbortController();
      const params = new URLSearchParams();
      if (value) {
        params.set('q', value);
      }
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
          if (data && data.html !== undefined) {
            tbody.innerHTML = data.html;
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
        runSearch(value);
      }, 250);
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
        if (window.handleErrors) {
          window.handleErrors({ form: form, errorBox: errorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
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
      try {
        var data = null;
        if (window.postFormJson) {
          data = await window.postFormJson(form);
        }
        if (data && data.org_id && !window.isOrgAdmin) {
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
        if (submitButton) {
          submitButton.disabled = false;
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
    var codeLabel = document.querySelector('[data-assign-code-label]');

    function resetAssignForm(codeValue, selectedGroups) {
      safeClearFormErrors(form, errorBox);
      form.reset();
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization(
          'assign-workcode-form',
          '[data-assign-org-label]',
        );
      }
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
      try {
        var data = null;
        if (window.postFormJson) {
          data = await window.postFormJson(form);
        }
        if (data && data.org_id && !window.isOrgAdmin) {
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
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });

    $(document).on('click', '[data-workcode-assign]', function () {
      var codeValue = $(this).data('workcode-code') || '';
      var codeId = $(this).data('workcode-id') || '';
      var groupIds = String($(this).data('workcode-groups') || '')
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
