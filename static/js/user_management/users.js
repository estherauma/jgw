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

    function renderWorkGroups(workGroups, selectedIds) {
      var section = modal.querySelector('[data-workgroups-section]');
      var container = modal.querySelector('.um-checkbox-list-scroll');
      if (!section || !container) return;

      if (!workGroups || workGroups.length === 0) {
        section.hidden = true;
        container.innerHTML = '';
        return;
      }

      var html = '<ul class="um-checkbox-list">';
      for (var group of workGroups) {

          var isChecked = selectedIds && selectedIds.indexOf(group.id) !== -1 ? 'checked' : '';

          html += `<li><label><input type="checkbox" name="work_groups" value="${group.id}" class="form-check-input" ${isChecked}> ${group.name}</label></li>`;
        }
      html += '</ul>';
      container.innerHTML = html;
      section.hidden = false;
    }

    $('[data-target="#edit-appuser-modal"]').on('click', async function () {
      var $btn = $(this);
      var userId = $btn.data('user-id');
      var editUrl = '/user-management/app-users/' + userId + '/edit/';
      
      form.action = editUrl;
      form.querySelector('[name="first_name"]').value = $btn.data('first-name') || '';
      form.querySelector('[name="last_name"]').value = $btn.data('last-name') || '';
      form.querySelector('[name="email"]').value = $btn.data('email') || '';

      var orgLabel = modal.querySelector('[data-appuser-org-label]');
      if (orgLabel) {
        orgLabel.textContent = $btn.data('org-name') || 'None';
      }

      try {
        var response = await fetch(editUrl);
        var data = await response.json();
        if (data.ok) {
          renderWorkGroups(data.work_groups, data.user.work_group_ids);
        }
      } catch (err) {
        console.error('Failed to fetch work groups:', err);
      }

      clearErrors();
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
