/**
 * ECharts: User Insights – reusable report donut charts.
 *
 * Renders any report defined in chartPayload.by_report (e.g. early_risk,
 * decent_employment, responsible_recruitment). Each donut uses the same
 * needs_action / on_track / no_response schema and shared legend colors.
 */
var USER_INSIGHTS_DONUT_ROW_ID = "user-insights-donut-row";
var USER_INSIGHTS_DONUT_ID_PREFIX = "user-insights-donut-";
var USER_INSIGHTS_DEFAULT_MAX_SLOTS = 5;
var userInsightsDonutResizeScheduled = false;

/**
 * @param {object} chartPayload - JSON from #user-insights-chart-payload
 * @returns {number}
 */
function getUserInsightsMaxDonutSlots(chartPayload) {
    if (!chartPayload || !chartPayload.by_report) {
        return USER_INSIGHTS_DEFAULT_MAX_SLOTS;
    }
    var max = 0;
    Object.keys(chartPayload.by_report).forEach(function (reportId) {
        var report = chartPayload.by_report[reportId];
        var n =
            report && typeof report.donut_count === "number"
                ? report.donut_count
                : report && report.donuts
                  ? report.donuts.length
                  : 0;
        if (n > max) {
            max = n;
        }
    });
    return max || USER_INSIGHTS_DEFAULT_MAX_SLOTS;
}

/**
 * @param {object} chartPayload
 * @param {string} reportId - e.g. early_risk | decent_employment | responsible_recruitment
 * @returns {{ donuts: Array, count: number }}
 */
function getUserInsightsReportChartMeta(chartPayload, reportId) {
    if (!chartPayload || !reportId) {
        return { donuts: [], count: 0 };
    }
    var byReport =
        chartPayload.by_report && chartPayload.by_report[reportId]
            ? chartPayload.by_report[reportId]
            : null;
    if (!byReport) {
        console.warn("User Insights donut: unknown report id", reportId);
        return { donuts: [], count: 0 };
    }
    var donuts = byReport.donuts || [];
    var count =
        typeof byReport.donut_count === "number" ? byReport.donut_count : donuts.length;
    return { donuts: donuts, count: count };
}

/**
 * @param {object} chartPayload - legends + colors
 * @param {object} donut - { title, needs_action, on_track, no_response }
 */
function buildUserInsightsReportDonutOption(chartPayload, donut) {
    var legends = chartPayload.legends;
    var colors = chartPayload.colors;
    var data = [
        {
            name: legends.needs_action,
            value: donut.needs_action,
            itemStyle: { color: colors.needs_action },
        },
        {
            name: legends.on_track,
            value: donut.on_track,
            itemStyle: { color: colors.on_track },
        },
        {
            name: legends.no_response,
            value: donut.no_response,
            itemStyle: { color: colors.no_response },
        },
    ];
    var hiddenSliceLabel = { show: false };
    var hiddenSliceLabelLine = { show: false };
    return {
        tooltip: {
            trigger: "item",
            formatter: "{b}: {c}% ({d}%)",
            confine: true,
        },
        graphic: [
            {
                type: "text",
                left: "center",
                top: "center",
                z: 10,
                style: {
                    text: donut.title,
                    textAlign: "center",
                    fill: "#1a3b5d",
                    font: "600 13px Arial, sans-serif",
                    lineHeight: 16,
                    width: 118,
                    overflow: "break",
                },
            },
        ],
        series: [
            {
                type: "pie",
                radius: ["60%", "82%"],
                center: ["50%", "50%"],
                avoidLabelOverlap: false,
                itemStyle: { borderColor: "#fff", borderWidth: 1 },
                label: { show: false },
                labelLine: { show: false },
                emphasis: {
                    scale: true,
                    scaleSize: 4,
                    label: { show: false },
                    labelLine: { show: false },
                },
                data: data.map(function (item) {
                    return Object.assign({}, item, {
                        label: hiddenSliceLabel,
                        labelLine: hiddenSliceLabelLine,
                        emphasis: {
                            label: hiddenSliceLabel,
                            labelLine: hiddenSliceLabelLine,
                        },
                    });
                }),
            },
        ],
    };
}

/**
 * Initialise one donut chart (any report).
 * @returns {object|null} ECharts instance
 */
