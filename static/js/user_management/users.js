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
  
      if (!workGroups || workGroups.length === 0) {
          if (section) section.classList.add('d-none'); 
          return;
      }
  
      if (!section) {
          section = document.createElement('div');
          section.className = 'um-field form-group';
          section.setAttribute('data-workgroups-section', '');
          section.innerHTML = '<span>Work groups</span><div class="um-checkbox-list-scroll"></div>';
          form.querySelector('.modal-body').appendChild(section);
      }
  
      section.classList.remove('d-none');
      var container = section.querySelector('.um-checkbox-list-scroll');
      
      var html = '<ul class="um-checkbox-list">';
      for (var i = 0; i < workGroups.length; i++) {
          var wg = workGroups[i];
          var isChecked = selectedIds && selectedIds.indexOf(wg.id) !== -1 ? 'checked' : '';
          html += '<li><label><input type="checkbox" name="work_groups" value="' + wg.id + '" ' + isChecked + '> ' + wg.name + '</label></li>';
      }
      html += '</ul>';
      
      container.innerHTML = html;
  }
    $('[data-target="#edit-appuser-modal"]').on('click', function () {
      var $btn = $(this);
      var userId = $btn.data('user-id');
      
      form.action = '/user-management/app-users/' + userId + '/edit/';
      form.querySelector('[name="first_name"]').value = $btn.data('first-name') || '';
      form.querySelector('[name="last_name"]').value = $btn.data('last-name') || '';
      form.querySelector('[name="email"]').value = $btn.data('email') || '';

      var orgLabel = modal.querySelector('[data-appuser-org-label]');
      if (orgLabel) {
        orgLabel.textContent = $btn.data('org-name') || 'None';
      }

      var orgWorkGroups = $btn.data('org-work-groups') || [];
      var userWorkGroupsStr = String($btn.data('user-work-groups') || '');
      var userWorkGroupIds = userWorkGroupsStr ? userWorkGroupsStr.split(',').map(function(id) {
        return parseInt(id, 10);
      }) : [];

      renderWorkGroups(orgWorkGroups, userWorkGroupIds);
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
