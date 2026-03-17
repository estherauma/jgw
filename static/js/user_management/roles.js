(function () {
  var addForm = document.getElementById('add-role-form');
  var editForm = document.getElementById('edit-role-form');
  var addErrorBox = document.getElementById('add-role-form-error');
  var editErrorBox = document.getElementById('edit-role-form-error');

  function clearRoleErrors(form, errorBox) {
    if (window.clearFormErrors) {
      window.clearFormErrors(form, errorBox);
    }
  }

  function setPermissions(form, permissionIds) {
    if (!form) {
      return;
    }
    var inputs = form.querySelectorAll('input[name="permissions"]');
    inputs.forEach(function (input) {
      var value = parseInt(input.value, 10);
      input.checked = permissionIds.indexOf(value) !== -1;
    });
  }

  if (addForm) {
    addForm.addEventListener('submit', async function (event) {
      event.preventDefault();
      clearRoleErrors(addForm, addErrorBox);

      var submitButton = addForm.querySelector("button[type='submit']");
      if (submitButton) submitButton.disabled = true;

      try {
        if (window.postFormJson) {
          await window.postFormJson(addForm);
        }
        window.location.reload();
      } catch (data) {
        if (window.handleErrors) {
          window.handleErrors({ form: addForm, errorBox: addErrorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });
  }

  if (editForm) {
    editForm.addEventListener('submit', async function (event) {
      event.preventDefault();
      clearRoleErrors(editForm, editErrorBox);

      var submitButton = editForm.querySelector("button[type='submit']");
      if (submitButton) submitButton.disabled = true;

      try {
        if (window.postFormJson) {
          await window.postFormJson(editForm);
        }
        window.location.reload();
      } catch (data) {
        if (window.handleErrors) {
          window.handleErrors({ form: editForm, errorBox: editErrorBox, data: data });
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });
  }

  $('[data-target="#add-role-modal"]').on('click', function () {
    clearRoleErrors(addForm, addErrorBox);
  });

  $('[data-role-edit]').on('click', async function () {
    var $btn = $(this);
    var roleId = $btn.data('role-id');
    var editUrl = '/user-management/roles/' + roleId + '/edit/';

    if (!editForm) {
      return;
    }

    editForm.action = editUrl;
    clearRoleErrors(editForm, editErrorBox);

    try {
      var response = await fetch(editUrl);
      var data = await response.json();
      if (!data.ok) {
        window.handleErrors({ form: editForm, errorBox: editErrorBox, data: data });
        return;
      }
      var role = data.role;
      editForm.querySelector('[name="name"]').value = role.name || '';
      editForm.querySelector('[name="description"]').value = role.description || '';
      var accessField = editForm.querySelector('[name="grants_dashboard_access"]');
      if (accessField) {
        accessField.checked = !!role.grants_dashboard_access;
      }
      setPermissions(editForm, role.permission_ids || []);
    } catch (err) {
      console.error('Failed to fetch role data:', err);
    }
  });

  $('[data-role-delete]').on('click', function () {
    var $btn = $(this);
    var roleId = $btn.data('role-id');
    var roleName = $btn.data('role-name') || 'this role';
    var deleteUrl = '/user-management/roles/' + roleId + '/delete/';

    if (!window.showDeleteConfirm) {
      return;
    }

    window.showDeleteConfirm({
      title: 'Delete role',
      message: 'Delete "' + roleName + '"?',
      warning: 'Users assigned to this role will lose its permissions.',
      url: deleteUrl,
      onSuccess: function () {
        window.location.reload();
      },
    });
  });
})();
