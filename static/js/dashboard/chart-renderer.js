/**
 * Chart Renderer
 * Handles dynamic rendering of charts based on chart ID and type
 */

const ChartRenderer = {
    renderChart(chartId, chartType, containerId, settings = {}) {
        const chartConfig = window.CHART_DEFINITIONS && window.CHART_DEFINITIONS[chartId];
        if (!chartConfig) {
            console.warn(`Chart definition not found for: ${chartId}`);
            return false;
        }
        
        const chartData = this.getChartData(chartId);
        if (!chartData) {
            console.warn(`Chart data not available for: ${chartId}`);
            return false;
        }
        
        const renderFunction = chartConfig.render_function;
        
        if (!window[renderFunction]) {
            console.warn(`Render function not found: ${renderFunction}`);
            return false;
        }
        
        try {
            switch(chartId) {
                case 'monthly_active_users':
                    if (typeof initMonthlyActiveUsersChart === 'function') {
                        initMonthlyActiveUsersChart(chartData, containerId, chartType || 'bar');
                    }
                    break;
                    
                case 'users_by_origin_country':
                    if (typeof initUsersByOriginChart === 'function') {
                        initUsersByOriginChart(chartData, containerId, chartType || 'bar');
                    }
                    break;
                    
                case 'users_by_gender':
                    if (typeof initUsersByGenderChart === 'function') {
                        initUsersByGenderChart(chartData, containerId, chartType || 'pie');
                    }
                    break;
                    
                case 'users_by_destination_country':
                    if (typeof initUsersByDestinationChart === 'function') {
                        initUsersByDestinationChart(chartData, containerId, chartType || 'pie');
                    }
                    break;
                    
                case 'users_by_language':
                    if (typeof initUsersByLanguageChart === 'function') {
                        initUsersByLanguageChart(chartData, containerId, chartType || 'bar');
                    }
                    break;
                    
                case 'users_by_country_state':
                    if (typeof initUsersByStateChart === 'function') {
                        initUsersByStateChart(chartData, containerId, chartType || 'bar');
                    }
                    break;
                    
                case 'users_by_immigration_status':
                    if (typeof initUsersByImmigrationStatusChart === 'function') {
                        initUsersByImmigrationStatusChart(chartData, containerId, chartType || 'bar');
                    }
                    break;
                    
                case 'users_by_age':
                    if (typeof initUsersByAgeChart === 'function') {
                        initUsersByAgeChart(chartData, containerId, chartType || 'pie');
                    }
                    break;
                    
                case 'users_by_sector':
                    if (typeof initUsersBySectorChart === 'function') {
                        initUsersBySectorChart(chartData, containerId, chartType || 'bar');
                    }
                    break;
                    
                case 'work_code_usage':
                    if (typeof initWorkCodeUsageChart === 'function') {
                        initWorkCodeUsageChart(chartData, containerId);
                    }
                    break;
                    
                case 'new_monthly_users':
                    if (typeof initPreferencesMonthlyUsersChart === 'function') {
                        const monthlyData = window.preferenceMonthlyUsersChartData;
                        const activeData = window.monthlyActiveUserCountData;
                        initPreferencesMonthlyUsersChart(monthlyData, activeData, containerId);
                    }
                    break;
                    
                case 'link_clicks':
                    if (typeof linkClicksGraph === 'function') {
                        linkClicksGraph(chartData);
                    }
                    break;
                    
                case 'user_route_map':
                    if (typeof createUserRouteMap === 'function') {
                        const routeData = window.getUserCountsByOriginDestination;
                        const coords = window.countryCoords;
                        if (routeData && coords) {
                            createUserRouteMap(routeData, containerId, coords);
                        }
                    }
                    break;
                    
                case 'user_geolocation_map':
                    if (typeof createUserGeolocationMap === 'function') {
                        const geoData = window.userGeoCountryData;
                        createUserGeolocationMap(geoData, containerId);
                    }
                    break;
                    
                case 'user_geolocation_map_user_engagement':
                    if (typeof createUserGeolocationMap === 'function') {
                        const geoData = window.getUserCountsByGeolocation;
                        createUserGeolocationMap(geoData, containerId);
                    }
                    break;
                    
                default:
                    console.warn(`Chart rendering not implemented for: ${chartId}`);
                    return false;
            }
            
            return true;
        } catch (error) {
            console.error(`Error rendering chart ${chartId}:`, error);
            return false;
        }
    },
    
    getChartData(chartId) {
        const dataMap = {
            'monthly_active_users': window.monthlyActiveUserCountData,
            'users_by_origin_country': window.originData,
            'users_by_gender': window.genderData,
            'users_by_destination_country': window.destinationData,
            'users_by_language': window.languageData,
            'users_by_country_state': window.usersByCountryStateChartData,
            'users_by_immigration_status': window.immigrationStatusData,
            'users_by_age': window.ageData,
            'users_by_sector': window.usersBySectorsChartData,
            'work_code_usage': window.swsWorkcodesWithAccessCode,
            'new_monthly_users': window.preferenceMonthlyUsersChartData,
            'link_clicks': window.linkClicksData,
            'user_route_map': window.getUserCountsByOriginDestination,
            'user_geolocation_map': window.userGeoCountryData,
            'user_geolocation_map_user_engagement': window.getUserCountsByGeolocation
        };
        
        let data = dataMap[chartId];
        
        if (!data) {
            const chartConfig = window.CHART_DEFINITIONS && window.CHART_DEFINITIONS[chartId];
            if (chartConfig && chartConfig.data_variable) {
                const dataVarName = chartConfig.data_variable;
                if (window[dataVarName]) {
                    data = window[dataVarName];
                } else {
                    console.warn(`Chart data not found for ${chartId}. Tried window.${dataVarName} but it's undefined.`);
                }
            } else {
                console.warn(`Chart data not found for ${chartId} and no data_variable in chart definition.`);
            }
        }
        
        return data;
    },
    
    destroyChart(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        if (typeof echarts !== 'undefined' && echarts.getInstanceByDom) {
            const echartsInstance = echarts.getInstanceByDom(container);
            if (echartsInstance) {
                echartsInstance.dispose();
                console.log(`Destroyed ECharts instance for: ${containerId}`);
            }
        }
        
        const canvas = container.querySelector('canvas');
        if (canvas && window.Chart && window.Chart.getChart) {
            const chartInstance = window.Chart.getChart(canvas.id);
            if (chartInstance) {
                chartInstance.destroy();
                console.log(`Destroyed Chart.js instance for: ${canvas.id}`);
            }
        }
        
        if (window.chartInstances && window.chartInstances[containerId]) {
            const chartInstance = window.chartInstances[containerId];
            if (chartInstance && typeof chartInstance.destroy === 'function') {
                chartInstance.destroy();
                delete window.chartInstances[containerId];
                console.log(`Destroyed chart instance from window.chartInstances for: ${containerId}`);
            }
        }
        
        container.innerHTML = '';
    }
};

window.ChartRenderer = ChartRenderer;

