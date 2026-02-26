(function () {
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

  window.addEventListener('load', initAppUserForm);
  window.addEventListener('load', initEditUserForm);
})();
