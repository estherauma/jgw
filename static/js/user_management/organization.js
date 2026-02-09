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
    var errorBox = document.getElementById('create-org-form-error');
    var fieldErrors = form.querySelectorAll('[data-error-for]');

    function clearErrors() {
      if (errorBox) {
        errorBox.classList.add('d-none');
        errorBox.textContent = '';
      }
      fieldErrors.forEach(function (el) {
        el.textContent = '';
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
