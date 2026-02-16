(function () {
  
  function safeClearFormErrors(form, errorBox) {
    if (window.clearFormErrors) {
      window.clearFormErrors(form, errorBox);
    } else {
      if (errorBox) {
        errorBox.classList.add('d-none');
        errorBox.textContent = '';
      }
      form.querySelectorAll('[data-error-for]').forEach(el => el.textContent = '');
    }
  }

  function initOrgForm() {
    const modals = document.querySelectorAll('[id$="-org-modal"]');
  
    modals.forEach((modal) => {
        const form = modal.querySelector('form');
        if (!form) return;

        const submitBtn = form.querySelector("button[type='submit']");
        const errorBox = modal.querySelector('.alert-danger');

        modal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            safeClearFormErrors(form, errorBox);

            if (modal.id === 'edit-org-modal' && button) {
                const orgId = button.getAttribute('data-org-id');
                const editBaseUrl = form.getAttribute('data-edit-url-base');
                form.action = editBaseUrl.replace('0', orgId);
            } else {
                form.action = form.getAttribute('data-create-url');
                if (modal.id === 'create-org-modal') form.reset();
            }
        });

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
      if (submitBtn) submitBtn.disabled = true;

      try {
        let data = null;
        if (window.postFormJson) {
          data = await window.postFormJson(form);
        } else {
          const response = await fetch(form.action, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: new FormData(form),
          });
          data = await response.json();
          if (!response.ok) throw data;
        }

        const homeUrl = form.getAttribute('data-home-url') || window.location.pathname;
        if (data && data.org_id) {
          window.location.href = `${homeUrl}?selected_org_id=${encodeURIComponent(data.org_id)}`;
        } else {
          window.location.href = homeUrl;
        }
      } catch (err) {
        if (err && err.errors) {
          Object.keys(err.errors).forEach(field => {
            const el = form.querySelector(`[data-error-for="${field}"]`);
            if (el) {
              const error = err.errors[field];
              el.textContent = Array.isArray(error) ? (error[0].message || error[0]) : error;
            }
          });
        }
        if (errorBox) {
          errorBox.textContent = 'Please fix the errors and try again.';
          errorBox.classList.remove('d-none');
        }
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  });
  }

  
  function initModalRedirect() {
    var modal = document.getElementById('create-org-modal');
    if (!modal) return;
    modal.addEventListener('hidden.bs.modal', function () {
      var homeUrl = modal.getAttribute('data-home-url');
      if (homeUrl && window.location.pathname !== homeUrl) {
        window.location.href = homeUrl;
      }
    });
  }

  
  function initWorkCodeForm() {
    var form = document.getElementById('add-workcode-form');
    if (!form) return;
    var errorBox = document.getElementById('add-workcode-form-error');

    function syncOrganisation() {
      var selected = document.querySelector('[data-org-hidden]');
      var selectedId = selected?.value || '';
      if (form) {
        var actionUrl = form.getAttribute('action');
        var url = new URL(actionUrl, window.location.origin);
        if (selectedId) url.searchParams.set('selected_org_id', selectedId);
        else url.searchParams.delete('selected_org_id');
        form.setAttribute('action', url.toString());
      }
      var targetLabel = document.querySelector('[data-workcode-org-label]');
      if (!targetLabel) return;

      var selected_option = document.getElementById('org-option-' + selectedId);
      if (selected_option) {
        targetLabel.textContent = selected_option.getAttribute('data-org-label') || 'None selected';
      }
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) submitButton.disabled = true;

      try {
        var data = null;
        if (window.postFormJson) data = await window.postFormJson(form);
        if (data && data.org_id) {
          var homeUrl = form.getAttribute('data-home-url') || window.location.pathname;
          window.location.href = homeUrl + '?selected_org_id=' + encodeURIComponent(data.org_id);
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

    var modalEl = document.getElementById('add-workcode-modal');
    if (modalEl) {
      modalEl.addEventListener('show.bs.modal', syncOrganisation);
      modalEl.addEventListener('hidden.bs.modal', () => {
        safeClearFormErrors(form, errorBox);
        form.reset();
        syncOrganisation();
      });
    }
  }

  window.addEventListener('load', initModalRedirect);
  window.addEventListener('load', initOrgForm);
  window.addEventListener('load', initWorkCodeForm);
})();