(() => {
  let isInitialized = false;
  const menuGap = 8;
  const viewportGap = 12;
  const openDropdownSelector = '.um-actions.show';

  const measureMenuHeight = (menu) => {
    if (!menu) {
      return 0;
    }

    const previousDisplay = menu.style.display;
    const previousVisibility = menu.style.visibility;

    menu.style.display = 'block';
    menu.style.visibility = 'hidden';
    const height = menu.getBoundingClientRect().height;
    menu.style.display = previousDisplay;
    menu.style.visibility = previousVisibility;

    return height;
  };

  const getMenu = (dropdownElement) =>
    dropdownElement?.querySelector('.um-actions-menu');

  const getOpenDropdowns = () =>
    document.querySelectorAll(openDropdownSelector);

  const resetMenuStyles = (dropdownElement) => {
    const menu = getMenu(dropdownElement);
    if (!menu) {
      return;
    }

    dropdownElement.classList.remove('dropup');
    menu.style.top = '';
    menu.style.bottom = '';
    menu.style.left = '';
    menu.style.right = '';
    menu.style.maxHeight = '';
    menu.style.overflowY = '';
  };

  const updateDropdownDirection = (dropdownElement) => {
    if (!dropdownElement) {
      return;
    }

    const menu = getMenu(dropdownElement);
    if (!menu) {
      return;
    }

    resetMenuStyles(dropdownElement);

    const scrollContainer = dropdownElement.closest('.um-table-scroll');
    const menuHeight = measureMenuHeight(menu);
    if (!scrollContainer) {
      return;
    }

    const row = dropdownElement.closest('tr');
    if (!row) {
      return;
    }

    const rowBottomInView =
      row.offsetTop - scrollContainer.scrollTop + row.offsetHeight;
    const rowTopInView = row.offsetTop - scrollContainer.scrollTop;
    const spaceBelow = scrollContainer.clientHeight - rowBottomInView - viewportGap;
    const spaceAbove = rowTopInView - viewportGap;

    if (menuHeight > spaceBelow && spaceAbove > spaceBelow) {
      dropdownElement.classList.add('dropup');
      menu.style.top = 'auto';
      menu.style.bottom = `calc(100% + ${menuGap}px)`;
      menu.style.left = 'auto';
      menu.style.right = '0';

      if (menuHeight > spaceAbove) {
        menu.style.maxHeight = `${Math.max(spaceAbove - menuGap, 120)}px`;
        menu.style.overflowY = 'auto';
      }
      return;
    }

    menu.style.top = `calc(100% + ${menuGap}px)`;
    menu.style.bottom = 'auto';
    menu.style.left = 'auto';
    menu.style.right = '0';

    if (menuHeight > spaceBelow) {
      menu.style.maxHeight = `${Math.max(spaceBelow - menuGap, 120)}px`;
      menu.style.overflowY = 'auto';
    }
  };

  const hideDropdown = (dropdownElement) => {
    if (!dropdownElement) {
      return;
    }

    const trigger = dropdownElement.querySelector('.um-actions-trigger');
    resetMenuStyles(dropdownElement);

    if (!trigger || !dropdownElement.classList.contains('show')) {
      return;
    }

    $(trigger).dropdown('hide');
  };

  const hideOtherDropdowns = (currentDropdownElement) => {
    getOpenDropdowns().forEach((dropdownElement) => {
      if (dropdownElement === currentDropdownElement) {
        return;
      }

      hideDropdown(dropdownElement);
    });
  };

  const hideOpenDropdowns = () => {
    getOpenDropdowns().forEach((dropdownElement) => {
      hideDropdown(dropdownElement);
    });
  };

  const initActionsMenus = () => {
    if (isInitialized) {
      return;
    }
    isInitialized = true;

    $(document).on('click', '.um-actions-trigger', function () {
      updateDropdownDirection(this.closest('.um-actions'));
    });

    $(document).on('show.bs.dropdown', '.um-actions', function () {
      hideOtherDropdowns(this);
      updateDropdownDirection(this);
    });

    $(document).on('hidden.bs.dropdown', '.um-actions', function () {
      resetMenuStyles(this);
    });

    window.addEventListener('resize', hideOpenDropdowns);
    window.addEventListener('scroll', hideOpenDropdowns, true);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initActionsMenus);
    window.addEventListener('load', initActionsMenus);
  } else {
    initActionsMenus();
  }
})();
