(function () {
  function isDocsPath(pathname) {
    return typeof pathname === 'string' && pathname.indexOf('/docs/') === 0;
  }

  function canInterceptLink(anchor) {
    return (
      anchor &&
      !anchor.target &&
      !anchor.hasAttribute('download') &&
      anchor.origin === window.location.origin &&
      isDocsPath(anchor.pathname)
    );
  }

  function parseDocsPage(htmlText) {
    var parser = new DOMParser();
    var nextDocument = parser.parseFromString(htmlText, 'text/html');

    return {
      title: nextDocument.title,
      article: nextDocument.querySelector('[data-docs-article]'),
    };
  }

  document.addEventListener('DOMContentLoaded', function () {
    var shell = document.querySelector('[data-docs-shell]');
    var article = document.querySelector('[data-docs-article]');

    if (!shell || !article) {
      return;
    }

    function setActiveLink(url) {
      var normalizedUrl = new URL(url, window.location.origin).pathname;

      document.querySelectorAll('[data-docs-nav-link]').forEach(function (link) {
        var linkPath = new URL(link.href, window.location.origin).pathname;
        link.classList.toggle('active', linkPath === normalizedUrl);
      });
    }

    function loadPage(url, pushState) {
      window
        .fetch(url, {
          credentials: 'same-origin',
        })
        .then(function (response) {
          if (!response.ok) {
            throw new Error('Failed to load docs page.');
          }
          return response.text();
        })
        .then(function (htmlText) {
          var parsedPage = parseDocsPage(htmlText);

          if (!parsedPage.article) {
            window.location.assign(url);
            return;
          }

          article.innerHTML = parsedPage.article.innerHTML;
          document.title = parsedPage.title || document.title;
          setActiveLink(url);

          if (pushState) {
            window.history.pushState({ url: url }, '', url);
          }

          window.scrollTo({ top: 0, behavior: 'auto' });
        })
        .catch(function () {
          window.location.assign(url);
        });
    }

    function handleNavigation(url, pushState) {
      if (url === window.location.href && pushState) {
        return;
      }

      loadPage(url, pushState);
    }

    document.addEventListener('click', function (event) {
      var anchor = event.target.closest('a');

      if (!anchor || !shell.contains(anchor)) {
        return;
      }

      if (
        event.defaultPrevented ||
        event.button !== 0 ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey ||
        event.altKey ||
        !canInterceptLink(anchor)
      ) {
        return;
      }

      event.preventDefault();
      handleNavigation(anchor.href, true);
    });

    window.addEventListener('popstate', function () {
      if (!isDocsPath(window.location.pathname)) {
        window.location.reload();
        return;
      }

      loadPage(window.location.href, false);
    });
  });
})();
