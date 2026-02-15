(function () {
  function initOrgForm() {
    var modal = document.getElementById('create-org-modal');
    if (!modal) {
      return;
    }

    const form = modal.querySelector('form');
    const modalTitle = modal.querySelector('.um-modal-title');
    const submitBtn = form.querySelector("button[type='submit']");
    const errorBox = modal.querySelector('.alert-danger'); 
    const fieldErrors = modal.querySelectorAll('[data-error-for]');

    const nameInput = form.querySelector('input[name="name"]');
    const codeInput = form.querySelector('input[name="org_code"]');

    function clearErrors() {
      if (errorBox) {
          errorBox.classList.add('d-none');
          errorBox.textContent = '';
      }
      fieldErrors.forEach(el => { el.textContent = ''; });
    }

    modal.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget; 
      clearErrors();

      if (button && button.classList.contains('btn-edit-org')) {
        const orgId = button.getAttribute('data-org-id');
        const orgName = button.getAttribute('data-org-name');
        const orgCode = button.getAttribute('data-org-code');
        const editBaseUrl = form.getAttribute('data-edit-url-base');
        form.action = editBaseUrl.replace('0', orgId);

        modalTitle.textContent = 'Edit Organisation';
        submitBtn.textContent = 'Save Changes';

        if (nameInput) nameInput.value = orgName;
        if (codeInput) codeInput.value = orgCode;

      } 

      else {
        modalTitle.textContent = 'Create New Organisation';
        submitBtn.textContent = 'Create';
        form.action = form.getAttribute('data-create-url');
        form.reset(); 
      }
    });

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      clearErrors();
      submitBtn.disabled = true;

      fetch(form.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: new FormData(form),
      })
        .then((response) => {
          if (response.ok) return response.json();
          return response.json().then((err) => {
            throw err;
          });
        })
        .then(() => {
          const homeUrl = form.getAttribute('data-home-url');
          window.location.href = homeUrl || window.location.pathname;
        })
        .catch(data => {
            if (data && data.errors) {
                Object.keys(data.errors).forEach(field => {
                    const el = form.querySelector(`[data-error-for="${field}"]`);
                    if (el) {
                        const error = data.errors[field];
                        el.textContent = Array.isArray(error) ? error[0] : error;
                    }
                });

                if (errorBox) {
                    errorBox.textContent = "Please correct the errors highlighted below.";
                    errorBox.classList.remove('d-none');
                }
            }
        })
        .finally(() => {
          submitBtn.disabled = false;
        });
    });
  }

  window.addEventListener('DOMContentLoaded', initOrgForm);
})();