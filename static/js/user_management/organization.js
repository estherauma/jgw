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

  function initEditOrgForm() {
    var modal = document.getElementById('edit-org-modal');
    if (!modal) return;
  
    var form = modal.querySelector('form');
    var errorBox = document.getElementById('edit-org-form-error');
  
    $('[data-edit-btn]').on('click', function() {
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

  function initOrgSearch() {
    const input = document.querySelector('[data-org-search]');
    const url = input.getAttribute('data-org-search-url');
    const tbody = document.querySelector('[data-org-table-body]');
    let debounceTimer = null;
    let controller = null;

    function runSearch(value) {
      if (controller) {
        controller.abort();
      }
      controller = new AbortController();
      const params = new URLSearchParams();
      if (value) {
        params.set('q', value);
      }
      fetch(url + (params.toString() ? '?' + params.toString() : ''), {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        signal: controller.signal,
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error('Search failed');
          }
          return response.json();
        })
        .then(function (data) {
          if (data && data.html !== undefined) {
            tbody.innerHTML = data.html;
          }
        })
        .catch(function (error) {
          if (error.name === 'AbortError') {
            return;
          }
          console.error(error);
        });
    }

    input.addEventListener('input', function (event) {
      const value = (event.target.value || '').trim();
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        runSearch(value);
      }, 250);
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
        if (data && data.org_id && !window.isOrgAdmin) {
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

    $('[data-target="#add-workgroup-modal"]').on('click', function () {
      resetWorkGroupForm();
    });
  }

  function initDeleteWorkGroup() {
    $(document).on('click', '[data-delete-workgroup-btn]', function() {
      var $btn = $(this);
      var workGroupId = $btn.data('workgroup-id');
      var workGroupName = $btn.data('workgroup-name');

      if (window.showDeleteConfirm) {
        window.showDeleteConfirm({
          url: '/user-management/work-groups/' + workGroupId + '/delete/',
          itemName: workGroupName,
          onSuccess: function() {
            window.location.reload();
          }
        });
      }
    });
  }

  window.addEventListener('load', ()=>{
    initCreateOrgForm();
    initOrgSearch();
    initWorkCodeForm();
    initWorkGroupForm();
    initAssignWorkCodeForm();
    initEditOrgForm();
    initDeleteWorkGroup();
  })

  function safeClearFormErrors(form, errorBox) {
    if (window.clearFormErrors) {
      window.clearFormErrors(form, errorBox);
    }
  }

  function initAssignWorkCodeForm() {
    var form = document.getElementById('assign-workcode-form');
    if (!form) {
      return;
    }
    var errorBox = document.getElementById('assign-workcode-form-error');
    var codeLabel = document.querySelector('[data-assign-code-label]');

    function resetAssignForm(codeValue, selectedGroups) {
      safeClearFormErrors(form, errorBox);
      form.reset();
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization(
          'assign-workcode-form',
          '[data-assign-org-label]',
        );
      }
      if (codeLabel) {
        codeLabel.textContent = codeValue;
      }
      if (selectedGroups?.length) {
        const groupInputs = form.querySelectorAll('input[name="work_groups"]');
        groupInputs.forEach(function (input) {
          input.checked = selectedGroups.indexOf(input.value) !== -1;
        });
      }
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      safeClearFormErrors(form, errorBox);
      if (window.syncSelectedOrganization) {
        window.syncSelectedOrganization(
          'assign-workcode-form',
          '[data-assign-org-label]',
        );
      }
      var selectedInput = form.querySelector('[data-selected-org-id]');
      var selectedId = selectedInput ? selectedInput.value || '' : '';
      var workCodeInput = form.querySelector('[data-workcode-id]');
      var workCodeId = workCodeInput ? workCodeInput.value || '' : '';
      if (!selectedId) {
        if (errorBox) {
          errorBox.textContent = 'Select an organisation first.';
          errorBox.classList.remove('d-none');
        }
        return;
      }
      if (!workCodeId) {
        if (errorBox) {
          errorBox.textContent = 'Select a work code first.';
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
        if (data && data.org_id && !window.isOrgAdmin) {
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

    $(document).on('click', '[data-workcode-assign]', function () {
      var codeValue = $(this).data('workcode-code') || '';
      var codeId = $(this).data('workcode-id') || '';
      var groupIds = String($(this).data('workcode-groups') || '')
        .split(',')
        .map(function (value) {
          return value.trim();
        })
        .filter(function (value) {
          return value.length > 0;
        });
      resetAssignForm(codeValue, groupIds);
      var workCodeInput = form.querySelector('[data-workcode-id]');
      workCodeInput.value = codeId || '';
    });
  }
})();
