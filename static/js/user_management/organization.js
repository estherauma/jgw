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
        var homeUrl = form.getAttribute('data-home-url') || window.location.pathname;
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

  function initWorkCodeForm() {
    var form = document.getElementById('add-workcode-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('add-workcode-form-error');
    function resetWorkCodeForm() {
      safeClearFormErrors(form, errorBox);
      if (form) {
        form.reset();
      }
      syncOrganisation();
    }


    function syncOrganisation() {
      var selected = document.querySelector('[data-org-hidden]');
      var selectedId =  selected?.value || '' ;
      if (form) {
        var actionUrl = form.getAttribute('action');
        var url = new URL(actionUrl, window.location.origin);
        if (selectedId) {
          url.searchParams.set('selected_org_id', selectedId);
        } else {
          url.searchParams.delete('selected_org_id');
        }
        form.setAttribute('action', url.toString());
      }
      var targetLabel = document.querySelector('[data-workcode-org-label]');
      if (!targetLabel) {
        return;
      }

      var selected_option = document.getElementById('org-option-' + selectedId);
      if (selected_option) {
        targetLabel.textContent =
          selected_option.getAttribute('data-org-label') || 'None selected';
        return;
      }
      var label = document.querySelector('[data-org-selected-label]');
      var text = label ? label.textContent.trim() : '';
      targetLabel.textContent = text 
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
      syncOrganisation();
      var selected = document.querySelector('[data-org-hidden]');
      var selectedId = selected ? selected.value || '' : '';
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
          var homeUrl = form.getAttribute('data-home-url') || window.location.pathname;
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

    var modalEl = document.getElementById('add-workcode-modal');
    if (modalEl) {
      modalEl.addEventListener('show.bs.modal', syncOrganisation);
      modalEl.addEventListener('hidden.bs.modal', resetWorkCodeForm);
    }

  }

  window.addEventListener('load', initModalRedirect);
  window.addEventListener('load', initCreateOrgForm);
  window.addEventListener('load', initWorkCodeForm);

  function safeClearFormErrors(form, errorBox) {
    if (window.clearFormErrors) {
      window.clearFormErrors(form, errorBox);
    }
  }

})();
