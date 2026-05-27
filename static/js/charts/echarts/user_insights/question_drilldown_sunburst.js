/**
 * ECharts sunburst for User Insights indicator question drill-down.
 */
var userInsightsSunburstInstances = {};
var userInsightsSunburstNodeIndex = {};
var userInsightsSunburstPending = {};
var userInsightsSunburstResizeObservers = {};

function sunburstHostHasLayout(dom) {
    if (!dom || !dom.offsetParent) {
        return false;
    }
    var rect = dom.getBoundingClientRect();
    return rect.width >= 80 && rect.height >= 80;
}

function scheduleUserInsightsSunburstResize(chart) {
    if (!chart || chart.isDisposed()) {
        return;
    }
    chart.resize();
    requestAnimationFrame(function () {
        if (!chart.isDisposed()) {
            chart.resize();
        }
    });
    requestAnimationFrame(function () {
        requestAnimationFrame(function () {
            if (!chart.isDisposed()) {
                chart.resize();
            }
        });
    });
    setTimeout(function () {
        if (!chart.isDisposed()) {
            chart.resize();
        }
    }, 350);
}

function observeSunburstHostResize(containerId, dom, chart) {
    if (typeof ResizeObserver === "undefined" || !dom) {
        return;
    }
    if (userInsightsSunburstResizeObservers[containerId]) {
        userInsightsSunburstResizeObservers[containerId].disconnect();
    }
    var observer = new ResizeObserver(function () {
        if (!sunburstHostHasLayout(dom)) {
            return;
        }
        var pending = userInsightsSunburstPending[containerId];
        if (pending) {
            delete userInsightsSunburstPending[containerId];
            renderUserInsightsSunburstChart(containerId, dom, pending.sunburstData, pending.highlightName);
            return;
        }
        var instance = userInsightsSunburstInstances[containerId];
        if (instance && !instance.isDisposed()) {
            scheduleUserInsightsSunburstResize(instance);
        }
    });
    observer.observe(dom);
    userInsightsSunburstResizeObservers[containerId] = observer;
}

