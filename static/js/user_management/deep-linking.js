(function () {
  const DEFAULT_MODAL_TITLE = 'Generated QR Code';
  const DEFAULT_COPY_LABEL = 'Copy';
  const DEFAULT_COPIED_LABEL = 'Copied';
  const DEFAULT_ERROR_MESSAGE = 'Could not generate the deep link. Please try again.';

  const getCsrfToken = () =>
    document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

  const downloadDataUrl = (href, filename) => {
    const link = document.createElement('a');
    link.href = href;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const svgDataUrlToPngDataUrl = (svgDataUrl) =>
    new Promise((resolve, reject) => {
      if (!svgDataUrl) {
        reject(new Error('QR image is not available.'));
        return;
      }

      const image = new Image();
      image.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = image.width;
        canvas.height = image.height;
        const context = canvas.getContext('2d');

        if (!context) {
          reject(new Error('Could not render QR code image.'));
          return;
        }

        context.drawImage(image, 0, 0);
        resolve(canvas.toDataURL('image/png'));
      };
      image.onerror = () => {
        reject(new Error('Could not render QR code image.'));
      };
      image.src = svgDataUrl;
    });

  const copyText = async (text) => {
    if (!text || !navigator.clipboard?.writeText) {
      return false;
    }

    await navigator.clipboard.writeText(text);
    return true;
  };

  const createQrCodeModalController = (modal) => {
    if (!modal) {
      return null;
    }

    const qrImage = modal.querySelector('[data-workcode-link-qr]');
    const linkOutput = modal.querySelector('[data-workcode-link-output]');
    const copyButton = modal.querySelector('[data-copy-workcode-link]');
    const downloadSvgButton = modal.querySelector('[data-download-workcode-link-svg]');
    const downloadPngButton = modal.querySelector('[data-download-workcode-link-png]');
    const loadingState = modal.querySelector('[data-workcode-link-loading]');
    const successState = modal.querySelector('[data-workcode-link-success]');
    const errorState = modal.querySelector('[data-workcode-link-error]');
    const errorText = modal.querySelector('[data-workcode-link-error-text]');
    const modalTitle = modal.querySelector('[data-qr-code-modal-title]');

    const getTitle = () => modalTitle?.dataset.defaultTitle || DEFAULT_MODAL_TITLE;
    const getLinkValue = () => linkOutput?.value || '';
    const getQrImageUrl = () => qrImage?.src || '';

    const setState = (state) => {
      if (loadingState) {
        loadingState.classList.toggle('d-none', state !== 'loading');
      }
      if (successState) {
        successState.classList.toggle('d-none', state !== 'success');
      }
      if (errorState) {
        errorState.classList.toggle('d-none', state !== 'error');
      }
    };

    const setTitle = (title) => {
      if (modalTitle) {
        modalTitle.textContent = title || getTitle();
      }
    };

    const resetContent = () => {
      if (linkOutput) {
        linkOutput.value = '';
      }
      if (qrImage) {
        qrImage.src = '';
      }
      if (errorText) {
        errorText.textContent = '';
      }
    };

    const showLoading = (title) => {
      setTitle(title);
      resetContent();
      setState('loading');
      $(modal).modal('show');
    };

    const showSuccess = ({ title, url, qrCodeUrl }) => {
      setTitle(title);
      if (linkOutput) {
        linkOutput.value = url || '';
      }
      if (qrImage) {
        qrImage.src = qrCodeUrl || '';
      }
      setState('success');
    };

    const showError = ({ title, message }) => {
      setTitle(title);
      if (errorText) {
        errorText.textContent = message || DEFAULT_ERROR_MESSAGE;
      }
      setState('error');
    };

    const bindCopyAction = () => {
      if (!copyButton || !linkOutput || copyButton.dataset.bound) {
        return;
      }

      copyButton.dataset.bound = 'true';
      copyButton.addEventListener('click', async () => {
        const copied = await copyText(getLinkValue());
        if (!copied) {
          return;
        }

        copyButton.textContent = DEFAULT_COPIED_LABEL;
        window.setTimeout(() => {
          copyButton.textContent = DEFAULT_COPY_LABEL;
        }, 1200);
      });
    };

    const bindDownloadAction = ({ button, format, getFilename }) => {
      if (!button || button.dataset.bound) {
        return;
      }

      button.dataset.bound = 'true';
      button.addEventListener('click', async () => {
        const qrImageUrl = getQrImageUrl();
        if (!qrImageUrl) {
          return;
        }

        try {
          const downloadUrl =
            format === 'png'
              ? await svgDataUrlToPngDataUrl(qrImageUrl)
              : qrImageUrl;

          downloadDataUrl(downloadUrl, getFilename(format));
        } catch (error) {
          alert(error.message || 'Could not download the QR code.');
        }
      });
    };

    bindCopyAction();
    bindDownloadAction({
      button: downloadSvgButton,
      format: 'svg',
      getFilename: (extension) => `work-code-qr.${extension}`,
    });
    bindDownloadAction({
      button: downloadPngButton,
      format: 'png',
      getFilename: (extension) => `work-code-qr.${extension}`,
    });

    return {
      showLoading,
      showSuccess,
      showError,
    };
  };

  const generateQrCode = async ({
    buttonElement,
    modalController,
    title,
    requestUrl,
    requestBody,
    errorMessage = DEFAULT_ERROR_MESSAGE,
    mapSuccessData,
  }) => {
    if (!buttonElement || !modalController) {
      return;
    }

    const $button = $(buttonElement);
    $button.prop('disabled', true);
    modalController.showLoading(title);

    try {
      const response = await fetch(requestUrl, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCsrfToken(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      const data = await response.json();

      if (!response.ok || !data.ok) {
        throw data;
      }

      const successData = mapSuccessData
        ? mapSuccessData(data)
        : {
            url: data.url || '',
            qrCodeUrl: data.qr_code_url || '',
          };

      modalController.showSuccess({
        title,
        url: successData.url,
        qrCodeUrl: successData.qrCodeUrl,
      });
    } catch (data) {
      modalController.showError({
        title,
        message: data?.error || errorMessage,
      });
    } finally {
      $button.prop('disabled', false);
    }
  };

  function initGenerateWorkCodeLink() {
    const modal = document.getElementById('workcode-link-modal');
    const modalController = createQrCodeModalController(modal);

    if (!modalController) {
      return;
    }

    $(document).on('click', '[data-generate-workcode-link]', async function () {
      await generateQrCode({
        buttonElement: this,
        modalController: modalController,
        title: this.dataset.qrCodeTitle || '',
        requestUrl: '/user-management/deep-links/create/',
        requestBody: {
          work_code_id: $(this).data('workcode-id'),
          type: 'login',
        },
      });
    });
  }

  window.addEventListener('load', function () {
    initGenerateWorkCodeLink();
  });
})();
