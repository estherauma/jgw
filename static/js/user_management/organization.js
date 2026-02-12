(function () {
  function initModalRedirect() {
    var modal = document.getElementById('create-org-modal');
    if (!modal) {
      return;
    }
    modal.addEventListener('hidden.bs.modal', function () {
      var homeUrl = modal.getAttribute('data-home-url');
      if (homeUrl && window.location.pathname !== homeUrl) {
        window.location.href = homeUrl;
      }
    });
  }

  function initCreateOrgForm() {
    var form = document.getElementById('create-org-form');
    if (!form) {
      return;
    }
    var modal = document.getElementById('create-org-modal');
    var modalTitle = document.getElementById('create-org-title');
    var errorBox = document.getElementById('create-org-form-error');
    var fieldErrors = form.querySelectorAll('[data-error-for]');
    var nameInput = form.querySelector('[name="name"]');
    var codeInput = form.querySelector('[name="org_code"]');
    var baseUrl = form.getAttribute('data-base-url');
    var createUrl = form.getAttribute('data-create-url');

    function clearErrors() {
      if (errorBox) {
        errorBox.classList.add('d-none');
        errorBox.textContent = '';
      }
      fieldErrors.forEach(function (el) {
        el.textContent = '';
      });
    }

    document.addEventListener('click', function (event) {
      var btn = event.target.closest('.btn-edit-org');
      if (!btn) {
        return;
      }
      var orgId = btn.getAttribute('data-org-id');
      var orgName = btn.getAttribute('data-org-name');
      var orgCode = btn.getAttribute('data-org-code');

      if (modalTitle) {
        modalTitle.textContent = 'Edit organisation';
      }
      nameInput.value = orgName;
      codeInput.value = orgCode;
      form.action = baseUrl + orgId + '/edit/';
      clearErrors();
    });

    if (modal) {
      modal.addEventListener('show.bs.modal', function (event) {
        var relatedTarget = event.relatedTarget;
        if (relatedTarget && !relatedTarget.classList.contains('btn-edit-org')) {
          if (modalTitle) {
            modalTitle.textContent = 'Create new organisation';
          }
          form.action = createUrl;
          nameInput.value = '';
          codeInput.value = '';
          clearErrors();
        }
      });
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      clearErrors();
      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) {
        submitButton.disabled = true;
      }
      fetch(form.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: new FormData(form),
      })
        .then(function (response) {
          if (response.ok) {
            return response.json();
          }
          return response.json().then(function (data) {
            throw data;
          });
        })
        .then(function () {
          var homeUrl = form.getAttribute('data-home-url');
          if (homeUrl) {
            window.location.href = homeUrl;
          } else {
            window.location.reload();
          }
        })
        .catch(function (data) {
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
        })
        .finally(function () {
          if (submitButton) {
            submitButton.disabled = false;
          }
        });
    });
  }

  window.addEventListener('load', initModalRedirect);
  window.addEventListener('load', initCreateOrgForm);
})();