function escapeSunburstTooltipText(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

var SUNBURST_PATH_SEP = "\u0001";

/**
 * Index sunburst nodes by ancestor path so tooltips can resolve question text.
 * @param {Array} nodes
 * @param {string[]} ancestorNames
 * @param {object} index
 * @returns {object}
 */
function buildSunburstNodeIndex(nodes, ancestorNames, index) {
    if (!nodes || !nodes.length) {
        return index;
    }
    nodes.forEach(function (node) {
        if (!node || !node.name) {
            return;
        }
        var names = ancestorNames.concat([node.name]);
        var pathKey = names.join(SUNBURST_PATH_SEP);
        index[pathKey] = {
            name: node.name,
            question: node.question || null,
            value: node.value,
        };
        if (node.children && node.children.length) {
            buildSunburstNodeIndex(node.children, names, index);
        }
    });
    return index;
}

/**
 * Resolve path segment names from ECharts tooltip params.
 * @param {object} params
 * @returns {string[]}
 */
function getSunburstPathNames(params) {
    var names = [];
    if (params.treePathInfo && params.treePathInfo.length) {
        params.treePathInfo.forEach(function (node) {
            if (node && node.name) {
                names.push(node.name);
            }
        });
    }
    if (!names.length && params.name) {
        names.push(params.name);
    }
    return names;
}

/**
 * @param {string} containerId
 * @param {object} params - ECharts tooltip params
 * @returns {string}
 */
function formatUserInsightsSunburstTooltip(containerId, params) {
    if (!params) {
        return "";
    }
    var index = userInsightsSunburstNodeIndex[containerId] || {};
    var pathNames = getSunburstPathNames(params);
    var layers = [];

    pathNames.forEach(function (name, i) {
        var pathKey = pathNames.slice(0, i + 1).join(SUNBURST_PATH_SEP);
        var meta = index[pathKey];
        var isHovered = i === pathNames.length - 1;

        if (!meta && isHovered && params.data) {
            meta = {
                name: params.data.name || params.name,
                question: params.data.question || null,
                value: params.data.value != null ? params.data.value : params.value,
            };
        }

        if (!meta) {
            return;
        }

        var response = meta.name || name;
        var count = meta.value != null ? meta.value : isHovered ? params.value : null;

        if (meta.question) {
            layers.push(
                '<div class="user-insights-sunburst-tip-layer">' +
                '<div class="user-insights-sunburst-tip-question">' +
                escapeSunburstTooltipText(meta.question) +
                "</div>" +
                '<div class="user-insights-sunburst-tip-response">' +
                "<strong>" +
                escapeSunburstTooltipText(response) +
                "</strong>" +
                (count != null ? ' <span class="user-insights-sunburst-tip-count">(' + count + ")</span>" : "") +
                "</div>" +
                "</div>"
            );
        } else {
            layers.push(
                '<div class="user-insights-sunburst-tip-layer">' +
                "<strong>" +
                escapeSunburstTooltipText(response) +
                "</strong>" +
                (count != null ? ": " + count : "") +
                "</div>"
            );
        }
    });

    if (!layers.length) {
        return params.name + (params.value != null ? ": " + params.value : "");
    }

    return (
        '<div class="user-insights-sunburst-tooltip">' +
        layers.join('<div class="user-insights-sunburst-tip-divider"></div>') +
        "</div>"
    );
}

function buildUserInsightsSunburstOption(sunburstData, highlightName, containerId) {
    return {
        tooltip: {
            trigger: "item",
            confine: true,
            backgroundColor: "#fff",
            borderColor: "#dce4ee",
            borderWidth: 1,
            padding: 12,
            textStyle: {
                color: "#193560",
                fontSize: 13,
                lineHeight: 20,
            },
            extraCssText:
                "box-shadow: 0 8px 24px rgba(25, 53, 96, 0.15); border-radius: 8px; max-width: 320px;",
            formatter: function (params) {
                return formatUserInsightsSunburstTooltip(containerId, params);
            },
        },
        series: [
            {
                type: "sunburst",
                left: "4%",
                right: "4%",
                top: "6%",
                bottom: "6%",
                radius: ["18%", "72%"],
                center: ["50%", "50%"],
                sort: null,
                nodeClick: false,
                emphasis: {
                    focus: "ancestor",
                },
                label: {
                    show: false,
                },
                labelLayout: {
                    hideOverlap: true,
                },
                levels: [
                    {},
                    {
                        r0: "0%",
                        r: "42%",
                        label: { show: false },
                        itemStyle: { borderWidth: 2, borderColor: "#fff" },
                    },
                    {
                        r0: "42%",
                        r: "68%",
                        label: { show: false },
                        itemStyle: { borderWidth: 2, borderColor: "#fff" },
                    },
                    {
                        r0: "68%",
                        r: "100%",
                        label: {
                            show: true,
                            position: "outside",
                            distance: 6,
                            formatter: function (params) {
                                if (highlightName && params.name === highlightName) {
                                    return params.name;
                                }
                                return "";
                            },
                            color: "#193560",
                            fontSize: 10,
                            fontWeight: 600,
                            width: 90,
                            overflow: "truncate",
                        },
                        itemStyle: { borderWidth: 2, borderColor: "#fff" },
                    },
                ],
                data: sunburstData,
            },
        ],
    };
}

/**
 * @param {string} containerId
 * @param {HTMLElement} dom
 * @param {Array} sunburstData
 * @param {string} [highlightName]
 * @returns {object|null}
 */
function renderUserInsightsSunburstChart(containerId, dom, sunburstData, highlightName) {
    var existing = echarts.getInstanceByDom(dom);
    if (existing) {
        delete userInsightsSunburstNodeIndex[containerId];
        existing.dispose();
    }
    userInsightsSunburstNodeIndex[containerId] = buildSunburstNodeIndex(sunburstData, [], {});
    var chart = echarts.init(dom);
    chart.setOption(buildUserInsightsSunburstOption(sunburstData, highlightName, containerId));
    userInsightsSunburstInstances[containerId] = chart;
    observeSunburstHostResize(containerId, dom, chart);
    scheduleUserInsightsSunburstResize(chart);
    return chart;
}

/**
 * @param {string} containerId
 * @param {Array} sunburstData
 * @param {string} [highlightName]
 * @returns {object|null}
 */
function initUserInsightsSunburst(containerId, sunburstData, highlightName) {
    if (typeof echarts === "undefined") {
        return null;
    }
    var dom = document.getElementById(containerId);
    if (!dom || !sunburstData) {
        return null;
    }
    userInsightsSunburstPending[containerId] = {
        sunburstData: sunburstData,
        highlightName: highlightName,
    };
    if (!sunburstHostHasLayout(dom)) {
        observeSunburstHostResize(containerId, dom, null);
        return null;
    }
    delete userInsightsSunburstPending[containerId];
    return renderUserInsightsSunburstChart(containerId, dom, sunburstData, highlightName);
}

function resizeUserInsightsSunburst(containerId) {
    var chart = userInsightsSunburstInstances[containerId];
    if (chart && !chart.isDisposed()) {
        scheduleUserInsightsSunburstResize(chart);
        return;
    }
    var pending = userInsightsSunburstPending[containerId];
    if (pending) {
        initUserInsightsSunburst(containerId, pending.sunburstData, pending.highlightName);
    }
}

function resizeAllUserInsightsSunbursts() {
    Object.keys(userInsightsSunburstInstances).forEach(function (id) {
        resizeUserInsightsSunburst(id);
    });
}

window.addEventListener(
    "resize",
    function () {
        resizeAllUserInsightsSunbursts();
    },
    { passive: true }
);
