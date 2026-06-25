(() => {
  let isInitialized = false;
  let rafId = null;
  const menuGap = 8;
  const viewportGap = 12;
  const openRootClass = 'is-open';
  const portalStateKey = '__ellipsisPortalState';

  const getOpenRoots = () =>
    document.querySelectorAll(`[data-ellipsis-root].${openRootClass}`);

  const getTrigger = (root) => root?.querySelector('[data-ellipsis-trigger]');

  const getInlineMenu = (root) => root?.querySelector('[data-ellipsis-menu]');

  const getMenu = (root) => root?.[portalStateKey]?.menu || getInlineMenu(root);

  const setExpanded = (root, expanded) => {
    const trigger = getTrigger(root);
    if (trigger) {
      trigger.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    }
  };

  const clearMenuStyles = (menu) => {
    if (!menu) {
      return;
    }

    menu.style.display = '';
    menu.style.position = '';
    menu.style.top = '';
    menu.style.left = '';
    menu.style.right = '';
    menu.style.bottom = '';
    menu.style.maxHeight = '';
    menu.style.overflowY = '';
    menu.style.transform = '';
    menu.style.zIndex = '';
    menu.style.visibility = '';
  };

  const measureMenuRect = (menu) => {
    if (!menu) {
      return { height: 0, width: 0 };
    }

    const previousDisplay = menu.style.display;
    const previousPosition = menu.style.position;
    const previousTop = menu.style.top;
    const previousLeft = menu.style.left;
    const previousVisibility = menu.style.visibility;
    const hadOpenClass = menu.classList.contains(openRootClass);

    if (!hadOpenClass) {
      menu.classList.add(openRootClass);
    }

    menu.style.display = 'block';
    menu.style.position = 'fixed';
    menu.style.top = '0';
    menu.style.left = '0';
    menu.style.visibility = 'hidden';

    const rect = menu.getBoundingClientRect();

    menu.style.display = previousDisplay;
    menu.style.position = previousPosition;
    menu.style.top = previousTop;
    menu.style.left = previousLeft;
    menu.style.visibility = previousVisibility;

    if (!hadOpenClass) {
      menu.classList.remove(openRootClass);
    }

    return {
      height: rect.height,
      width: rect.width,
    };
  };

  const ensurePortaledMenu = (root) => {
    if (!root) {
      return null;
    }

    if (root[portalStateKey]?.menu) {
      return root[portalStateKey].menu;
    }

    const menu = getInlineMenu(root);
    if (!menu) {
      return null;
    }

    const originalParent = menu.parentNode;
    const placeholder = document.createComment('ellipsis-menu-placeholder');
    if (originalParent) {
      originalParent.insertBefore(placeholder, menu);
    }

    document.body.appendChild(menu);
    menu.__ellipsisOwner = root;
    root[portalStateKey] = {
      menu,
      originalParent,
      placeholder,
    };

    return menu;
  };

  const restoreMenu = (root) => {
    if (!root) {
      return;
    }

    const portalState = root[portalStateKey];
    const menu = getMenu(root);

    root.classList.remove(openRootClass);
    setExpanded(root, false);

    if (menu) {
      menu.classList.remove(openRootClass);
      clearMenuStyles(menu);
      delete menu.__ellipsisOwner;
    }

    if (!portalState) {
      return;
    }

    if (menu && portalState.originalParent && portalState.placeholder?.parentNode) {
      portalState.originalParent.insertBefore(menu, portalState.placeholder);
    }
    if (portalState.placeholder?.parentNode) {
      portalState.placeholder.parentNode.removeChild(portalState.placeholder);
    }

    delete root[portalStateKey];
  };

  const positionMenu = (root) => {
    if (!root?.classList.contains(openRootClass)) {
      return;
    }

    const menu = ensurePortaledMenu(root);
    const trigger = getTrigger(root);

    if (!menu || !trigger || !document.contains(trigger)) {
      restoreMenu(root);
      return;
    }

    const triggerRect = trigger.getBoundingClientRect();
    const { height: menuHeight, width: menuWidth } = measureMenuRect(menu);
    const spaceBelow = window.innerHeight - triggerRect.bottom - viewportGap;
    const spaceAbove = triggerRect.top - viewportGap;
    const shouldOpenUp = menuHeight > spaceBelow && spaceAbove > spaceBelow;
    const availableHeight = shouldOpenUp ? spaceAbove : spaceBelow;

    root.classList.toggle('dropup', shouldOpenUp);
    setExpanded(root, true);

    menu.classList.add(openRootClass);
    menu.style.display = 'block';
    menu.style.position = 'fixed';
    menu.style.transform = 'none';
    menu.style.zIndex = '1080';

    if (menuHeight > availableHeight) {
      menu.style.maxHeight = `${Math.max(availableHeight - menuGap, 120)}px`;
      menu.style.overflowY = 'auto';
    } else {
      menu.style.maxHeight = '';
      menu.style.overflowY = '';
    }

    const effectiveHeight = menu.style.maxHeight
      ? Math.min(menuHeight, parseFloat(menu.style.maxHeight))
      : menuHeight;

    const top = shouldOpenUp
      ? Math.max(viewportGap, triggerRect.top - effectiveHeight - menuGap)
      : Math.max(
          viewportGap,
          Math.min(
            triggerRect.bottom + menuGap,
            window.innerHeight - effectiveHeight - viewportGap,
          ),
        );

    const alignRight = menu.dataset.ellipsisAlign !== 'left';
    const desiredLeft = alignRight
      ? triggerRect.right - menuWidth
      : triggerRect.left;
    const left = Math.min(
      Math.max(desiredLeft, viewportGap),
      Math.max(viewportGap, window.innerWidth - menuWidth - viewportGap),
    );

    menu.style.top = `${top}px`;
    menu.style.left = `${left}px`;
    menu.style.right = 'auto';
    menu.style.bottom = 'auto';
  };

  const openMenu = (root) => {
    if (!root) {
      return;
    }

    getOpenRoots().forEach((openRoot) => {
      if (openRoot !== root) {
        restoreMenu(openRoot);
      }
    });

    if (!ensurePortaledMenu(root)) {
      return;
    }

    root.classList.add(openRootClass);
    positionMenu(root);
  };

  const toggleMenu = (root) => {
    if (!root) {
      return;
    }

    if (root.classList.contains(openRootClass)) {
      restoreMenu(root);
      return;
    }

    openMenu(root);
  };

  const isInsideOpenMenu = (target) =>
    Array.from(getOpenRoots()).some((root) => {
      const menu = getMenu(root);
      return root.contains(target) || (menu && menu.contains(target));
    });

  const scheduleReposition = () => {
    if (rafId !== null) {
      return;
    }

    rafId = window.requestAnimationFrame(() => {
      rafId = null;
      getOpenRoots().forEach((root) => {
        positionMenu(root);
      });
    });
  };

  const closeAllMenus = () => {
    getOpenRoots().forEach((root) => {
      restoreMenu(root);
    });
  };

  const initActionsMenus = () => {
    if (isInitialized) {
      return;
    }
    isInitialized = true;

    document.addEventListener('click', (event) => {
      const trigger = event.target.closest('[data-ellipsis-trigger]');
      if (trigger) {
        const root = trigger.closest('[data-ellipsis-root]');
        if (!root) {
          return;
        }

        event.preventDefault();
        event.stopPropagation();
        toggleMenu(root);
        return;
      }

      const menuItem = event.target.closest('[data-ellipsis-menu] .dropdown-item');
      if (menuItem) {
        const root = menuItem.closest('[data-ellipsis-menu]')?.__ellipsisOwner;
        if (root) {
          window.setTimeout(() => {
            restoreMenu(root);
          }, 0);
        }
        return;
      }

      if (!isInsideOpenMenu(event.target)) {
        closeAllMenus();
      }
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeAllMenus();
      }
    });

    window.addEventListener('resize', scheduleReposition);
    window.addEventListener('scroll', scheduleReposition, true);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initActionsMenus);
    window.addEventListener('load', initActionsMenus);
  } else {
    initActionsMenus();
  }
})();
