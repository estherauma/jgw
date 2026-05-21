/**
 * User Insights – actionable From/To date filter (flatpickr).
 */
(function () {
    function dispatchDateChange(panelEl, fromDate, toDate) {
        panelEl.dispatchEvent(
            new CustomEvent("user-insights:date-filter-change", {
                bubbles: true,
                detail: { from: fromDate, to: toDate },
            })
        );
    }

    function initDateFilter(panelEl) {
        var filter = panelEl.querySelector("[data-user-insights-date-filter]");
        if (!filter || filter.getAttribute("data-date-filter-bound") === "true") {
            return;
        }
        if (typeof flatpickr === "undefined") {
            return;
        }

        var fromInput = filter.querySelector('[data-date-role="from"]');
        var toInput = filter.querySelector('[data-date-role="to"]');
        var calendarBtn = filter.querySelector(".user-insights-date-filter-calendar-btn");
        if (!fromInput || !toInput) {
            return;
        }

        filter.setAttribute("data-date-filter-bound", "true");

        var fpOptions = {
            dateFormat: "j F Y",
            allowInput: true,
            disableMobile: true,
        };

        var fpFrom = flatpickr(fromInput, {
            dateFormat: fpOptions.dateFormat,
            allowInput: fpOptions.allowInput,
            disableMobile: fpOptions.disableMobile,
            defaultDate: fromInput.getAttribute("data-default-date") || undefined,
            onChange: function (selectedDates) {
                if (fpTo && selectedDates[0]) {
                    fpTo.set("minDate", selectedDates[0]);
                }
                dispatchDateChange(panelEl, fpFrom.selectedDates[0], fpTo.selectedDates[0]);
            },
        });

        var fpTo = flatpickr(toInput, {
            dateFormat: fpOptions.dateFormat,
            allowInput: fpOptions.allowInput,
            disableMobile: fpOptions.disableMobile,
            defaultDate: toInput.getAttribute("data-default-date") || undefined,
            onChange: function () {
                dispatchDateChange(panelEl, fpFrom.selectedDates[0], fpTo.selectedDates[0]);
            },
        });

        if (fpFrom.selectedDates[0]) {
            fpTo.set("minDate", fpFrom.selectedDates[0]);
        }

        if (calendarBtn) {
            calendarBtn.addEventListener("click", function () {
                fpFrom.open();
            });
        }

        fromInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                fpFrom.setDate(fromInput.value, true);
            }
        });
        toInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                fpTo.setDate(toInput.value, true);
            }
        });
    }

    function initAllDateFilters() {
        document.querySelectorAll(".user-insights-indicator-panel").forEach(initDateFilter);
    }

    document.addEventListener("DOMContentLoaded", function () {
        initAllDateFilters();
    });

    window.initUserInsightsDateFilter = initDateFilter;
})();
