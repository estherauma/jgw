(() => {
  const triggerFieldChange = (field) => {
    field.dispatchEvent(new Event('change', { bubbles: true }));
  };

  const getSelectedOptions = (field) =>
    Array.from(field.options).filter(
      (option) => option.selected && option.value !== '',
    );

  const updateLabel = (root) => {
    const field = root.querySelector('select');
    const label = root.querySelector('[data-um-select-label]');
    const placeholder =
      root.getAttribute('data-um-select-placeholder') || 'Select an option';
    const isMultiple = root.getAttribute('data-um-select-multiple') === 'true';

    if (!field || !label) {
      return;
    }

    const selectedOptions = getSelectedOptions(field);
    if (!selectedOptions.length) {
      label.textContent = placeholder;
      root.classList.add('is-placeholder');
      return;
    }

    root.classList.remove('is-placeholder');

    if (!isMultiple || selectedOptions.length === 1) {
      label.textContent = selectedOptions[0]?.text || placeholder;
      return;
    }

    label.textContent = `${selectedOptions.length} selected`;
  };

  const syncOptionStates = (root) => {
    const field = root.querySelector('select');
    if (!field) {
      return;
    }

    root.querySelectorAll('[data-um-select-option]').forEach((item) => {
      const optionValue = item.getAttribute('data-um-select-value');
      const option = Array.from(field.options).find(
        (candidate) => candidate.value === optionValue,
      );
      const isSelected = !!option?.selected;

      item.classList.toggle('is-selected', isSelected);
      const checkbox = item.querySelector('[data-um-select-checkbox]');
      if (checkbox) {
        checkbox.checked = isSelected;
      }
    });

    updateLabel(root);
  };

  const filterOptions = (root) => {
    const input = root.querySelector('[data-um-select-filter]');
    const empty = root.querySelector('[data-um-select-empty]');
    const query = (input?.value || '').toLowerCase().trim();
    let visibleCount = 0;

    root.querySelectorAll('[data-um-select-option]').forEach((item) => {
      if (item.getAttribute('data-um-select-placeholder-option') === 'true') {
        item.hidden = true;
        return;
      }

      const text = item.getAttribute('data-um-select-search-text') || '';
      const matches = !query || text.includes(query);
      item.hidden = !matches;
      if (matches) {
        visibleCount += 1;
      }
    });

    empty?.classList.toggle('d-none', visibleCount > 0);
  };

  const closeSelect = (root) => {
    const menu = root.querySelector('[data-um-select-menu]');
    const input = root.querySelector('[data-um-select-filter]');

    root.classList.remove('is-open');
    menu?.classList.remove('is-open');

    if (input) {
      input.value = '';
    }

    filterOptions(root);
  };

  const buildOptions = (root) => {
    const field = root.querySelector('select');
    const optionsContainer = root.querySelector('[data-um-select-options]');
    const isMultiple = root.getAttribute('data-um-select-multiple') === 'true';

    if (!field || !optionsContainer) {
      return;
    }

    optionsContainer.innerHTML = '';

    Array.from(field.options).forEach((option, index) => {
      const item = document.createElement(isMultiple ? 'div' : 'button');
      item.className = 'um-select-option';
      item.setAttribute('data-um-select-option', '');
      item.setAttribute('data-um-select-value', option.value);
      item.setAttribute('data-um-select-search-text', option.text.toLowerCase());
      if (!isMultiple && option.value === '') {
        item.setAttribute('data-um-select-placeholder-option', 'true');
      }

      if (isMultiple) {
        item.classList.add('um-select-option-check');

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = option.value;
        checkbox.id = `${field.id}-option-${index}`;
        checkbox.setAttribute('data-um-select-checkbox', '');
        checkbox.checked = option.selected;
        checkbox.addEventListener('click', (event) => {
          event.stopPropagation();
        });
        checkbox.addEventListener('change', () => {
          option.selected = checkbox.checked;
          syncOptionStates(root);
          triggerFieldChange(field);
        });
        item.addEventListener('click', (event) => {
          event.stopPropagation();

          if (event.target === checkbox) {
            return;
          }

          event.preventDefault();
          checkbox.checked = !checkbox.checked;
          option.selected = checkbox.checked;
          syncOptionStates(root);
          triggerFieldChange(field);
        });

        item.appendChild(checkbox);
      } else {
        item.type = 'button';
        item.addEventListener('click', () => {
          Array.from(field.options).forEach((candidate) => {
            candidate.selected = candidate.value === option.value;
          });
          syncOptionStates(root);
          triggerFieldChange(field);
          closeSelect(root);
        });
      }

      const text = document.createElement('span');
      text.textContent = option.text;
      item.appendChild(text);
      item.hidden = !isMultiple && option.value === '';
      optionsContainer.appendChild(item);
    });
  };

  const initCustomSelect = (root) => {
    if (!root) {
      return;
    }

    if (root.getAttribute('data-um-select-ready') === 'true') {
      syncOptionStates(root);
      return;
    }

    const toggle = root.querySelector('[data-um-select-toggle]');
    const menu = root.querySelector('[data-um-select-menu]');
    const input = root.querySelector('[data-um-select-filter]');

    if (!toggle || !menu) {
      return;
    }

    root.setAttribute('data-um-select-ready', 'true');
    buildOptions(root);
    syncOptionStates(root);
    filterOptions(root);

    toggle.addEventListener('click', () => {
      const isOpen = !root.classList.contains('is-open');
      root.classList.toggle('is-open', isOpen);
      menu.classList.toggle('is-open', isOpen);

      if (isOpen) {
        input?.focus();
        input?.select();
      }
    });

    input?.addEventListener('input', () => {
      filterOptions(root);
    });

    document.addEventListener('click', (event) => {
      if (!root.contains(event.target)) {
        closeSelect(root);
      }
    });
  };

  const initCustomSelects = (scope = document) => {
    scope.querySelectorAll('[data-um-select]').forEach((root) => {
      initCustomSelect(root);
    });
  };

  const rebuildCustomSelect = (root) => {
    if (!root) {
      return;
    }

    buildOptions(root);
    syncOptionStates(root);
    filterOptions(root);
  };

  window.initUmSelect = initCustomSelect;
  window.initUmSelects = initCustomSelects;
  window.refreshUmSelect = syncOptionStates;
  window.rebuildUmSelect = rebuildCustomSelect;
})();
