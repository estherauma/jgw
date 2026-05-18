(() => {
  const createPreviewItem = ({ src, alt, removable = false, onRemove }) => {
    const item = document.createElement('div');
    item.className = 'um-image-picker-card';

    const image = document.createElement('img');
    image.className = 'um-image-picker-thumb';
    image.src = (src || '').trim();
    image.alt = alt;
    image.referrerPolicy = 'no-referrer';
    image.style.display = 'block';
    item.appendChild(image);

    if (removable) {
      const removeButton = document.createElement('button');
      removeButton.type = 'button';
      removeButton.className = 'um-image-picker-remove';
      removeButton.textContent = 'Remove';
      removeButton.addEventListener('click', onRemove);
      item.appendChild(removeButton);
    }

    return item;
  };

  const updateEmptyState = (root) => {
    const preview = root.querySelector('[data-image-picker-preview]');
    const empty = root.querySelector('[data-image-picker-empty]');
    if (!preview || !empty) {
      return;
    }
    empty.classList.toggle('d-none', preview.childElementCount > 0);
  };

  const renderCurrentPreview = (root) => {
    const preview = root.querySelector('[data-image-picker-preview]');
    const currentUrl = root.getAttribute('data-image-picker-current-url') || '';
    const currentLabel =
      root.getAttribute('data-image-picker-current-label') || 'Current image';

    if (!preview) {
      return;
    }

    preview.innerHTML = '';
    if (currentUrl) {
      preview.appendChild(
        createPreviewItem({
          src: currentUrl,
          alt: currentLabel,
        }),
      );
    }

    updateEmptyState(root);
  };

  const updateMeta = (root, files) => {
    const meta = root.querySelector('[data-image-picker-meta]');
    const defaultText =
      root.getAttribute('data-image-picker-default-meta') || 'PNG, JPG, WEBP';

    if (!meta) {
      return;
    }

    if (!files.length) {
      meta.textContent = defaultText;
      return;
    }

    if (files.length === 1) {
      meta.textContent = files[0]?.name || defaultText;
      return;
    }

    meta.textContent = `${files.length} files selected`;
  };

  const renderSelectedFiles = (root) => {
    const input = root.querySelector('[data-image-picker-input]');
    const preview = root.querySelector('[data-image-picker-preview]');

    if (!input || !preview) {
      return;
    }

    const files = Array.from(input.files || []);
    preview.innerHTML = '';

    if (!files.length) {
      renderCurrentPreview(root);
      updateMeta(root, files);
      return;
    }

    files.forEach((file) => {
      const src = URL.createObjectURL(file);
      preview.appendChild(
        createPreviewItem({
          src,
          alt: file.name,
          removable: true,
          onRemove: () => {
            input.value = '';
            renderSelectedFiles(root);
          },
        }),
      );
    });

    updateMeta(root, files);
    updateEmptyState(root);
  };

  const initImagePicker = (root) => {
    if (!root || root.getAttribute('data-image-picker-ready') === 'true') {
      if (root) {
        renderCurrentPreview(root);
      }
      return;
    }

    const input = root.querySelector('[data-image-picker-input]');
    const trigger = root.querySelector('[data-image-picker-trigger]');
    const meta = root.querySelector('[data-image-picker-meta]');

    if (!input || !trigger) {
      return;
    }

    if (meta) {
      root.setAttribute(
        'data-image-picker-default-meta',
        meta.textContent.trim() || 'PNG, JPG, WEBP',
      );
    }

    root.setAttribute('data-image-picker-ready', 'true');

    trigger.addEventListener('click', () => {
      input.click();
    });

    input.addEventListener('change', () => {
      renderSelectedFiles(root);
    });

    renderCurrentPreview(root);
    updateMeta(root, []);
  };

  const initImagePickers = (scope = document) => {
    scope.querySelectorAll('[data-image-picker]').forEach((root) => {
      initImagePicker(root);
    });
  };

  const refreshImagePicker = (root, currentUrl = '') => {
    if (!root) {
      return;
    }

    const normalizedUrl = (currentUrl || '').trim();
    root.setAttribute('data-image-picker-current-url', normalizedUrl);
    const input = root.querySelector('[data-image-picker-input]');
    if (input) {
      input.value = '';
    }
    renderCurrentPreview(root);
    updateMeta(root, []);
    window.requestAnimationFrame(() => {
      renderCurrentPreview(root);
      updateMeta(root, []);
    });
  };

  window.initUmImagePickers = initImagePickers;
  window.refreshUmImagePicker = refreshImagePicker;
})();