function initUserInsightsReportDonut(donut, containerId, chartPayload) {
    if (typeof echarts === "undefined") {
        console.error("User Insights donut: ECharts is not loaded");
        return null;
    }
    var chartDom = document.getElementById(containerId);
    if (!chartDom || !donut || !chartPayload) {
        console.error("User Insights donut: container or data not found", {
            container: containerId,
            donut: donut,
        });
        return null;
    }
    var existingChart = echarts.getInstanceByDom(chartDom);
    if (existingChart) {
        existingChart.dispose();
    }
    var chart = echarts.init(chartDom);
    chart.setOption(buildUserInsightsReportDonutOption(chartPayload, donut));
    return chart;
}

function resizeUserInsightsReportDonuts(chartPayload) {
    if (typeof echarts === "undefined") {
        return;
    }
    var maxSlots = getUserInsightsMaxDonutSlots(chartPayload);
    for (var i = 0; i < maxSlots; i++) {
        var dom = document.getElementById(USER_INSIGHTS_DONUT_ID_PREFIX + i);
        if (!dom) {
            continue;
        }
        var instance = echarts.getInstanceByDom(dom);
        if (instance) {
            instance.resize();
        }
    }
}

function scheduleUserInsightsReportDonutResize(chartPayload) {
    if (userInsightsDonutResizeScheduled) {
        return;
    }
    userInsightsDonutResizeScheduled = true;
    window.addEventListener(
        "resize",
        function () {
            resizeUserInsightsReportDonuts(chartPayload);
        },
        { passive: true }
    );
}

/**
 * Render donuts for the selected report (Early Risk, Decent Employment, or Responsible Recruitment).
 * @param {string} reportId
 * @param {object} chartPayload
 */
function renderUserInsightsReportDonuts(reportId, chartPayload) {
    if (typeof echarts === "undefined" || !chartPayload) {
        return;
    }
    var meta = getUserInsightsReportChartMeta(chartPayload, reportId);
    var donuts = meta.donuts;
    var count = meta.count;
    var maxSlots = getUserInsightsMaxDonutSlots(chartPayload);
    scheduleUserInsightsReportDonutResize(chartPayload);

    var row = document.getElementById(USER_INSIGHTS_DONUT_ROW_ID);
    if (row) {
        row.setAttribute("data-donut-count", String(count));
        row.setAttribute("data-active-report", reportId);
    }

    for (var i = 0; i < maxSlots; i++) {
        var wrap = document.querySelector('.user-insights-donut-slot-wrap[data-slot="' + i + '"]');
        var containerId = USER_INSIGHTS_DONUT_ID_PREFIX + i;
        var dom = document.getElementById(containerId);
        if (i >= count) {
            if (dom && echarts.getInstanceByDom(dom)) {
                echarts.getInstanceByDom(dom).dispose();
            }
            if (wrap) {
                wrap.classList.add("d-none");
            }
            continue;
        }
        if (wrap) {
            wrap.classList.remove("d-none");
        }
        if (donuts[i]) {
            var chart = initUserInsightsReportDonut(donuts[i], containerId, chartPayload);
            if (dom) {
                dom.removeAttribute("title");
                dom.setAttribute("aria-label", donuts[i].title);
            }
            if (wrap && donuts[i].breakdown_index !== undefined) {
                wrap.setAttribute(
                    "data-breakdown-index",
                    String(donuts[i].breakdown_index)
                );
            }
            if (chart) {
                chart.off("click");
                (function (slotIndex) {
                    chart.on("click", function () {
                        if (typeof window.selectUserInsightsDonutSlot === "function") {
                            window.selectUserInsightsDonutSlot(slotIndex);
                        }
                    });
                })(i);
            }
        }
    }

    if (typeof window.onUserInsightsReportDonutsRendered === "function") {
        window.onUserInsightsReportDonutsRendered(reportId);
    }
}

/**
 * Page bootstrap: render initial report from payload.default_report_id.
 */
function initUserInsightsReportDonuts(chartPayload, initialReportId) {
    var reportId =
        initialReportId ||
        (chartPayload && chartPayload.default_report_id) ||
        "early_risk";
    renderUserInsightsReportDonuts(reportId, chartPayload);
}

/* Backward-compatible aliases */
var renderUserInsightsRiskIndicatorDonuts = renderUserInsightsReportDonuts;
var initUserInsightsRiskIndicatorDonut = initUserInsightsReportDonut;
var buildUserInsightsRiskIndicatorDonutOption = buildUserInsightsReportDonutOption;
var resizeUserInsightsRiskIndicatorDonuts = function () {
    resizeUserInsightsReportDonuts(
        window.userInsightsChartPayload || null
    );
};
