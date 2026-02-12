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

  window.addEventListener('load', initScrollbars);
  window.addEventListener('resize', syncAllThumbs);
})();
