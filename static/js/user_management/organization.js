(function () {
  function initCreateOrgForm() {
    var form = document.getElementById('create-org-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('create-org-form-error');

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) {
        submitButton.disabled = true;
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
        if (data && data.errors) {
          Object.keys(data.errors).forEach(function (field) {
            var el = form.querySelector("[data-error-for='" + field + "']");
            if (el) {
              el.textContent = data.errors[field].join(' ');
            }
          });
        }
        if (errorBox) {
          errorBox.textContent = 'Please fix the errors and try again.';
          errorBox.classList.remove('d-none');
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });
  }

  function initEditOrgForm() {
    var modal = document.getElementById('edit-org-modal');
    if (!modal) return;
  
    var form = modal.querySelector('form');
    var errorBox = document.getElementById('edit-org-form-error');
  
    $('.btn-edit-org').on('click', function() {
      var $btn = $(this);
      form.querySelector('[name="name"]').value = $btn.data('org-name');
      form.querySelector('[name="org_code"]').value = $btn.data('org-code');
      form.action = '/user-management/organisations/' + $btn.data('org-id') + '/edit/';
  
      if (errorBox) errorBox.classList.add('d-none');
      $(form).find("[data-error-for]").text("");
    });
  
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      safeClearFormErrors(form, errorBox);
  
      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) submitButton.disabled = true;
  
      try {
        if (window.postFormJson) {
          await window.postFormJson(form);
        }
        window.location.reload();
      } catch (data) {
        if (data && data.errors) {
          Object.keys(data.errors).forEach(function (field) {
            var el = form.querySelector("[data-error-for='" + field + "']");
            if (el) {
              el.textContent = data.errors[field].join(' ');
            }
          });
        }
        if (errorBox) {
          errorBox.textContent = 'Please fix the errors and try again.';
          errorBox.classList.remove('d-none');
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });
  }

  function initWorkCodeForm() {
    var form = document.getElementById('add-workcode-form');
    if (!form) return;
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
      if (submitButton) submitButton.disabled = true;

      try {
        var data = null;
        if (window.postFormJson) data = await window.postFormJson(form);
        if (data && data.org_id) {
          var homeUrl = window.location.pathname;
          var target =
            homeUrl + '?selected_org_id=' + encodeURIComponent(data.org_id);
          window.location.href = target;
        } else {
          window.location.reload();
        }
      } catch (err) {
        if (err && err.errors) {
          Object.keys(err.errors).forEach(field => {
            var el = form.querySelector("[data-error-for='" + field + "']");
            if (el) el.textContent = Array.isArray(err.errors[field]) ? err.errors[field].join(' ') : err.errors[field];
          });
        }
        if (errorBox) {
          errorBox.textContent = 'Please fix the errors and try again.';
          errorBox.classList.remove('d-none');
        }
      } finally {
        if (submitButton) submitButton.disabled = false;
      }
    });

    $('[data-target="#add-workcode-modal"]').on('click', function () {
      resetWorkCodeForm();
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
        if (data && data.org_id) {
          var homeUrl = window.location.pathname;
          var target =
            homeUrl + '?selected_org_id=' + encodeURIComponent(data.org_id);
          window.location.href = target;
        } else {
          window.location.reload();
        }
      } catch (data) {
        if (data && data.errors) {
          Object.keys(data.errors).forEach(function (field) {
            var el = form.querySelector("[data-error-for='" + field + "']");
            if (el) {
              el.textContent = data.errors[field].join(' ');
            }
          });
        }
        if (errorBox) {
          errorBox.textContent = 'Please fix the errors and try again.';
          errorBox.classList.remove('d-none');
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

  window.addEventListener('load', initCreateOrgForm);
  window.addEventListener('load', initEditOrgForm);
  window.addEventListener('load', initWorkCodeForm);
  window.addEventListener('load', initWorkGroupForm);

  function safeClearFormErrors(form, errorBox) {
    if (window.clearFormErrors) {
      window.clearFormErrors(form, errorBox);
    }
  }
})();
