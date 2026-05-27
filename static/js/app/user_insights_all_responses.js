/**
 * User Insights – "All responses" overlay for open-text questions.
 */
(function () {
    var modalEl;
    var tbodyEl;
    var breadcrumbEl;
    var countEl;
    var searchEl;
    var currentRows = [];
    var naLabel = "N/A";
    var countTemplate = "(%(count)s responses submitted)";

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function highlightText(text, query) {
        var safe = escapeHtml(text);
        if (!query) {
            return safe;
        }
        var pattern = new RegExp("(" + query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
        return safe.replace(pattern, '<mark class="user-insights-search-hit">$1</mark>');
    }

    function renderBreadcrumb(crumbs) {
        if (!breadcrumbEl) {
            return;
        }
        breadcrumbEl.innerHTML = "";
        crumbs.forEach(function (crumb, idx) {
            var span = document.createElement("span");
            span.className = "user-insights-all-responses-breadcrumb-item";
            span.textContent = crumb;
            breadcrumbEl.appendChild(span);
            if (idx < crumbs.length - 1) {
                var sep = document.createElement("span");
                sep.className = "user-insights-all-responses-breadcrumb-sep";
                sep.setAttribute("aria-hidden", "true");
                sep.textContent = ">";
                breadcrumbEl.appendChild(sep);
            }
        });
    }

    function rowMatchesQuery(row, query) {
        if (!query) {
            return true;
        }
        var haystack = [
            row.date,
            row.label,
            row.id,
            row.native,
            row.translation || "",
        ]
            .join(" ")
            .toLowerCase();
        return haystack.indexOf(query.toLowerCase()) !== -1;
    }

    function renderTable(rows, query) {
        if (!tbodyEl) {
            return;
        }
        tbodyEl.innerHTML = "";
        var visible = rows.filter(function (row) {
            return rowMatchesQuery(row, query);
        });
        visible.forEach(function (row) {
            var tr = document.createElement("tr");
            var translation = row.translation;
            var translationHtml;
            if (!translation) {
                translationHtml = '<span class="user-insights-all-responses-na">' + escapeHtml(naLabel) + "</span>";
            } else {
                translationHtml = highlightText(translation, query);
            }
            tr.innerHTML =
                "<td>" +
                escapeHtml(row.date) +
                "</td>" +
                "<td class=\"user-insights-all-responses-id\">" +
                escapeHtml(row.label) +
                "</td>" +
                "<td>" +
                escapeHtml(row.native) +
                "</td>" +
                "<td class=\"user-insights-all-responses-translation\">" +
                translationHtml +
                "</td>";
            tbodyEl.appendChild(tr);
        });
    }

    function updateCount(total) {
        if (!countEl) {
            return;
        }
        countEl.textContent = countTemplate.replace("%(count)s", String(total));
    }

    function getActiveTextPanelLead(panelEl) {
        var activePanel = panelEl.querySelector(".user-insights-text-responses-panel.is-active");
        if (!activePanel) {
            return null;
        }
        var leadId = activePanel.getAttribute("data-text-panel-for");
        var script = panelEl.previousElementSibling;
        while (script && !(script.tagName === "SCRIPT" && script.type === "application/json")) {
            script = script.previousElementSibling;
        }
        if (!script) {
            return null;
        }
        try {
            var detail = JSON.parse(script.textContent);
            if (!detail.lead_questions) {
                return null;
            }
            for (var i = 0; i < detail.lead_questions.length; i++) {
                var lead = detail.lead_questions[i];
                if (lead.id === leadId && lead.text_detail) {
                    return lead.text_detail;
                }
            }
        } catch (e) {
            return null;
        }
        return null;
    }

    function openModal(allResponses) {
        if (!modalEl || !allResponses) {
            return;
        }
        currentRows = allResponses.rows || [];
        renderBreadcrumb(allResponses.breadcrumb || []);
        updateCount(allResponses.total_count || currentRows.length);
        var defaultSearch = allResponses.default_search || "";
        if (searchEl) {
            searchEl.value = defaultSearch;
        }
        renderTable(currentRows, defaultSearch);
        if (typeof bootstrap !== "undefined" && bootstrap.Modal) {
            bootstrap.Modal.getOrCreateInstance(modalEl).show();
        } else {
            modalEl.classList.add("show");
            modalEl.style.display = "block";
        }
    }

    function bindExploreButtons() {
        document.addEventListener("click", function (e) {
            var btn = e.target.closest(".user-insights-explore-all-btn");
            if (!btn || btn.disabled) {
                return;
            }
            var panel = btn.closest(".user-insights-indicator-panel");
            if (!panel) {
                return;
            }
            var textDetail = getActiveTextPanelLead(panel);
            if (!textDetail || !textDetail.all_responses) {
                return;
            }
            openModal(textDetail.all_responses);
        });
    }

    function bindSearch() {
        if (!searchEl) {
            return;
        }
        searchEl.addEventListener("input", function () {
            renderTable(currentRows, searchEl.value.trim());
        });
    }

    function readConfig() {
        var configEl = document.getElementById("user-insights-all-responses-config");
        if (!configEl) {
            return;
        }
        try {
            var config = JSON.parse(configEl.textContent);
            naLabel = config.na_label || naLabel;
            countTemplate = config.count_template || countTemplate;
        } catch (e) {
            /* use defaults */
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        modalEl = document.getElementById("user-insights-all-responses-modal");
        tbodyEl = document.getElementById("user-insights-all-responses-tbody");
        breadcrumbEl = document.getElementById("user-insights-all-responses-breadcrumb");
        countEl = document.getElementById("user-insights-all-responses-count");
        searchEl = document.getElementById("user-insights-all-responses-search");
        readConfig();
        bindExploreButtons();
        bindSearch();
    });
})();
