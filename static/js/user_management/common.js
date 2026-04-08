(function () {
  function clearFormErrors(form, errorBox) {
    if (errorBox) {
      errorBox.classList.add('d-none');
      errorBox.textContent = '';
    }
    if (!form) {
      return;
    }
    var fieldErrors = form.querySelectorAll('[data-error-for]');
    fieldErrors.forEach(function (el) {
      el.textContent = '';
    });
  }
  window.clearFormErrors = clearFormErrors;

  function storeSelectedOrganisation(orgId, orgName) {
    if (!window.localStorage) {
      return;
    }
    if (!orgId) {
      window.localStorage.removeItem('selectedOrg');
      return;
    }
    window.localStorage.setItem(
      'selectedOrg',
      JSON.stringify({ id: orgId, name: orgName || '' }),
    );
  }

  function getSelectedOrgData() {
    if (!window.localStorage) {
      return null;
    }
    try {
      var stored = window.localStorage.getItem('selectedOrg');
      return stored ? JSON.parse(stored) : null;
    } catch (err) {
      console.error('Error parsing stored organization data:', err);
      return null;
    }
  }

  window.storeSelectedOrganisation = storeSelectedOrganisation;
  window.getSelectedOrgData = getSelectedOrgData;

  function syncSelectedOrganization(formId, labelSelector) {
    if (window.isOrgAdminOrStaff) {
      return;
    }
    var form = document.getElementById(formId);
    var selectedId = '';
    var selectedName = '';
    var storedOrg = window.getSelectedOrgData();
    if (storedOrg) {
      selectedId = storedOrg.id ? String(storedOrg.id) : '';
      selectedName = storedOrg.name;
    }
    if (!selectedId) {
      var selected = document.querySelector('[data-org-hidden]');
      selectedId = selected?.value || '';
      if (!selectedId) {
        var initialOption = document.querySelector(
          '[data-org-selected="true"]',
        );
        if (initialOption) {
          selectedId = initialOption.getAttribute('data-org-value') || '';
        }
      }
      if (selected && selectedId) {
        selected.value = selectedId;
      }
    }
    if (form) {
      var hiddenInput = form.querySelector('[data-selected-org-id]');
      if (hiddenInput) {
        hiddenInput.value = selectedId;
      }
    }
    var selectedHidden = document.querySelector('[data-org-hidden]');
    if (selectedHidden && selectedId) {
      selectedHidden.value = selectedId;
    }
    var targetLabel = document.querySelector(labelSelector);
    if (!targetLabel) {
      return;
    }
    targetLabel.textContent = selectedName;
  }

  window.syncSelectedOrganization = syncSelectedOrganization;

  async function postFormJson(form) {
    var response = await fetch(form.action, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: new FormData(form),
    });
    var data = await response.json();
    if (!response.ok) {
      throw data;
    }
    return data;
  }

  window.postFormJson = postFormJson;

  function handleErrors({ form, errorBox, data, errorMessage }) {
    if (data && data.errors) {
      Object.keys(data.errors).forEach(function (field) {
        if (!form) {
          return;
        }
        var el = form.querySelector("[data-error-for='" + field + "']");
        if (el) {
          el.textContent = data.errors[field].join(' ');
        }
      });
    }
    if (errorBox) {
      errorBox.textContent = errorMessage || data?.error || 'Please fix the errors and try again.';
      errorBox.classList.remove('d-none');
    }
  }

  window.handleErrors = handleErrors;


  function showDeleteConfirm(options) {
    var modal = document.getElementById('confirm-modal');
    const confirmBtn = modal.querySelector('[data-confirm-btn]');
    const errorDiv = document.getElementById('confirm-error'); 
    
    if (!modal || !confirmBtn) {
      console.error('Confirm modal not found');
      return;
    }

    if (errorDiv) {
      errorDiv.classList.add('d-none');
      errorDiv.textContent = '';
    }

    if (confirmBtn) {
      confirmBtn.innerHTML = options.confirmButtonText || 'Delete';
      confirmBtn.className = options.confirmButtonClass || 'um-btn um-btn-danger';
    }

    var messageEl = modal.querySelector('[data-message]');
    if (messageEl) {
      messageEl.innerHTML = options.message || 'Are you sure you want to delete this item?';
    }

    var warningEl = modal.querySelector('[data-warning]');
    if (warningEl) {
      warningEl.innerHTML = options.warning || 'This action can not be reversed.';
    }

    var titleEl = modal.querySelector('[data-title]');
    if (titleEl) {
      titleEl.innerHTML = options.title || 'Confirm Deletion';
    }

    $(modal).modal('show');

    confirmBtn.onclick = async function () {
      const confirmBtn = modal.querySelector('[data-confirm-btn]');
      const loader = document.getElementById('um-fullscreen-loader');
      confirmBtn.disabled = true;
      if (options.showFullScreenLoader && loader) {
        loader.classList.remove('d-none');
      }
      if (errorDiv) {
              errorDiv.classList.add('d-none');
              errorDiv.textContent = '';
            }

      try {
        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        var response = await fetch(options.url, {
          method: options.method || 'POST',
          headers: {
            ...(options.headers || {}),
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
          },
          body: options.body || null,
        });
        
        var data = await response.json();

        if (!data.ok) {
          window.handleErrors({ errorBox: errorDiv, data: data }); 
          return;
        } 

        $(modal).one('hidden.bs.modal', function() {
            options?.onSuccess(data);
        });
        $(modal).modal('hide');
      } catch (err) {
        window.handleErrors({ 
          errorBox: errorDiv, 
          data: err, 
          errorMessage: 'An error occurred while communicating with the server.' 
        });
      } finally {
        confirmBtn.disabled = false;
        if (options.showFullScreenLoader && loader) {
          loader.classList.add('d-none');
        }
      }
    };
  }

  window.showDeleteConfirm = showDeleteConfirm;

  function syncThumb(container, track, thumb) {
    if (!thumb || !track || !container) {
      return;
    }
    var scrollHeight = container.scrollHeight;
    var clientHeight = container.clientHeight;
    if (scrollHeight <= clientHeight) {
      track.style.display = 'none';
      thumb.style.height = track.clientHeight + 'px';
      thumb.style.top = '0px';
      return;
    }
    track.style.display = '';
    var thumbHeight = Math.max(
      24,
      Math.floor((clientHeight / scrollHeight) * track.clientHeight),
    );
    thumb.style.height = thumbHeight + 'px';
    var maxThumbTop = track.clientHeight - thumbHeight;
    var scrollTop = container.scrollTop;
    var maxScrollTop = scrollHeight - clientHeight;
    var thumbTop = Math.floor((scrollTop / maxScrollTop) * maxThumbTop);
    thumb.style.top = thumbTop + 'px';
  }

  function attachScrollbar(container, track, thumb) {
    if (!thumb || !track || !container) {
      return;
    }
    var dragState = {
      dragging: false,
      startY: 0,
      startScrollTop: 0,
    };

    function updateFromThumb(deltaY) {
      var scrollHeight = container.scrollHeight;
      var clientHeight = container.clientHeight;
      var maxScrollTop = scrollHeight - clientHeight;
      if (maxScrollTop <= 0) {
        return;
      }
      var trackHeight = track.clientHeight;
      var thumbHeight = thumb.offsetHeight;
      var maxThumbTop = trackHeight - thumbHeight;
      var ratio = maxScrollTop / maxThumbTop;
      container.scrollTop = dragState.startScrollTop + deltaY * ratio;
    }

    thumb.addEventListener('mousedown', function (event) {
      event.preventDefault();
      dragState.dragging = true;
      dragState.startY = event.clientY;
      dragState.startScrollTop = container.scrollTop;
      document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', function (event) {
      if (!dragState.dragging) {
        return;
      }
      updateFromThumb(event.clientY - dragState.startY);
    });

    document.addEventListener('mouseup', function () {
      if (!dragState.dragging) {
        return;
      }
      dragState.dragging = false;
      document.body.style.userSelect = '';
    });

    track.addEventListener('click', function (event) {
      if (event.target === thumb) {
        return;
      }
      var rect = track.getBoundingClientRect();
      var clickY = event.clientY - rect.top;
      var scrollHeight = container.scrollHeight;
      var clientHeight = container.clientHeight;
      var maxScrollTop = scrollHeight - clientHeight;
      if (maxScrollTop <= 0) {
        return;
      }
      var trackHeight = track.clientHeight;
      var thumbHeight = thumb.offsetHeight;
      var maxThumbTop = trackHeight - thumbHeight;
      var thumbTop = Math.min(
        Math.max(clickY - thumbHeight / 2, 0),
        maxThumbTop,
      );
      container.scrollTop = (thumbTop / maxThumbTop) * maxScrollTop;
    });
  }

  function initScrollbars() {
    var wrappers = document.querySelectorAll('.um-table-scroll-wrapper');
    wrappers.forEach(function (wrapper) {
      var container = wrapper.querySelector('.um-table-scroll');
      var track = wrapper.querySelector('.um-scrollbar');
      var thumb = wrapper.querySelector('.um-scrollbar-thumb');
      attachScrollbar(container, track, thumb);
      syncThumb(container, track, thumb);
      container.addEventListener('scroll', function () {
        syncThumb(container, track, thumb);
      });
    });
  }

  function syncAllThumbs() {
    var wrappers = document.querySelectorAll('.um-table-scroll-wrapper');
    wrappers.forEach(function (wrapper) {
      var container = wrapper.querySelector('.um-table-scroll');
      var track = wrapper.querySelector('.um-scrollbar');
      var thumb = wrapper.querySelector('.um-scrollbar-thumb');
      syncThumb(container, track, thumb);
    });
  }
  
  function setupFieldReset(formId, inputName) {
    const form = document.getElementById(formId);
    if (!form) return;

    const targetInput = form.querySelector(`[name="${inputName}"]`);
    
    const resetBtn = form.querySelector(`[data-reset-for="${inputName}"]`);
    
    if (!targetInput || !resetBtn) return;

    const toggleBtn = () => {
        resetBtn.classList.toggle('d-none', !targetInput.value);
    };

    if (targetInput.dataset.fieldResetListenerAttached) {
      toggleBtn();
      return; 
    }

    targetInput.addEventListener('input', toggleBtn);
    targetInput.addEventListener('change', toggleBtn);

    targetInput.dataset.fieldResetListenerAttached = "true";
    
    toggleBtn();

    resetBtn.onclick = function() {
      targetInput.value = '';
      toggleBtn();
      targetInput.dispatchEvent(new Event('input', { bubbles: true }));
      targetInput.dispatchEvent(new Event('change', { bubbles: true }));
    };
  }

  window.setupFieldReset = setupFieldReset;

  window.addEventListener('load', initScrollbars);
  window.addEventListener('resize', syncAllThumbs);
})();
