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

  function createAsyncOrganisationPicker(root, config) {
    config = config || {};
    if (!root) {
      return null;
    }

    const toggle = root.querySelector(config.toggleSelector);
    const menu = root.querySelector(config.menuSelector);
    const searchInput = root.querySelector(config.searchInputSelector);
    const optionsContainer = root.querySelector(config.optionsContainerSelector);
    const hiddenInput = root.querySelector(config.hiddenInputSelector);
    const label = root.querySelector(config.labelSelector);
    const searchUrl = root.getAttribute(config.urlAttribute || 'data-org-options-url') || '';
    const placeholder =
      root.getAttribute(config.placeholderAttribute || 'data-org-placeholder') ||
      config.placeholder ||
      'Select organisation';
    const noResultsMessage = config.noResultsMessage || 'No organisations found.';
    const loadErrorMessage = config.loadErrorMessage || 'Could not load organisations.';
    const optionValueAttr = config.optionValueAttribute || 'data-async-org-value';
    const optionLabelAttr = config.optionLabelAttribute || 'data-async-org-label';
    const optionNameAttr = config.optionNameAttribute || 'data-async-org-name';
    const optionCodeAttr = config.optionCodeAttribute || 'data-async-org-code';
    const optionCreatedAtAttr =
      config.optionCreatedAtAttribute || 'data-async-org-created-at';
    const optionSelector = config.optionSelector || '[data-async-org-option]';
    const emptyStateAttr = config.emptyStateAttribute || 'data-async-org-empty-state';
    let controller = null;
    let debounceTimer = null;
    let hasLoaded = false;
    let currentPage = 0;
    let hasNextPage = true;
    let isLoading = false;
    let currentQuery = '';
    let selectedId = root.getAttribute(config.initialIdAttribute || 'data-initial-org-id') || '';
    let selectedLabel =
      root.getAttribute(config.initialLabelAttribute || 'data-initial-org-label') || '';

    if (
      !toggle ||
      !menu ||
      !searchInput ||
      !optionsContainer ||
      !hiddenInput ||
      !label ||
      !searchUrl
    ) {
      return null;
    }

    function updateLabel(text) {
      const displayText = text || placeholder;
      label.textContent = displayText;
      root.classList.toggle('is-placeholder', !text);
    }

    function closeMenu() {
      root.classList.remove('is-open');
      menu.classList.remove('is-open');
      if (currentQuery) {
        currentQuery = '';
        currentPage = 0;
        hasNextPage = true;
        hasLoaded = false;
      }
      searchInput.value = '';
    }

    function renderEmptyState(message) {
      optionsContainer.innerHTML =
        '<div class="um-select-option text-muted" ' +
        emptyStateAttr +
        '>' +
        message +
        '</div>';
    }

    function getSelectedValue() {
      return (hiddenInput.value || '').trim();
    }

    function syncSelectedState() {
      const currentSelected = getSelectedValue();
      optionsContainer.querySelectorAll(optionSelector).forEach(function (option) {
        const isSelected = option.getAttribute(optionValueAttr) === currentSelected;
        option.classList.toggle('is-selected', isSelected);
      });
    }

    function buildOptionData(option) {
      return {
        id: option.getAttribute(optionValueAttr) || '',
        label: option.getAttribute(optionLabelAttr) || '',
        name: option.getAttribute(optionNameAttr) || '',
        code: option.getAttribute(optionCodeAttr) || '',
        created_at: option.getAttribute(optionCreatedAtAttr) || '',
      };
    }

    function setValue(value, text, suppressChange) {
      hiddenInput.value = value || '';
      selectedId = value || '';
      selectedLabel = text || '';
      updateLabel(text || '');
      syncSelectedState();
      if (!suppressChange) {
        hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }

    function handleSelection(option) {
      const data = buildOptionData(option);
      setValue(data.id, data.label, false);
      if (config.onSelect) {
        config.onSelect(data, api);
      }
      closeMenu();
    }

    function createOptionElement(org) {
      const option = document.createElement('button');
      const isSelected = selectedId && String(org.id) === String(selectedId);
      option.type = 'button';
      option.className = 'um-select-option' + (isSelected ? ' is-selected' : '');
      option.setAttribute('data-async-org-option', '');
      option.setAttribute(optionValueAttr, String(org.id));
      option.setAttribute(optionLabelAttr, org.name || '');
      option.setAttribute(optionNameAttr, org.name || '');
      option.setAttribute(optionCodeAttr, org.org_code || '');
      option.setAttribute(optionCreatedAtAttr, org.created_at || '');
      option.textContent = org.name || '';
      return option;
    }

    function renderOptions(items, append) {
      if (!items.length) {
        if (!append) {
          renderEmptyState(noResultsMessage);
        }
        return;
      }

      const fragment = document.createDocumentFragment();
      items.forEach(function (org) {
        fragment.appendChild(createOptionElement(org));
      });

      if (append) {
        const emptyState = optionsContainer.querySelector('[' + emptyStateAttr + ']');
        if (emptyState) {
          emptyState.remove();
        }
        optionsContainer.appendChild(fragment);
      } else {
        optionsContainer.innerHTML = '';
        optionsContainer.appendChild(fragment);
      }

      syncSelectedState();
    }

    function loadOptions(page, append, query) {
      currentQuery = query || '';
      if (isLoading) {
        return;
      }
      if (!append && controller) {
        controller.abort();
      }
      controller = new AbortController();
      isLoading = true;
      const params = new URLSearchParams();
      params.set('page', String(page || 1));
      if (currentQuery) {
        params.set('q', currentQuery);
      }

      fetch(searchUrl + '?' + params.toString(), {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        signal: controller.signal,
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error('Organisation load failed');
          }
          return response.json();
        })
        .then(function (data) {
          renderOptions(data?.options || [], append);
          currentPage = page || 1;
          hasNextPage = Boolean(data?.has_next);
          hasLoaded = true;
        })
        .catch(function (error) {
          if (error.name === 'AbortError') {
            return;
          }
          console.error(error);
          if (!append) {
            renderEmptyState(loadErrorMessage);
          }
        })
        .finally(function () {
          isLoading = false;
        });
    }

    const api = {
      getValue: getSelectedValue,
      setValue: function (value, text, suppressChange) {
        setValue(value, text, suppressChange);
      },
      clear: function (suppressChange) {
        setValue('', '', suppressChange);
        if (config.onClear) {
          config.onClear(api);
        }
      },
      close: closeMenu,
      loadOptions: loadOptions,
      root: root,
      hiddenInput: hiddenInput,
    };

    toggle.addEventListener('click', function () {
      const isOpen = !root.classList.contains('is-open');
      root.classList.toggle('is-open', isOpen);
      menu.classList.toggle('is-open', isOpen);

        if (isOpen) {
          searchInput.focus();
          searchInput.select();
          if (!hasLoaded) {
            loadOptions(1, false, currentQuery);
          }
        } else {
          searchInput.value = '';
      }
    });

    searchInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        currentPage = 0;
        hasNextPage = true;
        loadOptions(1, false, (searchInput.value || '').trim());
      }, 250);
    });

    optionsContainer.addEventListener('scroll', function () {
      if (!hasNextPage || isLoading) {
        return;
      }
      const remaining =
        optionsContainer.scrollHeight -
        optionsContainer.scrollTop -
        optionsContainer.clientHeight;
      if (remaining <= 40) {
        loadOptions(currentPage + 1, true, currentQuery);
      }
    });

    optionsContainer.addEventListener('click', function (event) {
      const option = event.target.closest(optionSelector);
      if (!option || !optionsContainer.contains(option)) {
        return;
      }
      handleSelection(option);
    });

    document.addEventListener('click', function (event) {
      if (!root.contains(event.target)) {
        closeMenu();
      }
    });

    setValue(selectedId, selectedLabel, true);
    return api;
  }

  window.createAsyncOrganisationPicker = createAsyncOrganisationPicker;

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

  async function postFormJson(form, options) {
    options = options || {};
    var headers = {
      'X-Requested-With': 'XMLHttpRequest',
    };
    var body = null;

    if (options.asJson) {
      var csrfToken =
        form?.querySelector('[name=csrfmiddlewaretoken]')?.value ||
        document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
        '';
      headers['X-CSRFToken'] = csrfToken;
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(options.payload || {});
    } else {
      body = new FormData(form);
    }

    var response = await fetch(form.action, {
      method: options.method || 'POST',
      headers: headers,
      body: body,
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

  function toggleFullScreenLoader(show) {
    var loader = document.querySelector('.um-fullscreen-loader');
    if (!loader) {
      return;
    }
    loader.classList.toggle('d-none', !show);
  }

  window.toggleFullScreenLoader = toggleFullScreenLoader;


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
      messageEl.className = 'um-navy' + (options.messageClass ? ' ' + options.messageClass : '');
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
      const loader = document.querySelector('.um-fullscreen-loader');
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
        if (options.showFullScreenLoader && loader){
          loader.classList.add('d-none')
        }
      }
    };
  }

  window.showDeleteConfirm = showDeleteConfirm;

  function syncScrollbar(container, track, thumb, axis) {
    if (!thumb || !track || !container) {
      return;
    }
    var isX = axis === 'x';
    var scrollSize = isX ? container.scrollWidth : container.scrollHeight;
    var clientSize = isX ? container.clientWidth : container.clientHeight;
    if (scrollSize <= clientSize) {
      track.style.display = 'none';
      if (isX) {
        thumb.style.width = track.clientWidth + 'px';
        thumb.style.left = '0px';
      } else {
        thumb.style.height = track.clientHeight + 'px';
        thumb.style.top = '0px';
      }
      return;
    }
    track.style.display = '';
    var trackSize = isX ? track.clientWidth : track.clientHeight;
    var thumbSize = Math.max(
      24,
      Math.floor((clientSize / scrollSize) * trackSize),
    );
    if (isX) {
      thumb.style.width = thumbSize + 'px';
    } else {
      thumb.style.height = thumbSize + 'px';
    }
    var maxThumbPos = trackSize - thumbSize;
    var scrollPos = isX ? container.scrollLeft : container.scrollTop;
    var maxScrollPos = scrollSize - clientSize;
    var thumbPos = Math.floor((scrollPos / maxScrollPos) * maxThumbPos);
    if (isX) {
      thumb.style.left = thumbPos + 'px';
    } else {
      thumb.style.top = thumbPos + 'px';
    }
  }

  function attachScrollbar(container, track, thumb, axis) {
    if (!thumb || !track || !container) {
      return;
    }
    var isX = axis === 'x';
    var dragState = {
      dragging: false,
      startPos: 0,
      startScroll: 0,
    };

    function updateFromThumb(delta) {
      var scrollSize = isX ? container.scrollWidth : container.scrollHeight;
      var clientSize = isX ? container.clientWidth : container.clientHeight;
      var maxScroll = scrollSize - clientSize;
      if (maxScroll <= 0) {
        return;
      }
      var trackSize = isX ? track.clientWidth : track.clientHeight;
      var thumbSize = isX ? thumb.offsetWidth : thumb.offsetHeight;
      var maxThumbPos = trackSize - thumbSize;
      var ratio = maxScroll / maxThumbPos;
      if (isX) {
        container.scrollLeft = dragState.startScroll + delta * ratio;
      } else {
        container.scrollTop = dragState.startScroll + delta * ratio;
      }
    }

    thumb.addEventListener('mousedown', function (event) {
      event.preventDefault();
      dragState.dragging = true;
      dragState.startPos = isX ? event.clientX : event.clientY;
      dragState.startScroll = isX ? container.scrollLeft : container.scrollTop;
      document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', function (event) {
      if (!dragState.dragging) {
        return;
      }
      var delta = isX ? event.clientX - dragState.startPos : event.clientY - dragState.startPos;
      updateFromThumb(delta);
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
      var clickPos = isX ? event.clientX - rect.left : event.clientY - rect.top;
      var scrollSize = isX ? container.scrollWidth : container.scrollHeight;
      var clientSize = isX ? container.clientWidth : container.clientHeight;
      var maxScroll = scrollSize - clientSize;
      if (maxScroll <= 0) {
        return;
      }
      var trackSize = isX ? track.clientWidth : track.clientHeight;
      var thumbSize = isX ? thumb.offsetWidth : thumb.offsetHeight;
      var maxThumbPos = trackSize - thumbSize;
      var thumbPos = Math.min(
        Math.max(clickPos - thumbSize / 2, 0),
        maxThumbPos,
      );
      var targetScroll = (thumbPos / maxThumbPos) * maxScroll;
      if (isX) {
        container.scrollLeft = targetScroll;
      } else {
        container.scrollTop = targetScroll;
      }
    });
  }

  function initScrollbars() {
    var wrappers = document.querySelectorAll('.um-table-scroll-wrapper');
    wrappers.forEach(function (wrapper) {
      var container = wrapper.querySelector('.um-table-scroll');
      var trackY =
        wrapper.querySelector('.um-scrollbar-y') ||
        wrapper.querySelector('.um-scrollbar:not(.um-scrollbar-x)') ||
        wrapper.querySelector('.um-scrollbar');
      var thumbY = trackY
        ? trackY.querySelector('.um-scrollbar-thumb-y') ||
          trackY.querySelector('.um-scrollbar-thumb')
        : null;
      var trackX = wrapper.querySelector('.um-scrollbar-x');
      var thumbX = trackX
        ? trackX.querySelector('.um-scrollbar-thumb-x') ||
          trackX.querySelector('.um-scrollbar-thumb')
        : null;
      attachScrollbar(container, trackY, thumbY, 'y');
      attachScrollbar(container, trackX, thumbX, 'x');
      syncScrollbar(container, trackY, thumbY, 'y');
      syncScrollbar(container, trackX, thumbX, 'x');
      container.addEventListener('scroll', function () {
        syncScrollbar(container, trackY, thumbY, 'y');
        syncScrollbar(container, trackX, thumbX, 'x');
      });
    });
  }

  function syncAllThumbs() {
    var wrappers = document.querySelectorAll('.um-table-scroll-wrapper');
    wrappers.forEach(function (wrapper) {
      var container = wrapper.querySelector('.um-table-scroll');
      var trackY =
        wrapper.querySelector('.um-scrollbar-y') ||
        wrapper.querySelector('.um-scrollbar:not(.um-scrollbar-x)') ||
        wrapper.querySelector('.um-scrollbar');
      var thumbY = trackY
        ? trackY.querySelector('.um-scrollbar-thumb-y') ||
          trackY.querySelector('.um-scrollbar-thumb')
        : null;
      var trackX = wrapper.querySelector('.um-scrollbar-x');
      var thumbX = trackX
        ? trackX.querySelector('.um-scrollbar-thumb-x') ||
          trackX.querySelector('.um-scrollbar-thumb')
        : null;
      syncScrollbar(container, trackY, thumbY, 'y');
      syncScrollbar(container, trackX, thumbX, 'x');
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
