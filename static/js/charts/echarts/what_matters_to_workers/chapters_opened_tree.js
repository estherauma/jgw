/**
 * ECharts tree chart for chapters opened data.
 * Accepts tree data: { name, children } with optional leaf nodes { name, value }.
 * Data can be the full API response { tree, labels, ... } or the tree object directly.
 */
function initChaptersOpenedTreeChart(data, customContainerId) {
    if (typeof echarts === 'undefined') {
        return null;
    }

    const treeData = data && data.tree ? data.tree : data;
    const containerId = customContainerId || 'chapters-opened-tree-chart-id';
    const chartDom = document.getElementById(containerId);

    if (!chartDom) {
        return null;
    }

    if (!treeData || !treeData.children || treeData.children.length === 0) {
        return null;
    }

    const existingChart = echarts.getInstanceByDom(chartDom);
    if (existingChart) {
        existingChart.dispose();
    }

    const myChart = echarts.init(chartDom);
    myChart.showLoading();

    const levelColors = ['#1a365d', '#2c5282', '#2b6cb0', '#3182ce', '#4299e1'];
    const leafColor = '#63b3ed';
    const lineColor = 'rgba(99, 179, 237, 0.45)';
    const labelColor = '#2d3748';
    const labelColorLight = '#718096';

    function assignDepth(node, depth) {
        node.depth = depth;
        if (node.children && node.children.length) {
            node.children.forEach(function (child) {
                assignDepth(child, depth + 1);
            });
        }
    }
    treeData.depth = 0;
    treeData.children.forEach(function (child) {
        assignDepth(child, 1);
    });

    function formatCount(n) {
        if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
        if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
        return String(n);
    }

    function computeNodeTotals(node) {
        if (node.value != null && node.value !== undefined) {
            node.total = node.value;
            return node.total;
        }
        node.total = 0;
        if (node.children && node.children.length) {
            node.children.forEach(function (child) {
                node.total += computeNodeTotals(child);
            });
        }
        return node.total;
    }
    computeNodeTotals(treeData);
    treeData.children.forEach(function (child, index) {
        if (index % 2 === 0) {
            child.collapsed = true;
        }
    });

    treeData.children.forEach(function (child) {
        if (child.children && child.children.length > 0) {
            child.children.unshift({
                name: 'User Destination',
                isLayerTitle: true
            });
        }
    });

    treeData.children.forEach(function (middleChild) {
        if (middleChild.children) {
            middleChild.children.forEach(function (grandchild) {
                if (grandchild.children && grandchild.children.length > 0 && !grandchild.isLayerTitle) {
                    grandchild.children.unshift({
                        name: 'User Origin Country',
                        isLayerTitle: true
                    });
                }
            });
        }
    });

    treeData.children.forEach(function (middleChild) {
        if (middleChild.children) {
            middleChild.children.forEach(function (grandchild) {
                if (grandchild.children) {
                    grandchild.children.forEach(function (greatGrandchild) {
                        if (greatGrandchild.children && greatGrandchild.children.length > 0 && !greatGrandchild.isLayerTitle) {
                            greatGrandchild.children.unshift({
                                name: 'Chapter titles viewed',
                                isLayerTitle: true
                            });
                        }
                    });
                }
            });
        }
    });
    treeData.children.forEach(function (child) {
        assignDepth(child, 1);
    });
    computeNodeTotals(treeData);

    function setDisplayTitles(node) {
        if (node.isLayerTitle) {
            node.displayTitle = node.name;
        } else {
            const total = node.total != null ? node.total : (node.value != null ? node.value : 0);
            node.displayTitle = node.name + (total > 0 ? '  ·  ' + formatCount(total) : '');
        }
        if (node.children && node.children.length) {
            node.children.forEach(setDisplayTitles);
        }
    }
    treeData.displayTitle = treeData.name || 'Chapter Views';
    treeData.children.forEach(setDisplayTitles);

    function getNodeColor(node) {
        if (node.isLayerTitle) return 'transparent';
        if (node.value != null && node.value !== undefined) return leafColor;
        const d = node.depth != null ? node.depth : 0;
        return levelColors[Math.min(d, levelColors.length - 1)];
    }

    myChart.hideLoading();
    myChart.setOption({
        tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove',
            backgroundColor: 'rgba(26, 32, 44, 0.94)',
            borderColor: 'rgba(99, 179, 237, 0.4)',
            borderWidth: 1,
            padding: 10,
            textStyle: {
                fontSize: 12,
                color: '#e2e8f0'
            },
            formatter: function (params) {
                const node = params.data;
                if (node.isLayerTitle) return node.name;
                const title = node.displayTitle || node.name;
                const total = node.total != null ? node.total : node.value;
                if (total != null && total !== undefined) {
                    return '<strong>' + title + '</strong><br/>Views: ' + (total).toLocaleString();
                }
                return title;
            }
        },
        series: [
            {
                type: 'tree',
                data: [treeData],
                name: 'Chapter views',
                top: 48,
                left: '5%',
                bottom: '2%',
                right: '25%',
                symbolSize: function (value, params) {
                    return (params.data && params.data.isLayerTitle) ? 0 : 10;
                },
                edgeForkPosition: '50%',
                initialTreeDepth: 2,
                lineStyle: {
                    color: lineColor,
                    width: 1.5,
                    curveness: 0.35
                },
                label: {
                    position: 'left',
                    verticalAlign: 'middle',
                    align: 'right',
                    fontSize: 12,
                    color: labelColor,
                    fontWeight: 500,
                    formatter: function (params) {
                        return params.data.displayTitle || params.data.name;
                    }
                },
                leaves: {
                    label: {
                        position: 'right',
                        verticalAlign: 'middle',
                        align: 'left',
                        fontSize: 12,
                        color: labelColorLight,
                        rich: {
                            layerTitle: {
                                fontWeight: 'bold',
                                color: labelColor
                            }
                        },
                        formatter: function (params) {
                            const d = params.data;
                            const text = d.displayTitle != null ? d.displayTitle : d.name;
                            return d.isLayerTitle ? '{layerTitle|' + text + '}' : text;
                        }
                    },
                    itemStyle: function (params) {
                        if (params.data && params.data.isLayerTitle) {
                            return { color: 'transparent', borderColor: 'transparent', borderWidth: 0 };
                        }
                        return { color: leafColor, borderColor: 'rgba(99, 179, 237, 0.6)', borderWidth: 1 };
                    }
                },
                itemStyle: {
                    color: function (params) {
                        return getNodeColor(params.data);
                    },
                    borderColor: 'rgba(255,255,255,0.9)',
                    borderWidth: 1.5
                },
                emphasis: {
                    focus: 'descendant',
                    itemStyle: {
                        borderColor: '#3182ce',
                        borderWidth: 2,
                        shadowBlur: 8,
                        shadowColor: 'rgba(49, 130, 206, 0.35)'
                    },
                    lineStyle: {
                        width: 3.5,
                        color: 'rgba(49, 130, 206, 0.6)'
                    }
                },
                expandAndCollapse: true,
                animationDuration: 450,
                animationDurationUpdate: 650,
            }
        ]
    });

    const resizeHandler = function () {
        try {
            if (myChart && typeof myChart.resize === 'function') {
                myChart.resize();
            }
        } catch (e) {}
    };
    window.addEventListener('resize', resizeHandler);
    myChart._chaptersOpenedTreeResizeHandler = resizeHandler;

    return myChart;
}
