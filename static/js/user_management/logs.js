(function () {
  var logsBody = document.querySelector("[data-logs-body]");
  var logsCount = document.querySelector("[data-logs-count]");
  var logsPagination = document.querySelector("[data-logs-pagination]");
  if (!logsBody || !logsPagination) return;

  var ICONS = {
    info: "◆",
    warning: "◆",
    error: "◆",
  };

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function renderRows(rows) {
    if (!rows.length) {
      logsBody.innerHTML =
        '<div class="um-log-row um-log-empty">' +
        '<div class="um-navy" style="grid-column:1/-1;text-align:center;padding:24px;">No activity logs found.</div>' +
        "</div>";
      return;
    }
    logsBody.innerHTML = rows
      .map(function (r) {
        return (
          '<div class="um-log-row">' +
          '<div class="um-log-level">' +
          '<span class="um-log-icon um-log-icon-' +
          r.log_level_key +
          '">' +
          ICONS[r.log_level_key] +
          "</span>" +
          '<span class="um-log-level-text um-log-level-' +
          r.log_level_key +
          '">' +
          escapeHtml(r.log_level) +
          "</span>" +
          "</div>" +
          '<div class="um-log-timestamp">' +
          escapeHtml(r.timestamp) +
          "</div>" +
          '<div class="um-log-message">' +
          escapeHtml(r.message) +
          "</div>" +
          "</div>"
        );
      })
      .join("");
  }

  function renderPagination(page, numPages) {
    var html = "";
    html +=
      '<button class="um-page-btn" data-page-prev' +
      (page <= 1 ? " disabled" : "") +
      ">Previous</button>";

    for (var i = 1; i <= numPages; i++) {
      if (
        i === 1 ||
        i === numPages ||
        (i >= page - 2 && i <= page + 2)
      ) {
        html +=
          '<button class="um-page-btn' +
          (i === page ? " um-page-btn-active" : "") +
          '" data-page="' +
          i +
          '">' +
          i +
          "</button>";
      } else if (i === page - 3 || i === page + 3) {
        html += '<span class="um-page-ellipsis">...</span>';
      }
    }

    html +=
      '<button class="um-page-btn" data-page-next' +
      (page >= numPages ? " disabled" : "") +
      ">Next</button>";

    logsPagination.innerHTML = html;
  }

  function loadPage(page) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "?page=" + page, true);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.onload = function () {
      if (xhr.status === 200) {
        var data = JSON.parse(xhr.responseText);
        if (data.ok) {
          renderRows(data.rows);
          renderPagination(data.page, data.num_pages);
          var startIndex = (data.page - 1) * 10 + 1;
          var endIndex = Math.min(data.page * 10, data.total);
          if (data.total === 0) {
            startIndex = 0;
            endIndex = 0;
          }
          if (logsCount) {
            logsCount.textContent =
              startIndex + "-" + endIndex + " of " + data.total + " row(s) shown.";
          }
        }
      }
    };
    xhr.send();
  }

  logsPagination.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-page], [data-page-prev], [data-page-next]");
    if (!btn || btn.disabled) return;

    if (btn.hasAttribute("data-page")) {
      loadPage(parseInt(btn.getAttribute("data-page"), 10));
    } else if (btn.hasAttribute("data-page-prev")) {
      var activeBtn = logsPagination.querySelector(".um-page-btn-active");
      if (activeBtn) {
        var currentPage = parseInt(activeBtn.getAttribute("data-page"), 10);
        if (currentPage > 1) loadPage(currentPage - 1);
      }
    } else if (btn.hasAttribute("data-page-next")) {
      var activeBtn = logsPagination.querySelector(".um-page-btn-active");
      if (activeBtn) {
        var currentPage = parseInt(activeBtn.getAttribute("data-page"), 10);
        loadPage(currentPage + 1);
      }
    }
  });
})();
