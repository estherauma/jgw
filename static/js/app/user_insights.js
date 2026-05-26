(function () {
    var chartPayload = null;
    var activeReportId = "early_risk";
    var selectedDonutSlot = null;
    function readChartPayload() {
        var el = document.getElementById("user-insights-chart-payload");
        if (!el || !el.textContent) {
            return null;
        }
        try {
            return JSON.parse(el.textContent);
        } catch (e) {
            console.error("User Insights: invalid chart payload", e);
            return null;
        }
    }

    function getReportDonutMeta(reportId) {
        if (typeof getUserInsightsReportChartMeta === "function") {
            return getUserInsightsReportChartMeta(chartPayload, reportId);
        }
        return { donuts: [], count: 0 };
    }

    function getIndicatorOptions(reportId) {
        if (!chartPayload || !chartPayload.by_report || !chartPayload.by_report[reportId]) {
            return [];
        }
        return chartPayload.by_report[reportId].indicator_options || [];
    }

    function findDonutSlotForBreakdown(reportId, breakdownIndex) {
        var meta = getReportDonutMeta(reportId);
        for (var i = 0; i < meta.donuts.length; i++) {
            if (meta.donuts[i].breakdown_index === breakdownIndex) {
                return i;
            }
        }
        return -1;
    }

    function clearDonutSlotSelection() {
        var row = document.getElementById("user-insights-donut-row");
        selectedDonutSlot = null;
        if (row) {
            row.classList.remove("has-donut-selection");
            row.querySelectorAll(".user-insights-donut-slot-wrap").forEach(function (wrap) {
                wrap.classList.remove("is-selected", "is-dimmed");
                var cell = wrap.querySelector(".user-insights-donut-cell");
                if (cell) {
                    cell.setAttribute("aria-pressed", "false");
                }
            });
        }
        document.querySelectorAll(".user-insights-indicator-block.is-donut-selected").forEach(function (block) {
            block.classList.remove("is-donut-selected");
        });
    }

    function applyDonutSlotSelection(slotIndex) {
        var row = document.getElementById("user-insights-donut-row");
        if (!row) {
            return;
        }
        selectedDonutSlot = slotIndex;
        row.classList.add("has-donut-selection");
        row.querySelectorAll(".user-insights-donut-slot-wrap:not(.d-none)").forEach(function (wrap) {
            var slot = parseInt(wrap.getAttribute("data-slot"), 10);
            var selected = slot === slotIndex;
            wrap.classList.toggle("is-selected", selected);
            wrap.classList.toggle("is-dimmed", !selected);
            var cell = wrap.querySelector(".user-insights-donut-cell");
            if (cell) {
                cell.setAttribute("aria-pressed", selected ? "true" : "false");
            }
        });
    }

    function expandBreakdownIndicator(reportId, breakdownIndex) {
        var stack = document.querySelector(
            '.user-insights-breakdown-stack[data-breakdown-for="' + reportId + '"]'
        );
        if (!stack || typeof bootstrap === "undefined") {
            return;
        }
        var targetId = "user-insights-ind-" + reportId + "-" + breakdownIndex;
        stack.querySelectorAll(".user-insights-indicator-detail").forEach(function (panel) {
            var isTarget = panel.id === targetId;
            var collapse = bootstrap.Collapse.getOrCreateInstance(panel, { toggle: false });
            if (isTarget) {
                collapse.show();
            } else if (panel.classList.contains("show")) {
                collapse.hide();
            }
        });
        stack.querySelectorAll(".user-insights-indicator-block").forEach(function (block) {
            var idx = parseInt(block.getAttribute("data-breakdown-index"), 10);
            block.classList.toggle("is-donut-selected", idx === breakdownIndex);
        });
        var targetBlock = stack.querySelector(
            '.user-insights-indicator-block[data-breakdown-index="' + breakdownIndex + '"]'
        );
        if (targetBlock && !targetBlock.classList.contains("filtered-out")) {
            targetBlock.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
    }

    function selectDonutSlot(slotIndex) {
        if (!chartPayload || slotIndex === null || slotIndex === undefined) {
            return;
        }
        var meta = getReportDonutMeta(activeReportId);
        if (slotIndex < 0 || slotIndex >= meta.count) {
            return;
        }
        var donut = meta.donuts[slotIndex];
        var breakdownIndex =
            donut && typeof donut.breakdown_index === "number"
                ? donut.breakdown_index
                : slotIndex;
        applyDonutSlotSelection(slotIndex);
        expandBreakdownIndicator(activeReportId, breakdownIndex);
    }

    function getActiveIndicatorFilterSelect() {
        var wrap = document.querySelector(
            '.user-insights-indicator-filter-wrap[data-indicator-filter-for="' +
                activeReportId +
                '"]:not(.d-none)'
        );
        return wrap ? wrap.querySelector(".user-insights-indicator-filter") : null;
    }

    function getActiveIndicatorFilterDonutSlots() {
        var select = getActiveIndicatorFilterSelect();
        if (!select) {
            return [];
        }
        var options = getIndicatorOptions(activeReportId);
        var selected = Array.from(select.selectedOptions).map(function (opt) {
            return parseInt(opt.value, 10);
        }).filter(function (n) {
            return !isNaN(n);
        });
        if (!selected.length || selected.length >= options.length) {
            return [];
        }
        return selected;
    }

    function showIndicatorFilterForReport(reportId) {
        document.querySelectorAll(".user-insights-indicator-filter-wrap").forEach(function (wrap) {
            var match = wrap.getAttribute("data-indicator-filter-for") === reportId;
            wrap.classList.toggle("d-none", !match);
        });
        var select = getActiveIndicatorFilterSelect();
        if (select && window.jQuery) {
            var $select = jQuery(select);
            if ($select.data("multiselect")) {
                $select.multiselect("deselectAll", false);
            }
        }
    }

    function applyIndicatorFilter(donutSlots) {
        var showAll = !donutSlots || !donutSlots.length;
        var selectedSet = showAll ? null : new Set(donutSlots);
        var meta = getReportDonutMeta(activeReportId);
        var row = document.getElementById("user-insights-donut-row");

        if (row) {
            row.classList.toggle("has-indicator-filter", !showAll);
            row.querySelectorAll(".user-insights-donut-slot-wrap").forEach(function (wrap) {
                if (wrap.classList.contains("d-none")) {
                    return;
                }
                var slot = parseInt(wrap.getAttribute("data-donut-slot"), 10);
                if (isNaN(slot)) {
                    slot = parseInt(wrap.getAttribute("data-slot"), 10);
                }
                var visible = showAll || selectedSet.has(slot);
                wrap.classList.toggle("indicator-filter-hidden", !visible);
            });
            if (typeof resizeUserInsightsReportDonuts === "function") {
                resizeUserInsightsReportDonuts(chartPayload);
            }
        }

        var stack = document.querySelector(
            '.user-insights-breakdown-stack[data-breakdown-for="' + activeReportId + '"]:not(.d-none)'
        );
        if (stack) {
            stack.querySelectorAll(".user-insights-indicator-block").forEach(function (block) {
                var donutSlot = parseInt(block.getAttribute("data-donut-slot"), 10);
                var visible = showAll || selectedSet.has(donutSlot);
                block.classList.toggle("indicator-filter-hidden", !visible);
                if (!visible && typeof bootstrap !== "undefined") {
                    var panel = block.querySelector(".user-insights-indicator-detail");
                    if (panel && panel.classList.contains("show")) {
                        bootstrap.Collapse.getOrCreateInstance(panel, { toggle: false }).hide();
                    }
                }
            });
        }

        clearDonutSlotSelection();
        filterIndicators();

        if (!showAll && donutSlots.length === 1) {
            var slot = donutSlots[0];
            var donut = meta.donuts[slot];
            if (donut) {
                applyDonutSlotSelection(slot);
                expandBreakdownIndicator(activeReportId, donut.breakdown_index);
            }
        }
    }

    function initIndicatorFilter() {
        if (!window.jQuery) {
            return;
        }
        document.querySelectorAll(".user-insights-indicator-filter").forEach(function (select) {
            var allText = select.getAttribute("data-all-text") || "All indicators";
            var nSelectedText = select.getAttribute("data-n-selected-text") || "indicators selected";
            var $select = jQuery(select);
            if ($select.data("multiselect")) {
                return;
            }
            $select.multiselect({
                maxHeight: 400,
                enableFiltering: true,
                enableCaseInsensitiveFiltering: true,
                includeSelectAllOption: true,
                selectAllText: allText,
                nonSelectedText: allText,
                allSelectedText: allText,
                nSelectedText: nSelectedText,
                numberDisplayed: 2,
                buttonWidth: "100%",
                buttonClass: "btn user-insights-indicator-filter-btn",
            });
            $select.on("change", function () {
                var reportId = select.getAttribute("data-report-id");
                if (reportId !== activeReportId) {
                    return;
                }
                applyIndicatorFilter(getActiveIndicatorFilterDonutSlots());
            });
        });
    }

    function resetIndicatorFilterForReport(reportId) {
        showIndicatorFilterForReport(reportId);
        applyIndicatorFilter([]);
    }

    window.selectUserInsightsDonutSlot = selectDonutSlot;
    window.onUserInsightsReportDonutsRendered = function (reportId) {
        if (reportId !== activeReportId) {
            return;
        }
        applyIndicatorFilter(getActiveIndicatorFilterDonutSlots());
    };

    function setActiveReport(reportId) {
        if (!reportId) {
            return;
        }
        activeReportId = reportId;
        selectedDonutSlot = null;

        document.querySelectorAll(".user-insights-report-accordion-item").forEach(function (item) {
            var id = item.getAttribute("data-report-id");
            var expanded = id === reportId;
            item.classList.toggle("is-expanded", expanded);
            var collapsedBtn = item.querySelector(".user-insights-report-collapsed");
            if (collapsedBtn) {
                collapsedBtn.setAttribute("aria-expanded", expanded ? "true" : "false");
            }
        });

        document.querySelectorAll("[data-breakdown-for]").forEach(function (el) {
            var match = el.getAttribute("data-breakdown-for") === reportId;
            el.classList.toggle("d-none", !match);
        });

        var titleEl = document.getElementById("user-insights-active-report-title");
        var selected = document.querySelector(
            '.user-insights-report-accordion-item[data-report-id="' + reportId + '"]'
        );
        if (titleEl && selected) {
            var titleNode = selected.querySelector(".user-insights-report-active-title");
            if (titleNode) {
                titleEl.textContent = titleNode.textContent.trim();
            }
        }

        var mainCard = document.getElementById("user-insights-main-chart-card");
        if (mainCard) {
            mainCard.setAttribute("data-active-report", reportId);
        }

        resetIndicatorFilterForReport(reportId);

        if (typeof renderUserInsightsReportDonuts === "function") {
            renderUserInsightsReportDonuts(reportId, chartPayload);
        } else if (typeof renderUserInsightsRiskIndicatorDonuts === "function") {
            renderUserInsightsRiskIndicatorDonuts(reportId, chartPayload);
        } else {
            filterIndicators();
        }
    }

    function initReportAccordion() {
        document.querySelectorAll(".user-insights-report-collapsed").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var item = btn.closest(".user-insights-report-accordion-item");
                if (!item) {
                    return;
                }
                var id = item.getAttribute("data-report-id");
                setActiveReport(id);
            });
        });

        var initial = document.querySelector(".user-insights-report-accordion-item.is-expanded");
        if (initial && initial.getAttribute("data-report-id")) {
            activeReportId = initial.getAttribute("data-report-id");
        } else if (chartPayload && chartPayload.default_report_id) {
            activeReportId = chartPayload.default_report_id;
        }
        setActiveReport(activeReportId);
    }

    function filterIndicators() {
        var input = document.getElementById("user-insights-keyword-search");
        var visible = document.querySelector(".user-insights-breakdown-stack:not(.d-none)");
        if (!input || !visible) {
            return;
        }
        var q = input.value.trim().toLowerCase();
        visible.querySelectorAll(".user-insights-indicator-block").forEach(function (block) {
            if (block.classList.contains("indicator-filter-hidden")) {
                return;
            }
            var name = (block.getAttribute("data-indicator-name") || "").toLowerCase();
            if (!q || name.indexOf(q) !== -1) {
                block.classList.remove("filtered-out");
            } else {
                block.classList.add("filtered-out");
            }
        });
    }

    function initIndicatorSearch() {
        var input = document.getElementById("user-insights-keyword-search");
        if (!input) {
            return;
        }
        input.addEventListener("input", filterIndicators);
    }

    function initAccordionIcons() {
        document.querySelectorAll(".user-insights-indicator-row").forEach(function (btn) {
            var target = btn.getAttribute("data-bs-target");
            if (!target) {
                return;
            }
            var panel = document.querySelector(target);
            var icon = btn.querySelector(".expand-icon");
            if (!panel || !icon) {
                return;
            }
            panel.addEventListener("shown.bs.collapse", function () {
                icon.textContent = "−";
                btn.setAttribute("aria-expanded", "true");
                var block = btn.closest(".user-insights-indicator-block");
                var stack = block && block.closest(".user-insights-breakdown-stack");
                if (!block || !stack) {
                    return;
                }
                var reportId = stack.getAttribute("data-breakdown-for");
                var breakdownIndex = parseInt(block.getAttribute("data-breakdown-index"), 10);
                if (reportId !== activeReportId || isNaN(breakdownIndex)) {
                    return;
                }
                var slot = findDonutSlotForBreakdown(reportId, breakdownIndex);
                if (slot >= 0) {
                    applyDonutSlotSelection(slot);
                }
                stack.querySelectorAll(".user-insights-indicator-block").forEach(function (el) {
                    var idx = parseInt(el.getAttribute("data-breakdown-index"), 10);
                    el.classList.toggle("is-donut-selected", idx === breakdownIndex);
                });
            });
            panel.addEventListener("hidden.bs.collapse", function () {
                icon.textContent = "+";
                btn.setAttribute("aria-expanded", "false");
                var block = btn.closest(".user-insights-indicator-block");
                if (block) {
                    block.classList.remove("is-donut-selected");
                }
            });
        });
    }

    function initDonutSlotClicks() {
        var row = document.getElementById("user-insights-donut-row");
        if (!row) {
            return;
        }
        function activateFromWrap(wrap) {
            if (
                !wrap ||
                wrap.classList.contains("d-none") ||
                wrap.classList.contains("indicator-filter-hidden")
            ) {
                return;
            }
            var slot = parseInt(wrap.getAttribute("data-slot"), 10);
            if (!isNaN(slot)) {
                selectDonutSlot(slot);
            }
        }
        row.addEventListener("click", function (e) {
            var wrap = e.target.closest(".user-insights-donut-slot-wrap");
            if (!wrap || !row.contains(wrap)) {
                return;
            }
            e.preventDefault();
            activateFromWrap(wrap);
        });
        row.addEventListener("keydown", function (e) {
            if (e.key !== "Enter" && e.key !== " ") {
                return;
            }
            var cell = e.target.closest(".user-insights-donut-cell");
            if (!cell) {
                return;
            }
            var wrap = cell.closest(".user-insights-donut-slot-wrap");
            if (!wrap || !row.contains(wrap)) {
                return;
            }
            e.preventDefault();
            activateFromWrap(wrap);
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        chartPayload = readChartPayload();
        window.userInsightsChartPayload = chartPayload;
        initIndicatorFilter();
        initReportAccordion();
        initIndicatorSearch();
        initAccordionIcons();
        initDonutSlotClicks();
    });
})();
