/**
 * User Insights – nested question drill-down (choice path + open-text responses).
 * Right panel (sunburst or text responses) shows only for the expanded lead question.
 */
(function () {
    function getDrilldownFromPanel(panelEl) {
        var prev = panelEl.previousElementSibling;
        while (prev) {
            if (prev.tagName === "SCRIPT" && prev.type === "application/json") {
                try {
                    return JSON.parse(prev.textContent);
                } catch (e) {
                    return null;
                }
            }
            prev = prev.previousElementSibling;
        }
        return null;
    }

    function getLeadById(detail, leadId) {
        if (!detail || !detail.lead_questions) {
            return null;
        }
        for (var i = 0; i < detail.lead_questions.length; i++) {
            if (detail.lead_questions[i].id === leadId) {
                return detail.lead_questions[i];
            }
        }
        return null;
    }

    function getDrilldownDetailEl(panelEl) {
        return panelEl.querySelector("[data-drilldown-detail]");
    }

    function getDrilldownEmptyEl(panelEl) {
        return panelEl.querySelector("[data-drilldown-empty]");
    }

    function updateBreadcrumb(panelEl, crumbs) {
        var el = panelEl.querySelector("[data-breadcrumb-root]");
        if (!el) {
            return;
        }
        el.innerHTML = "";
        if (!crumbs || !crumbs.length) {
            return;
        }
        crumbs.forEach(function (crumb, idx) {
            var span = document.createElement("span");
            span.className = "user-insights-breadcrumb-item";
            span.textContent = crumb;
            el.appendChild(span);
            if (idx < crumbs.length - 1) {
                var sep = document.createElement("span");
                sep.className = "user-insights-breadcrumb-sep";
                sep.setAttribute("aria-hidden", "true");
                sep.textContent = ">";
                el.appendChild(sep);
            }
        });
        var trail = document.createElement("span");
        trail.className = "user-insights-breadcrumb-trail";
        trail.setAttribute("aria-hidden", "true");
        trail.textContent = ">";
        el.appendChild(trail);
    }

    function showDrilldownDetail(panelEl, show) {
        var detailWrap = getDrilldownDetailEl(panelEl);
        var emptyEl = getDrilldownEmptyEl(panelEl);
        if (detailWrap) {
            detailWrap.classList.toggle("d-none", !show);
        }
        if (emptyEl) {
            emptyEl.classList.toggle("d-none", show);
        }
    }

    function showSideView(panelEl, viewName) {
        panelEl.querySelectorAll(".user-insights-side-view").forEach(function (view) {
            var show = view.getAttribute("data-side-view") === viewName;
            view.classList.toggle("d-none", !show);
        });
    }

    function hideAllSideViews(panelEl) {
        panelEl.querySelectorAll(".user-insights-side-view").forEach(function (view) {
            view.classList.add("d-none");
        });
    }

    function showTextPanel(panelEl, leadId) {
        panelEl.querySelectorAll(".user-insights-text-responses-panel").forEach(function (textPanel) {
            textPanel.classList.toggle("is-active", textPanel.getAttribute("data-text-panel-for") === leadId);
        });
    }

    function setActiveLeadCard(panelEl, leadId) {
        panelEl.querySelectorAll(".user-insights-lead-card").forEach(function (card) {
            var isActive = leadId && card.getAttribute("data-lead-id") === leadId;
            card.classList.toggle("is-active", isActive);
        });
    }

    function collapseOtherLeadBodies(panelEl, exceptLeadId) {
        panelEl.querySelectorAll(".user-insights-lead-body.show").forEach(function (body) {
            var card = body.closest(".user-insights-lead-card");
            if (!card || card.getAttribute("data-lead-id") === exceptLeadId) {
                return;
            }
            if (typeof bootstrap !== "undefined" && bootstrap.Collapse) {
                bootstrap.Collapse.getOrCreateInstance(body).hide();
            } else {
                body.classList.remove("show");
            }
        });
    }

    function getExpandedLeadId(panelEl) {
        var openBody = panelEl.querySelector(".user-insights-lead-body.show");
        if (!openBody) {
            return null;
        }
        var card = openBody.closest(".user-insights-lead-card");
        return card ? card.getAttribute("data-lead-id") : null;
    }

    function getLeadQuestionCode(panelEl, leadId, detail) {
        var leadRoot = panelEl.querySelector('.user-insights-lead-card[data-lead-id="' + leadId + '"]');
        if (leadRoot) {
            var fromData = leadRoot.getAttribute("data-lead-code");
            if (fromData) {
                return fromData;
            }
            var codeEl = leadRoot.querySelector(".user-insights-lead-code");
            if (codeEl && codeEl.textContent.trim()) {
                return codeEl.textContent.trim();
            }
        }
        var lead = getLeadById(detail, leadId);
        if (lead && lead.code) {
            return lead.code;
        }
        if (lead && lead.number != null) {
            var padded = String(lead.number);
            if (padded.length < 2) {
                padded = "0" + padded;
            }
            return "Q" + padded;
        }
        return "";
    }

    function buildChoiceBreadcrumb(panelEl, leadId) {
        var detail = getDrilldownFromPanel(panelEl);
        var crumbs = [];
        var leadRoot = panelEl.querySelector('.user-insights-lead-card[data-lead-id="' + leadId + '"]');
        if (!leadRoot) {
            return crumbs;
        }
        var leadCode = getLeadQuestionCode(panelEl, leadId, detail);
        if (leadCode) {
            crumbs.push(leadCode);
        }
        leadRoot.querySelectorAll(".user-insights-answer-bar.is-selected").forEach(function (bar) {
            crumbs.push(bar.getAttribute("data-response-label"));
        });
        leadRoot.querySelectorAll(".user-insights-option-row.is-selected").forEach(function (row) {
            crumbs.push(row.getAttribute("data-option-label"));
        });
        return crumbs;
    }

    function getSunburstHighlight(panelEl, detail, leadId) {
        var crumbs = buildChoiceBreadcrumb(panelEl, leadId);
        if (crumbs.length) {
            return crumbs[crumbs.length - 1];
        }
        return detail.sunburst_highlight || "";
    }

    function clearDrilldownDetail(panelEl) {
        panelEl.removeAttribute("data-active-lead-id");
        setActiveLeadCard(panelEl, null);
        hideAllSideViews(panelEl);
        showDrilldownDetail(panelEl, false);
        updateBreadcrumb(panelEl, []);
    }

    function activateOpenTextQuestion(panelEl, detail, lead) {
        panelEl.setAttribute("data-active-lead-id", lead.id);
        setActiveLeadCard(panelEl, lead.id);
        showDrilldownDetail(panelEl, true);
        showSideView(panelEl, "text");
        showTextPanel(panelEl, lead.id);
        if (lead.text_detail && lead.text_detail.breadcrumb) {
            updateBreadcrumb(panelEl, lead.text_detail.breadcrumb);
        }
    }

    function isIndicatorPanelVisible(panelEl) {
        var indicatorCollapse = panelEl.closest(".user-insights-indicator-detail");
        return !indicatorCollapse || indicatorCollapse.classList.contains("show");
    }

    function refreshSunburstChart(panelEl) {
        var detail = getDrilldownFromPanel(panelEl);
        var leadId = panelEl.getAttribute("data-active-lead-id") || getExpandedLeadId(panelEl);
        var lead = getLeadById(detail, leadId);
        if (
            !detail ||
            !lead ||
            (lead.response_type || "choice") !== "choice" ||
            typeof initUserInsightsSunburst !== "function"
        ) {
            return;
        }
        var sunburstData =
            lead.sunburst && lead.sunburst.length ? lead.sunburst : detail.sunburst;
        if (!sunburstData || !sunburstData.length) {
            return;
        }
        var containerId = detail.panel_dom_id + "-sunburst";
        initUserInsightsSunburst(
            containerId,
            sunburstData,
            getSunburstHighlight(panelEl, detail, lead.id)
        );
        if (typeof resizeUserInsightsSunburst === "function") {
            resizeUserInsightsSunburst(containerId);
        }
    }

    function ensureDefaultOptionSelection(container) {
        if (!container) {
            return;
        }
        container.querySelectorAll(".user-insights-option-list").forEach(function (list) {
            if (list.querySelector(".user-insights-option-row.is-selected")) {
                return;
            }
            var wraps = list.querySelectorAll(":scope > .user-insights-option-wrap");
            var targetWrap = null;
            wraps.forEach(function (wrap) {
                if (targetWrap) {
                    return;
                }
                if (wrap.querySelector(".user-insights-follow-up-branch")) {
                    targetWrap = wrap;
                }
            });
            if (!targetWrap && wraps.length) {
                targetWrap = wraps[0];
            }
            if (!targetWrap) {
                return;
            }
            var row = targetWrap.querySelector(".user-insights-option-row");
            if (row) {
                row.classList.add("is-selected");
            }
            var branch = targetWrap.querySelector(".user-insights-follow-up-branch");
            if (branch) {
                branch.classList.remove("d-none");
                ensureDefaultOptionSelection(branch);
            }
        });
    }

    function ensureDefaultAnswerSelection(panelEl, leadId) {
        var card = panelEl.querySelector('.user-insights-lead-card[data-lead-id="' + leadId + '"]');
        if (!card) {
            return;
        }
        var selectedBar = card.querySelector(".user-insights-answer-bar.is-selected");
        if (selectedBar) {
            var selectedId = selectedBar.getAttribute("data-response-id");
            card.querySelectorAll(".user-insights-lead-follow-up-root").forEach(function (root) {
                root.classList.toggle("d-none", root.getAttribute("data-follow-up-for") !== selectedId);
            });
            ensureDefaultOptionSelection(
                card.querySelector(".user-insights-lead-follow-up-root:not(.d-none)")
            );
            return;
        }
        var bars = card.querySelectorAll(".user-insights-answer-bar");
        var targetBar = null;
        bars.forEach(function (bar) {
            if (targetBar) {
                return;
            }
            var responseId = bar.getAttribute("data-response-id");
            var root = card.querySelector(
                '.user-insights-lead-follow-up-root[data-follow-up-for="' + responseId + '"]'
            );
            if (root) {
                targetBar = bar;
            }
        });
        if (!targetBar && bars.length) {
            targetBar = bars[0];
        }
        if (!targetBar) {
            return;
        }
        var responseId = targetBar.getAttribute("data-response-id");
        bars.forEach(function (bar) {
            bar.classList.toggle("is-selected", bar === targetBar);
        });
        card.querySelectorAll(".user-insights-lead-follow-up-root").forEach(function (root) {
            root.classList.toggle("d-none", root.getAttribute("data-follow-up-for") !== responseId);
        });
        ensureDefaultOptionSelection(
            card.querySelector(".user-insights-lead-follow-up-root:not(.d-none)")
        );
    }

    function activateChoiceQuestion(panelEl, detail, lead) {
        panelEl.setAttribute("data-active-lead-id", lead.id);
        setActiveLeadCard(panelEl, lead.id);
        showDrilldownDetail(panelEl, true);
        showSideView(panelEl, "chart");
        ensureDefaultAnswerSelection(panelEl, lead.id);
        var crumbs = buildChoiceBreadcrumb(panelEl, lead.id);
        if (!crumbs.length && detail.choice_breadcrumb) {
            crumbs = detail.choice_breadcrumb.slice();
        }
        updateBreadcrumb(panelEl, crumbs);
        if (isIndicatorPanelVisible(panelEl)) {
            refreshSunburstChart(panelEl);
        }
    }

    function activateLead(panelEl, leadId) {
        var detail = getDrilldownFromPanel(panelEl);
        var lead = getLeadById(detail, leadId);
        if (!detail || !lead) {
            clearDrilldownDetail(panelEl);
            return;
        }
        var responseType = lead.response_type || "choice";
        if (responseType === "open_text") {
            activateOpenTextQuestion(panelEl, detail, lead);
        } else {
            activateChoiceQuestion(panelEl, detail, lead);
        }
    }

    function syncDrilldownFromExpandedLead(panelEl) {
        var leadId = getExpandedLeadId(panelEl);
        if (!leadId) {
            clearDrilldownDetail(panelEl);
            return;
        }
        activateLead(panelEl, leadId);
    }

    function ensureLeadBodyExpanded(panelEl, leadId) {
        var card = panelEl.querySelector('.user-insights-lead-card[data-lead-id="' + leadId + '"]');
        if (!card) {
            return;
        }
        var leadBody = card.querySelector(".user-insights-lead-body");
        if (!leadBody || leadBody.classList.contains("show")) {
            return;
        }
        collapseOtherLeadBodies(panelEl, leadId);
        if (typeof bootstrap !== "undefined" && bootstrap.Collapse) {
            bootstrap.Collapse.getOrCreateInstance(leadBody).show();
        } else {
            leadBody.classList.add("show");
        }
    }

    function bindLeadChevrons(panelEl) {
        panelEl.querySelectorAll(".user-insights-lead-header").forEach(function (btn) {
            var target = btn.getAttribute("data-bs-target");
            if (!target) {
                return;
            }
            var body = panelEl.querySelector(target);
            if (!body) {
                return;
            }
            body.addEventListener("show.bs.collapse", function () {
                var card = btn.closest(".user-insights-lead-card");
                if (!card) {
                    return;
                }
                collapseOtherLeadBodies(panelEl, card.getAttribute("data-lead-id"));
            });
            body.addEventListener("shown.bs.collapse", function () {
                btn.setAttribute("aria-expanded", "true");
                btn.closest(".user-insights-lead-card").classList.add("is-expanded");
                var card = btn.closest(".user-insights-lead-card");
                if (card) {
                    activateLead(panelEl, card.getAttribute("data-lead-id"));
                    if (isIndicatorPanelVisible(panelEl)) {
                        refreshSunburstChart(panelEl);
                    }
                }
            });
            body.addEventListener("hidden.bs.collapse", function () {
                btn.setAttribute("aria-expanded", "false");
                btn.closest(".user-insights-lead-card").classList.remove("is-expanded");
                syncDrilldownFromExpandedLead(panelEl);
            });
        });
    }

    function bindAnswerBars(panelEl) {
        panelEl.addEventListener("click", function (e) {
            var bar = e.target.closest(".user-insights-answer-bar");
            if (!bar || !panelEl.contains(bar)) {
                return;
            }
            var leadId = bar.getAttribute("data-lead-id");
            var responseId = bar.getAttribute("data-response-id");
            var detail = getDrilldownFromPanel(panelEl);
            if (!detail) {
                return;
            }
            ensureLeadBodyExpanded(panelEl, leadId);
            panelEl.querySelectorAll('.user-insights-lead-card[data-lead-id="' + leadId + '"] .user-insights-answer-bar').forEach(function (b) {
                b.classList.toggle("is-selected", b === bar);
            });
            panelEl.querySelectorAll('.user-insights-lead-follow-up-root[data-lead-id="' + leadId + '"]').forEach(function (root) {
                var show = root.getAttribute("data-follow-up-for") === responseId;
                root.classList.toggle("d-none", !show);
            });
            activateLead(panelEl, leadId);
            updateBreadcrumb(panelEl, buildChoiceBreadcrumb(panelEl, leadId));
            if (isIndicatorPanelVisible(panelEl)) {
                refreshSunburstChart(panelEl);
            }
        });
    }

    function bindOptionRows(panelEl) {
        panelEl.addEventListener("click", function (e) {
            var row = e.target.closest(".user-insights-option-row");
            if (!row || !panelEl.contains(row)) {
                return;
            }
            var card = row.closest(".user-insights-lead-card");
            var leadId = card ? card.getAttribute("data-lead-id") : null;
            var wrap = row.closest(".user-insights-option-wrap");
            if (!wrap || !leadId) {
                return;
            }
            var list = wrap.closest(".user-insights-option-list");
            if (list) {
                list.querySelectorAll(".user-insights-option-row").forEach(function (r) {
                    r.classList.remove("is-selected");
                });
                list.querySelectorAll(".user-insights-follow-up-branch").forEach(function (branch) {
                    branch.classList.add("d-none");
                });
            }
            row.classList.add("is-selected");
            var branch = wrap.querySelector(".user-insights-follow-up-branch");
            if (branch) {
                branch.classList.remove("d-none");
            }
            ensureLeadBodyExpanded(panelEl, leadId);
            activateLead(panelEl, leadId);
            var crumbs = buildChoiceBreadcrumb(panelEl, leadId);
            updateBreadcrumb(panelEl, crumbs);
            refreshSunburstChart(panelEl);
        });
    }

    function initDrilldownPanel(panelEl) {
        if (!panelEl || panelEl.getAttribute("data-drilldown-bound") === "true") {
            return;
        }
        panelEl.setAttribute("data-drilldown-bound", "true");
        bindLeadChevrons(panelEl);
        bindAnswerBars(panelEl);
        bindOptionRows(panelEl);
        if (typeof initUserInsightsDateFilter === "function") {
            initUserInsightsDateFilter(panelEl);
        }
        syncDrilldownFromExpandedLead(panelEl);
    }

    function initAllDrilldownPanels() {
        document.querySelectorAll(".user-insights-indicator-panel").forEach(initDrilldownPanel);
    }

    function observeIndicatorExpand() {
        document.querySelectorAll(".user-insights-indicator-detail").forEach(function (collapseEl) {
            collapseEl.addEventListener("shown.bs.collapse", function () {
                var panel = collapseEl.querySelector(".user-insights-indicator-panel");
                if (!panel) {
                    return;
                }
                initDrilldownPanel(panel);
                syncDrilldownFromExpandedLead(panel);
                refreshSunburstChart(panel);
            });
            collapseEl.addEventListener("hidden.bs.collapse", function () {
                var panel = collapseEl.querySelector(".user-insights-indicator-panel");
                if (panel) {
                    clearDrilldownDetail(panel);
                }
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        initAllDrilldownPanels();
        observeIndicatorExpand();
    });

    window.initUserInsightsDrilldownPanel = initDrilldownPanel;
})();
