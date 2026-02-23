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

    function clearErrors(form, errorBox) {
      if (window.clearFormErrors) {
        window.clearFormErrors(form, errorBox);
      }
    }
  
    $('[data-target="#edit-appuser-modal"]').on('click', function () {
      var $btn = $(this);
      
      form.querySelector('[name="first_name"]').value = $btn.data('user-first-name') || '';
      form.querySelector('[name="last_name"]').value = $btn.data('user-last-name') || '';
      form.querySelector('[name="email"]').value = $btn.data('user-email') || '';

      var userID = $btn.data('user-id');
      form.action = '/user-management/app-users/' + userID + '/edit/';

      if (errorBox) errorBox.classList.add('d-none');
      $(form).find("[data-error-for]").text("");
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
        console.log('Edit user error response:', data);
        if (data && data.errors) {
          console.log('Errors object:', data.errors);
          Object.keys(data.errors).forEach(function (field) {
            console.log('Processing field:', field, 'error:', data.errors[field]);
            var el = form.querySelector("[data-error-for='" + field + "']");
            console.log('Found element for field:', field, el);
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
      }
    });
  }

  window.addEventListener('load', initAppUserForm);
  window.addEventListener('load', initEditUserForm);
})();
