(function () {
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

    function clearErrors() {
      if (window.clearFormErrors) {
        window.clearFormErrors(form, errorBox);
      }
    }

    function resetAppUserForm() {
      clearErrors();
      form.reset();
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization('add-appuser-form', '[data-appuser-org-label]');
      }
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      clearErrors();
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


    $('[data-target="#add-appuser-modal"]').on('click', function () {
      resetAppUserForm();
    });
  }

  function initDashboardUserForm() {
    var form = document.getElementById('add-dashboard-user-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('add-dashboard-user-form-error');

    function clearErrors() {
      if (window.clearFormErrors) {
        window.clearFormErrors(form, errorBox);
      }
    }

    function resetDashboardForm() {
      clearErrors();
      form.reset();
    }

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
        $('#add-dashboard-user-modal').modal('hide');
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

    $('[data-target="#add-dashboard-user-modal"]').on('click', function () {
      resetDashboardForm();
    });
  }

  function initEditDashboardUserForm() {
    var modal = document.getElementById('edit-dashboard-user-modal');
    if (!modal) {
      return;
    }
    var form = modal.querySelector('form');
    var errorBox = document.getElementById('edit-dashboard-user-form-error');

    function clearErrors() {
      if (window.clearFormErrors) {
        window.clearFormErrors(form, errorBox);
      }
    }

    function setSingleValue(name, value) {
      var input = form.querySelector('[name="' + name + '"]');
      if (input) {
        input.value = value || '';
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
      var inputs = form.querySelectorAll('input[name="' + name + '"]');
      inputs.forEach(function (input) {
        input.checked = valueSet.has(String(input.value));
      });
    }

    function resetForm() {
      clearErrors();
      form.reset();
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
        setMultiValues('organisation_data', user.organisation_data);
        setMultiValues('factories', user.factories);
        setMultiValues('destinations', user.destinations);
        setMultiValues('user_languages', user.user_languages);
        setMultiValues('excluded_origin_countries', user.excluded_origin_countries);
        setMultiValues('immigration_status', user.immigration_status);
      } catch (err) {
        console.error('Failed to fetch dashboard user data:', err);
      }
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

    function clearErrors() {
      if (window.clearFormErrors) {
        window.clearFormErrors(form, errorBox);
      }
    }

    function renderWorkGroups(workGroups, selectedIds,workGroupsContainer) {
      var section = modal.querySelector('[data-workgroups-section]');
      

      if (!workGroups?.length) {
        workGroupsContainer.innerHTML = '<p>No work groups available.</p>';
        return;
      }
      const workGroupOptions = workGroups.map(function (group, index) {
        var value = group.id;
        var checked = selectedIds.indexOf(value) !== -1 ? ' checked' : '';
        var inputId = 'id_work_groups_' + index;
        return (
          '<li>' +
          '<label for="' +
          inputId +
          '">' +
          '<input type="checkbox" name="work_groups" value="' +
          value +
          '" id="' +
          inputId +
          '"' +
          checked +
          '> ' +
          group.name +
          '</label>' +
          '</li>'
        );
      });
      workGroupsContainer.innerHTML = '<ul>' + workGroupOptions.join('') + '</ul>';

    }

    $('[data-target="#edit-appuser-modal"]').on('click', async function () {
      var $btn = $(this);
      var userId = $btn.data('user-id');
      var editUrl = '/user-management/app-users/' + userId + '/edit/';
      
      form.action = editUrl;
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
          form.querySelector('[name="role_group"]').value = user.role_group_id || '';
          form.querySelector('[name="phone_number"]').value = user.phone_local || '';
          var countryField = form.querySelector('[name="phone_country_iso"]');
          if (countryField) {
            countryField.value =
              user.phone_country_iso || countryField.options?.[0]?.value || '';
          }

          var orgLabel = modal.querySelector('[data-appuser-org-label]');
          if (orgLabel) {
            orgLabel.textContent = user.organisation_name || 'None';
          }

          renderWorkGroups(data.work_groups, user.work_group_ids,workGroupsContainer);
        }
      } catch (err) {
        console.error('Failed to fetch user data:', err);
      }
    });

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      clearErrors(form, errorBox);

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

  function initUserSearch() {
    const input = document.querySelector('[data-user-search]');
    if (!input) {
      return;
    }
    const url = input.getAttribute('data-user-search-url');
    const tbody = document.querySelector('[data-users-table-body]');
    if (!url || !tbody) {
      return;
    }
    let debounceTimer = null;
    let controller = null;

    async function runSearch(value) {
      if (controller) {
        controller.abort();
      }
      controller = new AbortController();
      const params = new URLSearchParams();
      if (value) {
        params.set('q', value);
      }
      var storedOrg = window.getSelectedOrgData
        ? window.getSelectedOrgData()
        : null;
      const selectedOrgId = storedOrg?.id ? String(storedOrg.id) : '';
 
      if (selectedOrgId) {
        params.set('selected_org_id', selectedOrgId);
      }
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
        if (data?.html) {
          tbody.innerHTML = data.html;
          updateAssignButtonState();
          updateDeleteButton();
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
        runSearch(value);
      }, 250);
    });
  }

  function updateDeleteButton() {
    const deleteButton = document.querySelector('[data-users-delete]');
    if (!deleteButton) {
      return;
    }
    const selectedIds = getSelectedUserIds();
    deleteButton.disabled = selectedIds.length === 0;
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
    }

    selectAll.addEventListener('change', function (event) {
      const checked = event.target.checked;
      const checkboxes = document.querySelectorAll('[data-user-select]');
      checkboxes.forEach(function (input) {
        input.checked = checked;
      });
      updateSelectionState();
      updateDeleteButton();
      
    });

    document.addEventListener('change', function (event) {
      if (event.target && event.target.matches('[data-user-select]')) {
        updateSelectionState();
        updateDeleteButton();
      }
    });
  }

  function initDeleteUsers() {
    const deleteBtn = document.querySelector('[data-users-delete]');
    if (!deleteBtn) {
      return;
    }

    deleteBtn.addEventListener('click', function () {
      const selectedIds = getSelectedUserIds();
      const count = selectedIds.length;
      
      if (!selectedIds.length) {
        alert('Select at least one user to delete.');
        return;
      }

      window.showDeleteConfirm({
        title: `Delete ${count === 1 ? 'User' : 'Users'}`,
        message: `Are you sure you want to delete ${count === 1? 'the selected user': `the ${count} selected users`}?`,
        url: '/user-management/users/delete/',
        method: 'POST',
        body: JSON.stringify({ ids: selectedIds.join(',') }),
        headers: {
          'Content-Type': 'application/json',
          },
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
          errorBox.textContent = 'Select at least one work group.';
          errorBox.classList.remove('d-none');
        }
        return;
      }
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

  window.addEventListener('load', function () {
    initAppUserForm();
    initDashboardUserForm();
    initEditDashboardUserForm();
    initEditUserForm();
    initUserSearch();
    initUserSelection();
    initAssignUsersToWorkGroups();
    initDeleteUsers();
  });
})();
