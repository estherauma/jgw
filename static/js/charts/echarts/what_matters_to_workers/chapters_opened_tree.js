/**
 * ECharts tree chart for chapters opened data.
 * Hierarchy: Chapter Views (root) -> User Destination -> User Origin Country -> Chapter titles view counts
 * (headings) over destination / origin / chapter data; leaves carry total_views and unique_views.
 */
function initChaptersOpenedTreeChart(data, customContainerId) {
    if (typeof echarts === 'undefined') {
        return null;
    }

    const treeData = data && data.tree ? data.tree : data;
    if (treeData.name === 'Chapter views') {
        treeData.name = 'Chapter Views';
    }
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

    function isChapterMetricLeaf(node) {
        return node.total_views != null && node.total_views !== undefined;
    }

    function computeNodeTotals(node) {
        if (isChapterMetricLeaf(node)) {
            node.total = node.total_views;
            return node.total;
        }
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

    var isLegacyTotalUniqueBranch = treeData.children.some(function (c) {
        return c.name === 'Total views' || c.name === 'Unique views';
    });
    if (isLegacyTotalUniqueBranch) {
        treeData.children.forEach(function (child) {
            if (child.children && child.children.length > 0) {
                child.children.unshift({
                    name: 'User Destination',
                    isLayerTitle: true
                });
            }
        });
    } else if (treeData.children && treeData.children.length > 0) {
        treeData.children.unshift({
            name: 'User Destination',
            isLayerTitle: true
        });
    }

    function forEachRealDestination(fn) {
        function walkDestinations(children) {
            if (!children || !children.length) {
                return;
            }
            children.forEach(function (node) {
                if (node.isLayerTitle) {
                    return;
                }
                if (node.children && node.children.length) {
                    fn(node);
                }
            });
        }
        if (isLegacyTotalUniqueBranch) {
            treeData.children.forEach(function (branch) {
                walkDestinations(branch.children);
            });
        } else {
            walkDestinations(treeData.children);
        }
    }

    // User Origin Country labels the column of origin nodes under each destination (not the chapter list).
    forEachRealDestination(function (destinationNode) {
        destinationNode.children.unshift({
            name: 'User Origin Country',
            isLayerTitle: true
        });
    });

    // Chapter titles view counts labels the leaf chapter rows under each origin.
    forEachRealDestination(function (destinationNode) {
        destinationNode.children.forEach(function (originNode) {
            if (originNode.isLayerTitle) {
                return;
            }
            if (originNode.children && originNode.children.length > 0) {
                originNode.children.unshift({
                    name: 'Chapter titles view counts',
                    isLayerTitle: true
                });
            }
        });
    });
    treeData.children.forEach(function (child) {
        assignDepth(child, 1);
    });
    computeNodeTotals(treeData);

    function collapseAllButFirstDestinationInList(children) {
        if (!children || !children.length) {
            return;
        }
        var firstBranchExpanded = false;
        children.forEach(function (node) {
            if (node.isLayerTitle) {
                return;
            }
            if (!node.children || !node.children.length) {
                return;
            }
            if (!firstBranchExpanded) {
                firstBranchExpanded = true;
                delete node.collapsed;
            } else {
                node.collapsed = true;
            }
        });
    }

    if (isLegacyTotalUniqueBranch) {
        treeData.children.forEach(function (branch) {
            if (branch.children && branch.children.length) {
                collapseAllButFirstDestinationInList(branch.children);
            }
        });
    } else {
        collapseAllButFirstDestinationInList(treeData.children);
    }

    function setDisplayTitles(node) {
        if (node.isLayerTitle) {
            node.displayTitle = node.name;
        } else if (isChapterMetricLeaf(node)) {
            const tv = node.total_views;
            const uv = node.unique_views != null ? node.unique_views : 0;
            node.displayTitle =
                node.name +
                '  ·  ' +
                formatCount(tv) +
                ' total / ' +
                formatCount(uv) +
                ' unique';
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
        if (isChapterMetricLeaf(node) || (node.value != null && node.value !== undefined)) return leafColor;
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
                if (isChapterMetricLeaf(node)) {
                    return (
                        '<strong>' +
                        node.name +
                        '</strong><br/>' +
                        'Total views: ' +
                        Number(node.total_views).toLocaleString() +
                        '<br/>' +
                        'Unique views: ' +
                        Number(node.unique_views).toLocaleString()
                    );
                }
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
                name: 'Chapter Views',
                top: 48,
                left: '12%',
                bottom: '2%',
                right: '35%',
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
                    rich: {
                        layerTitle: {
                            fontSize: 13,
                            fontWeight: 700,
                            color: '#1a365d',
                            padding: [3, 8],
                            backgroundColor: 'rgba(49, 130, 206, 0.12)',
                            borderRadius: 4
                        }
                    },
                    formatter: function (params) {
                        const d = params.data;
                        if (d.isLayerTitle) {
                            return '{layerTitle|' + (d.displayTitle != null ? d.displayTitle : d.name) + '}';
                        }
                        return d.displayTitle || d.name;
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
                                fontSize: 13,
                                fontWeight: 700,
                                color: '#1a365d',
                                padding: [3, 8],
                                backgroundColor: 'rgba(49, 130, 206, 0.12)',
                                borderRadius: 4
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
