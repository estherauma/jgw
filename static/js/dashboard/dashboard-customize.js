/**
 * Dashboard Customizer
 */

class DashboardCustomizer {
    constructor() {
        this.isCustomizing = false;
        this.layout = null;
        this.sortableInstances = [];
        this.selectedChart = null;
        this.selectedChartElement = null;
        this.selectedChartUniqueId = null;
        this.chartDefinitions = {};
        this.availableCharts = [];
        this.sidebarResizeTimeout = null;
    }
    
    async init() {
        this.setupEventListeners();
        await this.loadLayout(true);

        if (this.chartDefinitions && Object.keys(this.chartDefinitions).length > 0) {
            window.chartDefinitions = this.chartDefinitions;
        } else {
            console.warn('Chart definitions not loaded on init');
        }
        
        if (typeof window.chartSettings === 'undefined') {
            window.chartSettings = {};
        }
        
        setTimeout(() => {
            this.applySpacingToAllCharts();
        }, 100);
        this.setupSidebarResizeListeners();
    }
    
    setupSidebarResizeListeners() {
        const sidebar = document.querySelector('.enhanced-sidebar, .left-side-menu');
        const content = document.querySelector('.enhanced-content');
        
        if (!sidebar) {
            return;
        }
        
        this.ensureChartContainersWidth();
        
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    clearTimeout(this.sidebarResizeTimeout);
                    this.sidebarResizeTimeout = setTimeout(() => {
                        this.ensureChartContainersWidth();
                        this.resizeAllCharts();
                    }, 100);
                }
            });
        });
        
        observer.observe(sidebar, {
            attributes: true,
            attributeFilter: ['class']
        });
        
        if (content) {
            observer.observe(content, {
                attributes: true,
                attributeFilter: ['class']
            });
        }
        
        sidebar.addEventListener('mouseenter', () => {
            clearTimeout(this.sidebarResizeTimeout);
            this.sidebarResizeTimeout = setTimeout(() => {
                this.ensureChartContainersWidth();
                this.resizeAllCharts();
            }, 350);
        });
        
        sidebar.addEventListener('mouseleave', () => {
            clearTimeout(this.sidebarResizeTimeout);
            this.sidebarResizeTimeout = setTimeout(() => {
                this.ensureChartContainersWidth();
                this.resizeAllCharts();
            }, 300);
        });
        
        window.addEventListener('resize', () => {
            clearTimeout(this.sidebarResizeTimeout);
            this.sidebarResizeTimeout = setTimeout(() => {
                this.ensureChartContainersWidth();
                this.resizeAllCharts();
            }, 150);
        });
        
        const sidebarToggle = document.querySelector('[data-bs-toggle="collapse"]');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('shown.bs.collapse', () => {
                setTimeout(() => {
                    this.ensureChartContainersWidth();
                    this.resizeAllCharts();
                }, 100);
            });
            sidebarToggle.addEventListener('hidden.bs.collapse', () => {
                setTimeout(() => {
                    this.ensureChartContainersWidth();
                    this.resizeAllCharts();
                }, 100);
            });
        }
    }
    
    ensureChartContainersWidth() {
        const chartContainers = document.querySelectorAll('[id*="-graph-id"], [id*="-chart-id"], [id="user_route_map"], [id="user_geolocation_map"], [id="user_geolocation_map_user_engagement"], [id="link-clicks-graph-id"]');
        
        chartContainers.forEach(container => {
            if (!container || !container.id) return;
            
            if (!container.style.width || !container.style.width.includes('%')) {
                container.style.width = '100%';
            }
            container.style.maxWidth = '100%';
            container.style.boxSizing = 'border-box';
        });
    }
    
    resizeAllCharts() {
        const chartContainers = document.querySelectorAll('[id*="-graph-id"], [id*="-chart-id"], [id="user_route_map"], [id="user_geolocation_map"], [id="user_geolocation_map_user_engagement"], [id="link-clicks-graph-id"]');
        
        chartContainers.forEach(container => {
            if (!container || !container.id) return;
            
            if (container.style.width && !container.style.width.includes('%')) {
                container.style.width = '100%';
            } else if (!container.style.width) {
                container.style.width = '100%';
            }
            
            if (typeof echarts !== 'undefined' && echarts.getInstanceByDom) {
                try {
                    const echartsInstance = echarts.getInstanceByDom(container);
                    if (echartsInstance && typeof echartsInstance.resize === 'function') {
                        echartsInstance.resize();
                    }
                } catch (error) {
                    console.warn(`Error resizing ECharts instance for ${container.id}:`, error);
                }
            }
            
            try {
                const canvas = container.querySelector('canvas');
                if (canvas && window.Chart && window.Chart.getChart) {
                    const chartInstance = window.Chart.getChart(canvas.id || canvas);
                    if (chartInstance && typeof chartInstance.resize === 'function') {
                        chartInstance.resize();
                    }
                }
            } catch (error) {
                console.warn(`Error resizing Chart.js instance for ${container.id}:`, error);
            }
            
            if (window.chartInstances && window.chartInstances[container.id]) {
                try {
                    const chartInstance = window.chartInstances[container.id];
                    if (chartInstance && typeof chartInstance.resize === 'function') {
                        chartInstance.resize();
                    }
                } catch (error) {
                    console.warn(`Error resizing chart instance from window.chartInstances for ${container.id}:`, error);
                }
            }
        });
        
        window.dispatchEvent(new Event('resize'));
    }
    
    setupEventListeners() {
        const customizeBtn = document.getElementById('customize-dashboard-btn');
        if (customizeBtn) {
            customizeBtn.addEventListener('click', () => this.enterCustomizeMode());
        }
        
        const addRowBtn = document.getElementById('add-row-btn');
        if (addRowBtn) {
            addRowBtn.addEventListener('click', () => this.addNewRow());
        }
        
        const addChartBtn = document.getElementById('add-chart-btn');
        if (addChartBtn) {
            addChartBtn.addEventListener('click', () => this.showChartLibrary());
        }
        
        const saveBtn = document.getElementById('save-dashboard-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveLayout());
        }
        
        const resetBtn = document.getElementById('reset-dashboard-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetDashboard());
        }
        
        const exitBtn = document.getElementById('exit-customize-btn');
        if (exitBtn) {
            exitBtn.addEventListener('click', () => this.exitCustomizeMode());
        }
        
        const previewBtn = document.getElementById('preview-dashboard-btn');
        if (previewBtn) {
            previewBtn.addEventListener('click', () => this.togglePreview());
        }
    }
    
    async loadLayout(isInitialLoad = false) {
        try {
            const response = await fetch('/preference/api/dashboard/customize/');
            
            if (!response.ok) {
                console.error(`API response not OK: ${response.status} ${response.statusText}`);
                throw new Error(`API request failed: ${response.status}`);
            }
            
            const data = await response.json();
            
            this.layout = data.layout || { rows: [] };
            this.chartDefinitions = data.chart_definitions || {};
            this.availableCharts = data.available_charts || [];
            
            if (this.chartDefinitions && Object.keys(this.chartDefinitions).length > 0) {
                window.chartDefinitions = this.chartDefinitions;
            } else {
                console.warn('⚠ No chart definitions received from API!');
            }
            
            if (data.chart_settings) {
                window.chartSettings = data.chart_settings;
            }

            const hasCustomLayout = this.layout && this.layout.rows && this.layout.rows.length > 0;
            
            if (isInitialLoad) {
                if (!hasCustomLayout) {
                    this.layout = this.extractLayoutFromDOM();
                }
                return;
            }
            
            if (!this.isCustomizing && hasCustomLayout) {
                this.renderLayout();
            } else if (!hasCustomLayout) {
                this.layout = this.extractLayoutFromDOM();
            }
        } catch (error) {
            console.error('Error loading dashboard layout:', error);
            if (!isInitialLoad) {
                this.layout = this.extractLayoutFromDOM();
            }
        }
    }
    
    async enterCustomizeMode() {
        this.isCustomizing = true;
        document.body.classList.add('dashboard-customize-mode');
        
        const toolbar = document.getElementById('dashboard-toolbar');
        if (toolbar) {
            toolbar.style.display = 'flex';
        }
        
        if (!this.chartDefinitions || Object.keys(this.chartDefinitions).length === 0) {
            await this.loadLayout(false);
        }
        
        if (!window.chartDefinitions || Object.keys(window.chartDefinitions).length === 0) {
            if (this.chartDefinitions && Object.keys(this.chartDefinitions).length > 0) {
                window.chartDefinitions = this.chartDefinitions;
            }
        }
        
        if (!this.layout || !this.layout.rows || this.layout.rows.length === 0) {
            this.layout = this.extractLayoutFromDOM();
        }
        
        this.addCustomizationControls();
        this.initializeDragAndDrop();
        
        setTimeout(() => {
            this.applySpacingToAllCharts();
        }, 100);
        
        this.showNotification('Customization mode enabled', 'info');
    }
    
    exitCustomizeMode() {
        if (!confirm('Exit customization mode? Unsaved changes will be lost.')) {
            return;
        }
        
        this.isCustomizing = false;
        document.body.classList.remove('dashboard-customize-mode');
        
        const toolbar = document.getElementById('dashboard-toolbar');
        if (toolbar) {
            toolbar.style.display = 'none';
        }
        
        this.removeCustomizationControls();
        this.destroyDragAndDrop();
        
        this.loadLayout(false).then(() => {
            const hasCustomLayout = this.layout && this.layout.rows && this.layout.rows.length > 0;
            if (hasCustomLayout) {
                this.renderLayout();
            }
        });
    }
    
    addCustomizationControls() {
        document.querySelectorAll('.dashboard-row').forEach((row, index) => {
            if (!row.querySelector('.row-toolbar')) {
                row.appendChild(this.createRowToolbar(row, index));
            }
            if (!row.querySelector('.row-number-badge')) {
                const badge = document.createElement('div');
                badge.className = 'row-number-badge';
                badge.textContent = index + 1;
                row.appendChild(badge);
            }
        });
        
        document.querySelectorAll('.dashboard-row').forEach(row => {
            row.querySelectorAll('.dashboard-chart').forEach(chart => {
                const parentChart = chart.parentElement.closest('.dashboard-chart');
                if (parentChart && parentChart !== chart) {
                    return;
                }
                
                if (chart.querySelector('.chart-toolbar')) {
                    return;
                }
                
                const chartElementWithId = chart.querySelector('[data-chart-id]') || chart;
                
                chart.appendChild(this.createChartToolbar(chartElementWithId));
            });
        });
        
        document.querySelectorAll('.dashboard-row .card').forEach(card => {
            if (card.closest('.dashboard-chart')) return;
            
            if (card.querySelector('.dashboard-chart')) return;
            
            const chartId = this.detectChartId(card);
            if (chartId) {
                const wrapper = document.createElement('div');
                wrapper.className = 'dashboard-chart';
                wrapper.dataset.chartId = chartId;
                card.parentNode.insertBefore(wrapper, card);
                wrapper.appendChild(card);
                
                if (!wrapper.querySelector('.chart-toolbar')) {
                    wrapper.appendChild(this.createChartToolbar(wrapper));
                }
            }
        });
    }
    
    detectChartId(card) {
        const chartSelectors = [
            '#monthly-active-users-graph-id',
            '#preference-origin-graph-id',
            '#preference-gender-chart-id',
            '#preference-destination-chart-id',
            '#preference-language-graph-id',
            '#users-by-country-state-graph-id',
            '#preference-immigration-status-chart-id',
            '#preference-age-chart-id',
            '#users-by-sector-graph-id',
            '#organisation-work-code-usage-graph-id',
            '#preference-monthly-cumulative-users-graph-id',
            '#link-clicks-graph-id'
        ];
        
        for (const selector of chartSelectors) {
            if (card.querySelector(selector)) {
                return selector.replace('#', '').replace('-graph-id', '').replace('-chart-id', '');
            }
        }
        
        if (card.dataset.chartId) return card.dataset.chartId;
        if (card.id) {
            const idMatch = card.id.match(/(\w+)-(card|chart)/);
            if (idMatch) return idMatch[1];
        }
        
        return null;
    }
    
    removeCustomizationControls() {
        document.querySelectorAll('.row-toolbar, .chart-toolbar, .row-number-badge').forEach(ctrl => {
            ctrl.remove();
        });
    }
    
    createRowToolbar(rowElement, rowIndex) {
        const toolbar = document.createElement('div');
        toolbar.className = 'row-toolbar';
        const rowId = rowElement.dataset.rowId || `row-${rowIndex}`;
        toolbar.innerHTML = `
            <span class="row-toolbar-label">Row ${rowIndex + 1}</span>
            <button class="row-toolbar-btn drag-handle" title="Drag Row" onclick="event.stopPropagation();">
                <i class="fe-move"></i>
            </button>
            <button class="row-toolbar-btn" title="Add Column" onclick="event.stopPropagation(); dashboardCustomizer.addColumnToRow(this);">
                <i class="fe-plus"></i>
            </button>
            <button class="row-toolbar-btn" title="Delete Row" onclick="event.stopPropagation(); dashboardCustomizer.deleteRow(this);">
                <i class="fe-trash"></i>
            </button>
        `;
        return toolbar;
    }
    
    createChartToolbar(chartElement) {
        const toolbar = document.createElement('div');
        toolbar.className = 'chart-toolbar';
        
        let chartId = chartElement.dataset.chartId;
        
        if (!chartId) {
            const childWithId = chartElement.querySelector('[data-chart-id]');
            if (childWithId) {
                chartId = childWithId.dataset.chartId;
            }
        }
        
        if (!chartId) {
            const parentWithId = chartElement.closest('[data-chart-id]');
            if (parentWithId) {
                chartId = parentWithId.dataset.chartId;
            }
        }
        
        if (!chartId) {
            if (chartElement.id && chartElement.id.startsWith('chart-')) {
                chartId = chartElement.id.replace('chart-', '');
            } else {
                chartId = this.detectChartId(chartElement);
            }
        }
        
        let chartName = 'Chart';
        
        if (chartId && this.chartDefinitions && this.chartDefinitions[chartId]) {
            chartName = this.chartDefinitions[chartId].name;
        }
        else if (chartId && window.chartDefinitions && window.chartDefinitions[chartId]) {
            chartName = window.chartDefinitions[chartId].name;
        }
        else if (chartElement) {
            const titleElement = chartElement.querySelector('.chart-main-title, .chart-title, h4');
            if (titleElement) {
                chartName = titleElement.textContent.trim();
            }
        }
        if (chartName === 'Chart' && chartId) {
            chartName = chartId.replace(/_/g, ' ')
                .replace(/\b\w/g, l => l.toUpperCase())
                .replace(/\bUsers\b/g, 'Users')
                .replace(/\bBy\b/g, 'by');
        }
        
        if (!chartId) {
            console.warn('Could not determine chart ID for element:', chartElement);
            chartId = 'unknown';
        }
        
        toolbar.innerHTML = `
            <span class="chart-toolbar-label" title="${chartName}">${chartName}</span>
            <button class="chart-toolbar-btn drag-handle" title="Drag Chart" onclick="event.stopPropagation();">
                <i class="fe-move"></i>
            </button>
            <button class="chart-toolbar-btn edit-btn" title="Edit Chart" onclick="event.stopPropagation(); dashboardCustomizer.editChartFromButton(this);">
                <i class="fe-edit"></i>
            </button>
            <button class="chart-toolbar-btn duplicate-btn" title="Duplicate Chart" onclick="event.stopPropagation(); dashboardCustomizer.duplicateChart('${chartId}');">
                <i class="fe-copy"></i>
            </button>
            <button class="chart-toolbar-btn remove-btn" title="Remove Chart" onclick="event.stopPropagation(); dashboardCustomizer.removeChartFromButton(this);">
                <i class="fe-x"></i>
            </button>
        `;
        return toolbar; 
    }
    
    initializeDragAndDrop() {
        const sortableScript = document.createElement('script');
        sortableScript.src = '/static/themes/modern/libs/sortablejs/Sortable.min.js';
        sortableScript.onload = () => {
            this.setupRowSortable();
            this.setupChartSortable();
        };
        
        if (window.Sortable) {
            this.setupRowSortable();
            this.setupChartSortable();
        } else {
            document.head.appendChild(sortableScript);
        }
    }
    
    setupRowSortable() {
        const rowsContainer = document.getElementById('dashboard-rows-container');
        if (!rowsContainer || !window.Sortable) return;
        
        if (this.sortableInstances['rows']) {
            this.sortableInstances['rows'].destroy();
        }
        
        this.sortableInstances['rows'] = new Sortable(rowsContainer, {
            animation: 150,
            handle: '.row-toolbar .drag-handle',
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            onEnd: () => {
                this.saveLayout();
            }
        });
    }
    
    setupChartSortable() {
        if (!window.Sortable) return;
        
        document.querySelectorAll('.dashboard-row').forEach((row, rowIndex) => {
            let columnsContainer = row.querySelector('.row:not(.dashboard-row)');
            
            if (!columnsContainer && row.classList.contains('row')) {
                columnsContainer = row;
            }
            
            if (!columnsContainer) {
                console.warn('No columns container found for row:', row);
                return;
            }
            
            const instanceKey = `chart-row-${rowIndex}`;
            
            if (this.sortableInstances[instanceKey]) {
                this.sortableInstances[instanceKey].destroy();
            }
            
            const draggableSelector = row === columnsContainer 
                ? '[class*="col-md-"]' 
                : null;
            
            this.sortableInstances[instanceKey] = new Sortable(columnsContainer, {
                animation: 150,
                handle: '.chart-toolbar .drag-handle',
                group: 'charts',
                ghostClass: 'sortable-ghost',
                chosenClass: 'sortable-chosen',
                dragClass: 'sortable-drag',
                draggable: draggableSelector,
                filter: '.row-toolbar, .row-number-badge',
                onEnd: () => {
                    this.updateColumnSizes();
                    this.saveLayout();
                }
            });
        });
    }
    
    destroyDragAndDrop() {
        Object.values(this.sortableInstances).forEach(instance => {
            if (instance && instance.destroy) {
                instance.destroy();
            }
        });
        this.sortableInstances = [];
    }
    
    renderLayout() {
        const container = document.getElementById('dashboard-rows-container');
        if (!container) return;
        
        const hasExistingCharts = container.querySelectorAll('.dashboard-chart, .card').length > 0;
        if (!this.isCustomizing && !hasExistingCharts) {
            container.innerHTML = '';
        } else if (!this.isCustomizing && hasExistingCharts) {
            console.log('Charts already rendered, skipping layout render');
            return;
        } else if (this.isCustomizing) {
            container.innerHTML = '';
        }
        
        if (!this.layout || !this.layout.rows || this.layout.rows.length === 0) {
            return;
        }
        
        this.layout.rows.forEach((rowData, rowIndex) => {
            const rowEl = this.createRowElement(rowData, rowIndex);
            container.appendChild(rowEl);
        });
        
        setTimeout(() => {
            this.applySpacingToAllCharts();
        }, 50);
        
        setTimeout(() => {
            this.renderAllCharts();
        }, 100);
    }
    
    applySpacingToAllCharts() {
        document.querySelectorAll('.dashboard-row').forEach(row => {
            const columns = row.querySelectorAll('[class*="col-md-"]');
            let totalSize = 0;
            columns.forEach(col => {
                const colSize = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '0');
                totalSize += colSize;
            });
            
            columns.forEach(col => {
                const size = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '6');
                this.updateChartSpacing(col, size);
            });
        });
    }
    
    createRowElement(rowData, rowIndex) {
        const row = document.createElement('div');
        row.className = 'dashboard-row';
        row.dataset.rowId = rowData.id || `row-${rowIndex}`;
        
        row.appendChild(this.createRowToolbar(row, rowIndex));
        const badge = document.createElement('div');
        badge.className = 'row-number-badge';
        badge.textContent = rowIndex + 1;
        row.appendChild(badge);
        
        const columnsContainer = document.createElement('div');
        columnsContainer.className = 'row';
        
        if (rowData.columns && rowData.columns.length > 0) {
            rowData.columns.forEach((colData, colIndex) => {
                const colEl = this.createColumnElement(colData, colIndex);
                columnsContainer.appendChild(colEl);
            });
        }
        
        row.appendChild(columnsContainer);
        return row;
    }
    
    createColumnElement(colData, colIndex) {
        const col = document.createElement('div');
        const colSize = colData.size || 6;
        col.className = `col-md-${colSize}`;
        col.dataset.columnId = colData.id || `col-${colIndex}`;
        
        this.updateChartSpacing(col, colSize);
        
        const card = document.createElement('div');
        card.className = 'card h-100';
        
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body dashboard-chart';
        
        const chartContainer = document.createElement('div');
        chartContainer.className = 'dashboard-chart';
        chartContainer.dataset.chartId = colData.chart_id;
        
        const chartWrapper = document.createElement('div');
        chartWrapper.dataset.chartId = colData.chart_id;
        chartWrapper.id = `chart-${colData.chart_id}`;
        
        const chartDef = this.chartDefinitions[colData.chart_id] || window.chartDefinitions?.[colData.chart_id];
        const chartName = chartDef ? chartDef.name : colData.chart_id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        const chartHeader = document.createElement('div');
        chartHeader.className = 'chart-header';
        chartHeader.innerHTML = `
            <div class="chart-header-left">
                <h4 class="chart-main-title">${chartName}</h4>
            </div>
        `;
        chartWrapper.appendChild(chartHeader);
        
        const graphContainerId = this.getGraphContainerId(colData.chart_id);
        if (graphContainerId) {
            const graphContainer = document.createElement('div');
            graphContainer.id = graphContainerId;
            graphContainer.style.height = '500px';
            graphContainer.style.width = '100%';
            graphContainer.style.maxWidth = '100%';
            graphContainer.style.boxSizing = 'border-box';
            chartWrapper.appendChild(graphContainer);
        }
        
        chartWrapper.appendChild(this.createChartToolbar(chartWrapper));
        
        chartContainer.appendChild(chartWrapper);
        cardBody.appendChild(chartContainer);
        card.appendChild(cardBody);
        col.appendChild(card);
        
        return col;
    }
    
    renderAllCharts() {
        if (!this.layout || !this.layout.rows) return;
        
        this.layout.rows.forEach(row => {
            if (row.columns) {
                row.columns.forEach(col => {
                    if (col.enabled !== false && col.chart_id) {
                        const settings = col.settings || {};
                        const containerId = `chart-${col.chart_id}`;
                        
                        const container = document.getElementById(containerId);
                        if (!container) {
                            console.warn(`Chart container not found: ${containerId}`);
                            return;
                        }
                        
                        if (window.ChartRenderer) {
                            window.ChartRenderer.destroyChart(containerId);
                        }
                        
                        setTimeout(() => {
                            if (window.ChartRenderer) {
                                const success = window.ChartRenderer.renderChart(
                                    col.chart_id,
                                    settings.chart_type || this.chartDefinitions[col.chart_id]?.default_type || 'bar',
                                    containerId,
                                    settings
                                );
                                if (!success) {
                                    console.warn(`Failed to render chart: ${col.chart_id}`);
                                }
                            }
                        }, 100);
                    }
                });
            }
        });
    }
    
    extractLayoutFromDOM() {
        const rows = [];
        const rowsContainer = document.getElementById('dashboard-rows-container');
        
        if (!rowsContainer) {
            document.querySelectorAll('.dashboard-row').forEach((rowEl, rowIndex) => {
                const row = { id: rowEl.dataset.rowId || `row-${rowIndex}`, columns: [] };
                
                rowEl.querySelectorAll('[class*="col-md-"]').forEach((colEl) => {
                    const chartEl = colEl.querySelector('.dashboard-chart');
                    if (chartEl) {
                        const chartId = chartEl.dataset.chartId;
                        if (chartId) {
                            const size = parseInt(colEl.className.match(/col-md-(\d+)/)?.[1] || '6');
                            
                            row.columns.push({
                                id: chartEl.id || `col-${chartId}-${rowIndex}`,
                                chart_id: chartId,
                                size: size,
                                enabled: true,
                                settings: {}
                            });
                        }
                    }
                });
                
                if (row.columns.length > 0) {
                    rows.push(row);
                }
            });
        } else {
            rowsContainer.querySelectorAll('.dashboard-row').forEach((rowEl, rowIndex) => {
                const row = { id: rowEl.dataset.rowId || `row-${rowIndex}`, columns: [] };
                
                rowEl.querySelectorAll('[class*="col-md-"]').forEach((colEl) => {
                    const chartEl = colEl.querySelector('.dashboard-chart');
                    if (chartEl) {
                        const chartId = chartEl.dataset.chartId;
                        if (chartId) {
                            const size = parseInt(colEl.className.match(/col-md-(\d+)/)?.[1] || '6');
                            
                            row.columns.push({
                                id: chartEl.id || `col-${chartId}-${rowIndex}`,
                                chart_id: chartId,
                                size: size,
                                enabled: true,
                                settings: {}
                            });
                        }
                    }
                });
                
                if (row.columns.length > 0) {
                    rows.push(row);
                }
            });
        }
        
        return { rows };
    }
    
        detectChartId(element) {
        const id = element.id || '';
        const classList = element.className || '';
        
        const patterns = [
            { pattern: /monthly.*active.*user/i, id: 'monthly_active_users' },
            { pattern: /origin.*country|origin.*graph/i, id: 'users_by_origin_country' },
            { pattern: /gender|gender.*chart/i, id: 'users_by_gender' },
            { pattern: /destination.*country|destination.*graph/i, id: 'users_by_destination_country' },
            { pattern: /language|language.*graph/i, id: 'users_by_language' },
            { pattern: /country.*state|state.*graph/i, id: 'users_by_country_state' },
            { pattern: /immigration.*status/i, id: 'users_by_immigration_status' },
            { pattern: /age|age.*chart/i, id: 'users_by_age' },
            { pattern: /sector|sector.*graph/i, id: 'users_by_sector' },
            { pattern: /work.*code.*usage/i, id: 'work_code_usage' },
            { pattern: /monthly.*user|new.*user/i, id: 'new_monthly_users' },
            { pattern: /link.*click/i, id: 'link_clicks' },
            { pattern: /route.*map/i, id: 'user_route_map' },
            { pattern: /geolocation.*map/i, id: 'user_geolocation_map' }
        ];
        
        for (const { pattern, id } of patterns) {
            if (pattern.test(id + ' ' + classList)) {
                return id;
            }
        }
        
        return null;
    }
    
    async saveLayout() {
        const layout = this.extractLayoutFromDOM();
        
        if (window.chartSettings && layout && layout.rows) {
            layout.rows.forEach(row => {
                if (row.columns) {
                    row.columns.forEach(col => {
                        if (col.chart_id && window.chartSettings[col.chart_id]) {
                            const chartSetting = window.chartSettings[col.chart_id];
                            
                            if (chartSetting.size !== undefined) {
                                col.size = chartSetting.size;
                            }
                            
                            if (!col.settings) {
                                col.settings = {};
                            }
                            
                            if (chartSetting.chart_type) {
                                col.settings.chart_type = chartSetting.chart_type;
                            }
                            
                            if (chartSetting.enabled !== undefined) {
                                col.enabled = chartSetting.enabled;
                            }
                            
                            if (chartSetting.start_date !== undefined) {
                                col.settings.start_date = chartSetting.start_date;
                            }
                            
                            if (chartSetting.end_date !== undefined) {
                                col.settings.end_date = chartSetting.end_date;
                            }
                        }
                    });
                }
            });
        }
        
        try {
            const response = await fetch('/preference/api/dashboard/customize/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ layout })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.layout = layout;
                this.showNotification('Dashboard layout saved successfully!', 'success');
            } else {
                this.showNotification('Error saving layout: ' + (data.message || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Error saving layout:', error);
            this.showNotification('Error saving layout. Please try again.', 'error');
        }
    }
    
    async resetDashboard() {
        if (!confirm('Reset dashboard to default layout? This cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch('/preference/api/dashboard/reset/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification('Dashboard reset to default', 'success');
                this.loadLayout().then(() => {
                    this.renderLayout();
                    if (this.isCustomizing) {
                        this.addCustomizationControls();
                        this.initializeDragAndDrop();
                    }
                });
            } else {
                this.showNotification('Error resetting dashboard', 'error');
            }
        } catch (error) {
            console.error('Error resetting dashboard:', error);
            this.showNotification('Error resetting dashboard. Please try again.', 'error');
        }
    }
    
    addNewRow() {
        const container = document.getElementById('dashboard-rows-container');
        if (!container) return;
        
        const newRow = {
            id: `row-${Date.now()}`,
            columns: []
        };
        
        if (!this.layout) this.layout = { rows: [] };
        if (!this.layout.rows) this.layout.rows = [];
        this.layout.rows.push(newRow);
        
        const rowEl = this.createRowElement(newRow, this.layout.rows.length - 1);
        container.appendChild(rowEl);
        
        this.setupRowSortable();
        this.setupChartSortable();
    }
    
    addColumnToRow(button) {
        this.showChartLibrary(button);
    }
    
    async showChartLibrary(button = null) {
        const modal = document.getElementById('chart-library-modal');
        if (!modal) {
            console.error('Chart library modal not found');
            return;
        }
        
        if (!this.chartDefinitions || Object.keys(this.chartDefinitions).length === 0) {
            console.log('Loading chart definitions for chart library...');
            await this.loadLayout(false);
        }
        
        const chartsToShow = this.availableCharts.length > 0 
            ? this.availableCharts 
            : Object.keys(this.chartDefinitions || window.chartDefinitions || {});
        
        const chartsList = modal.querySelector('.charts-list');
        if (chartsList) {
            chartsList.innerHTML = '';
            
            if (chartsToShow.length === 0) {
                chartsList.innerHTML = '<p class="text-center text-muted">No charts available</p>';
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                return;
            }
            
            chartsToShow.forEach(chartId => {
                const chartDef = this.chartDefinitions[chartId] || window.chartDefinitions?.[chartId];
                if (!chartDef) {
                    console.warn(`Chart definition not found for: ${chartId}`);
                    return;
                }
                
                const chartItem = document.createElement('div');
                chartItem.className = 'chart-library-item';
                chartItem.dataset.chartId = chartId;
                chartItem.innerHTML = `
                    <i class="${chartDef.icon}"></i>
                    <div>
                        <strong>${chartDef.name}</strong>
                        <small>${chartDef.description}</small>
                    </div>
                `;
                chartItem.addEventListener('click', () => {
                    this.addChartToDashboard(chartId, button);
                    const bsModalInstance = bootstrap.Modal.getInstance(modal);
                    if (bsModalInstance) {
                        bsModalInstance.hide();
                    }
                });
                chartsList.appendChild(chartItem);
            });
        }
        
        if (button) {
            modal.dataset.targetButton = 'true';
        }
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    addChartToDashboard(chartId, targetButton = null) {
        console.log(`Adding chart to dashboard: ${chartId}`);
        
        let targetRow = null;
        
        if (targetButton) {
            targetRow = targetButton.closest('.dashboard-row');
        } else {
            const rows = document.querySelectorAll('.dashboard-row');
            targetRow = rows[rows.length - 1] || null;
        }
        
        if (!targetRow) {
            this.addNewRow();
            const rows = document.querySelectorAll('.dashboard-row');
            targetRow = rows[rows.length - 1];
        }
        
        const chartDef = this.chartDefinitions[chartId];
        if (!chartDef) {
            console.error(`Chart definition not found for: ${chartId}`);
            return;
        }
        
        let columnsContainer = targetRow.querySelector('.row:not(.dashboard-row)');
        if (!columnsContainer && targetRow.classList.contains('row')) {
            columnsContainer = targetRow;
        }
        
        if (!columnsContainer) {
            console.error('Columns container not found in target row');
            return;
        }
            
        const existingCharts = document.querySelectorAll(`[data-chart-id="${chartId}"]`);
        const timestamp = Date.now();
        const uniqueId = existingCharts.length > 0 ? `added_${timestamp}` : '';
        
        const baseGraphContainerId = this.getGraphContainerId(chartId);
        const graphContainerId = uniqueId ? `${baseGraphContainerId}-${uniqueId}` : baseGraphContainerId;
        
        const colData = {
            id: `col-${chartId}-${timestamp}`,
            chart_id: chartId,
            size: 6,
            enabled: true,
            settings: {
                chart_type: chartDef.default_type || 'bar'
            }
        };
        
        const colEl = this.createColumnElement(colData, columnsContainer.children.length);
        
        const chartWrapper = colEl.querySelector(`[data-chart-id="${chartId}"]`);
        if (!chartWrapper) {
            console.error('Chart wrapper not found in column element');
            return;
        }
        
        if (uniqueId) {
            chartWrapper.id = `chart-${chartId}-${uniqueId}`;
        }
        
        const existingGraphContainer = chartWrapper.querySelector(`#${baseGraphContainerId}`);
        if (existingGraphContainer) {
            existingGraphContainer.id = graphContainerId;
            console.log(`Updated graph container ID from ${baseGraphContainerId} to ${graphContainerId}`);
        } else {
            const graphContainer = document.createElement('div');
            graphContainer.id = graphContainerId;
            graphContainer.style.height = '500px';
            graphContainer.style.width = '100%';
            
            const chartHeader = chartWrapper.querySelector('.chart-header');
            if (chartHeader) {
                chartHeader.insertAdjacentElement('afterend', graphContainer);
            } else {
                chartWrapper.appendChild(graphContainer);
            }
            console.log(`Created unique graph container: ${graphContainerId}`);
        }
        
        columnsContainer.appendChild(colEl);
        
        this.updateChartSpacing(colEl, 6);
        
        if (!this.layout) this.layout = { rows: [] };
        if (!this.layout.rows) this.layout.rows = [];
        
        const rowId = targetRow.dataset.rowId || `row-${timestamp}`;
        let rowData = this.layout.rows.find(r => r.id === rowId);
        if (!rowData) {
            rowData = { id: rowId, columns: [] };
            this.layout.rows.push(rowData);
        }
        if (!rowData.columns) rowData.columns = [];
        rowData.columns.push(colData);
        
        console.log(`Rendering chart ${chartId} in container: ${graphContainerId}`);
        
        setTimeout(() => {
            if (window.ChartRenderer && graphContainerId) {
                const graphContainer = document.getElementById(graphContainerId);
                if (!graphContainer) {
                    console.error(`Graph container not found: ${graphContainerId}`);
                    return;
                }
                
                const success = window.ChartRenderer.renderChart(
                    chartId,
                    chartDef.default_type || 'bar',
                    graphContainerId,
                    {}
                );
                
                if (!success) {
                    console.error(`Failed to render chart: ${chartId}`);
                } else {
                    console.log(`Successfully rendered chart: ${chartId} in container: ${graphContainerId}`);
                }
            } else {
                console.error(`ChartRenderer not available or graph container ID not found for: ${chartId}`);
            }
        }, 200);
        
        this.setupChartSortable();
        
        setTimeout(() => {
            this.applySpacingToAllCharts();
        }, 100);
        
        this.saveLayout();
        
        this.showNotification(`Chart "${chartDef.name}" added successfully`, 'success');
    }
    
    getChartInfoFromButton(button) {
        const toolbar = button.closest('.chart-toolbar');
        if (!toolbar) {
            console.error('Chart toolbar not found');
            return null;
        }
        
        const dashboardChart = toolbar.closest('.dashboard-chart');
        if (!dashboardChart) {
            console.error('Dashboard chart container not found');
            return null;
        }
        
        let chartWrapper = null;
        
        if (dashboardChart.dataset && dashboardChart.dataset.chartId) {
            chartWrapper = dashboardChart;
        } else {
            chartWrapper = dashboardChart.querySelector('[data-chart-id]');
        }
        
        if (!chartWrapper) {
            console.error('Chart wrapper with data-chart-id not found in dashboard-chart container');
            return null;
        }
        
        const chartId = chartWrapper.dataset.chartId;
        if (!chartId) {
            console.error('Chart ID not found in wrapper:', chartWrapper);
            return null;
        }
        
        const uniqueId = chartWrapper.id || null;
        
        return {
            chartId: chartId,
            chartWrapper: chartWrapper,
            uniqueId: uniqueId
        };
    }
    
    editChartFromButton(button) {
        const chartInfo = this.getChartInfoFromButton(button);
        if (!chartInfo) {
            return;
        }
        
        this.editChart(chartInfo.chartId, chartInfo.chartWrapper, chartInfo.uniqueId);
    }
    
    editChart(chartId, chartElement = null, uniqueId = null) {
        console.log(`Editing chart: ${chartId}, uniqueId: ${uniqueId}`);
        this.selectedChart = chartId;
        this.selectedChartElement = chartElement;
        this.selectedChartUniqueId = uniqueId;
        
        if (!this.chartDefinitions || Object.keys(this.chartDefinitions).length === 0) {
            console.warn('Chart definitions not loaded, attempting to load...');
            this.loadLayout(false).then(() => {
                this.showChartSettingsModal(chartId, chartElement, uniqueId);
            });
            return;
        }
        
        this.showChartSettingsModal(chartId, chartElement, uniqueId);
    }
    
    async showChartSettingsModal(chartId, chartElement = null, uniqueId = null) {
        console.log(`showChartSettingsModal called for: ${chartId}, uniqueId: ${uniqueId}`);
        const modal = document.getElementById('chart-settings-modal');
        if (!modal) {
            console.error('Chart settings modal not found in DOM');
            return;
        }
        
        if (!chartId) {
            console.error('Chart ID is required');
            alert('Chart ID is required to open settings');
            return;
        }
        
        const loadingDiv = modal.querySelector('#chart-settings-loading');
        const formDiv = modal.querySelector('#chart-settings-form');
        if (loadingDiv) loadingDiv.style.display = 'block';
        if (formDiv) formDiv.style.display = 'none';
        
        let chartDef = null;
        let currentSettings = null;
        
        try {
            const response = await fetch(`/preference/api/chart-settings/${chartId}/`);
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success') {
                    chartDef = data.chart_definition;
                    currentSettings = data.settings;
                    
                    if (!window.chartSettings) window.chartSettings = {};
                    window.chartSettings[chartId] = currentSettings;
                    
                    if (chartDef && (!window.chartDefinitions || !window.chartDefinitions[chartId])) {
                        if (!window.chartDefinitions) window.chartDefinitions = {};
                        window.chartDefinitions[chartId] = chartDef;
                    }
                } else {
                    console.error('API returned error:', data.message);
                    alert(`Error loading chart settings: ${data.message || 'Unknown error'}`);
                    if (loadingDiv) loadingDiv.style.display = 'none';
                    return;
                }
            } else if (response.status === 403) {
                const errorData = await response.json();
                alert(`Error: ${errorData.message || 'Chart not available'}`);
                if (loadingDiv) loadingDiv.style.display = 'none';
                return;
            } else {
                console.error(`API request failed with status: ${response.status}`);
                alert('Error loading chart settings. Please try again.');
                if (loadingDiv) loadingDiv.style.display = 'none';
                return;
            }
        } catch (error) {
            console.error('Error fetching chart settings:', error);
            alert('Error loading chart settings. Please try again.');
            if (loadingDiv) loadingDiv.style.display = 'none';
            return;
        }
        
        if (!chartDef) {
            chartDef = this.chartDefinitions?.[chartId] || window.chartDefinitions?.[chartId];
            if (!chartDef) {
                console.warn(`Chart definition not found for ${chartId}, attempting to load...`);
                await this.loadLayout(false);
                chartDef = this.chartDefinitions?.[chartId] || window.chartDefinitions?.[chartId];
            }
        }
        
        if (!chartDef) {
            console.error(`Chart definition not found for: ${chartId}`);
            alert(`Chart settings not available for this chart. Please try again.`);
            if (loadingDiv) loadingDiv.style.display = 'none';
            return;
        }
        
        if (!chartElement) {
            if (uniqueId) {
                chartElement = document.getElementById(uniqueId);
            }
            
            if (!chartElement) {
                const allCharts = document.querySelectorAll(`[data-chart-id="${chartId}"]`);
                if (uniqueId) {
                    chartElement = Array.from(allCharts).find(el => {
                        const wrapperId = el.id || '';
                        return wrapperId === uniqueId || wrapperId.includes(uniqueId.split('-').pop());
                    });
                }
                
                if (!chartElement && allCharts.length > 0) {
                    chartElement = allCharts[0];
                }
            }
        }
        
        if (!chartElement) {
            if (uniqueId) {
                chartElement = document.getElementById(uniqueId);
            }
            
            if (!chartElement) {
                const allCharts = document.querySelectorAll(`[data-chart-id="${chartId}"]`);
                if (uniqueId) {
                    chartElement = Array.from(allCharts).find(el => {
                        const wrapperId = el.id || '';
                        return wrapperId === uniqueId || wrapperId.includes(uniqueId.split('-').pop());
                    });
                }
                
                if (!chartElement && allCharts.length > 0) {
                    chartElement = allCharts[0];
                }
            }
        }
        
        const typeSelect = modal.querySelector('#chart-type-select');
        if (typeSelect && chartDef) {
            typeSelect.innerHTML = '';
            if (chartDef.supported_types && Array.isArray(chartDef.supported_types)) {
                chartDef.supported_types.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type;
                    option.textContent = type.charAt(0).toUpperCase() + type.slice(1);
                    typeSelect.appendChild(option);
                });
                
                const chartType = currentSettings?.chart_type || chartDef.default_type || 'bar';
                typeSelect.value = chartType.toLowerCase();
            } else {
                console.warn('supported_types not found in chartDef:', chartDef);
                const commonTypes = ['bar', 'line', 'pie', 'doughnut', 'area', 'map'];
                commonTypes.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type;
                    option.textContent = type.charAt(0).toUpperCase() + type.slice(1);
                    typeSelect.appendChild(option);
                });
                typeSelect.value = currentSettings?.chart_type || 'bar';
            }
        }
        
        const sizeSelect = modal.querySelector('#chart-size-select');
        if (sizeSelect) {
            let currentSize = currentSettings?.size;
            if (!currentSize && chartElement) {
                const colElement = chartElement.closest('[class*="col-md-"]');
                if (colElement) {
                    currentSize = parseInt(colElement.className.match(/col-md-(\d+)/)?.[1] || '6');
                }
            }
            if (!currentSize) {
                currentSize = chartDef.default_size || 6;
            }
            sizeSelect.value = currentSize;
        }
        
        const enabledCheckbox = modal.querySelector('#chart-enabled-checkbox');
        if (enabledCheckbox) {
            enabledCheckbox.checked = currentSettings?.enabled !== false; 
        }
        
        if (loadingDiv) loadingDiv.style.display = 'none';
        if (formDiv) formDiv.style.display = 'block';
        
        const modalTitle = modal.querySelector('#chart-settings-modal-label');
        if (modalTitle && chartDef) {
            modalTitle.textContent = `Chart Settings - ${chartDef.name}`;
        }
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    async applyChartSettings() {
        if (!this.selectedChart) {
            console.error('No chart selected');
            return;
        }
        
        const modal = document.getElementById('chart-settings-modal');
        const type = modal.querySelector('#chart-type-select')?.value;
        const size = modal.querySelector('#chart-size-select')?.value;
        const enabled = modal.querySelector('#chart-enabled-checkbox')?.checked;
        
        const applyBtn = modal.querySelector('#apply-chart-settings-btn');
        const originalBtnText = applyBtn ? applyBtn.textContent : 'Apply Settings';
        if (applyBtn) {
            applyBtn.disabled = true;
            applyBtn.textContent = 'Saving...';
        }
        
        try {
            const response = await fetch(`/preference/api/chart-settings/${this.selectedChart}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    chart_type: type,
                    size: parseInt(size),
                    enabled: enabled === true || enabled === undefined
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                if (!window.chartSettings) window.chartSettings = {};
                window.chartSettings[this.selectedChart] = data.settings;
                
                console.log(`Chart settings saved successfully for ${this.selectedChart}`);
            } else {
                console.error('Error saving chart settings:', data.message);
                alert(`Error saving chart settings: ${data.message || 'Unknown error'}`);
                if (applyBtn) {
                    applyBtn.disabled = false;
                    applyBtn.textContent = originalBtnText;
                }
                return;
            }
        } catch (error) {
            console.error('Error saving chart settings to API:', error);
            alert('Error saving chart settings. Please try again.');
            if (applyBtn) {
                applyBtn.disabled = false;
                applyBtn.textContent = originalBtnText;
            }
            return;
        }
        
        
        let chartElement = this.selectedChartElement;
        
        if (!chartElement) {
            if (this.selectedChartUniqueId) {
                chartElement = document.getElementById(this.selectedChartUniqueId);
            }
            
            if (!chartElement) {
                const allCharts = document.querySelectorAll(`[data-chart-id="${this.selectedChart}"]`);
                
                if (this.selectedChartUniqueId) {
                    chartElement = Array.from(allCharts).find(el => {
                        const wrapperId = el.id || '';
                        return wrapperId === this.selectedChartUniqueId || wrapperId.includes(this.selectedChartUniqueId.split('-').pop());
                    });
                }
                
                if (!chartElement && allCharts.length > 0) {
                    chartElement = allCharts[0];
                }
            }
        }
        
        if (!chartElement) {
            console.error(`Chart element not found for chartId: ${this.selectedChart}, uniqueId: ${this.selectedChartUniqueId}`);
            return;
        }
        
        const colElement = chartElement.closest('[class*="col-md-"]');
        const oldSize = colElement ? parseInt(colElement.className.match(/col-md-(\d+)/)?.[1] || '6') : null;
        const newSize = size ? parseInt(size) : null;
        const sizeChanged = oldSize !== null && newSize !== null && oldSize !== newSize;
        
        const chartDef = this.chartDefinitions[this.selectedChart] || window.chartDefinitions?.[this.selectedChart];
        
        const storedType = this.getCurrentChartType(this.selectedChart, chartElement, this.selectedChartUniqueId);
        const defaultType = (chartDef?.default_type || 'bar').toLowerCase();
        const currentType = storedType ? storedType.toLowerCase() : defaultType;
        const normalizedNewType = type ? type.toLowerCase().trim() : null;
        
        const shouldRerender = normalizedNewType !== null;
        const typeChanged = normalizedNewType && normalizedNewType !== currentType;
        
        console.log(`Size change - Old: ${oldSize}, New: ${newSize}, Changed: ${sizeChanged}`);
        console.log(`Type change - Stored: ${storedType}, Default: ${defaultType}, Current: ${currentType}, New: ${normalizedNewType}, Changed: ${typeChanged}, Should Rerender: ${shouldRerender}`);
        
        if (colElement && newSize) {
            colElement.className = colElement.className.replace(/col-md-\d+/, `col-md-${newSize}`);
            console.log(`Updated column size to: col-md-${newSize}`);
            
            const rowElement = colElement.closest('.dashboard-row');
            if (rowElement) {
                const columns = rowElement.querySelectorAll('[class*="col-md-"]');
                columns.forEach(col => {
                    const colSize = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '6');
                    this.updateChartSpacing(col, colSize);
                });
            } else {
                this.updateChartSpacing(colElement, newSize);
            }
        }
        
        const containerId = chartElement.id || `chart-${this.selectedChart}`;
        
        const columnId = colElement.dataset.columnId || colElement.id || null;
        
        const baseGraphContainerId = this.getGraphContainerId(this.selectedChart);
        let graphContainerId = baseGraphContainerId;
        
        const graphContainer = colElement.querySelector(`[id*="${baseGraphContainerId}"]`);
        if (graphContainer && graphContainer.id && graphContainer.id !== baseGraphContainerId) {
            graphContainerId = graphContainer.id;
        }
        
        if (this.layout && this.layout.rows) {
            this.layout.rows.forEach(row => {
                if (row.columns) {
                    row.columns.forEach(col => {
                        if (col.chart_id === this.selectedChart) {
                            let shouldUpdate = false;
                            
                            if (this.selectedChartUniqueId && columnId) {
                                const uniqueSuffix = this.selectedChartUniqueId.split('-').pop();
                                if (col.id && col.id.includes(uniqueSuffix)) {
                                    shouldUpdate = true;
                                } else if (col.id === columnId) {
                                    shouldUpdate = true;
                                }
                            } else if (columnId && col.id === columnId) {
                                shouldUpdate = true;
                            } else if (!this.selectedChartUniqueId && !columnId) {
                                shouldUpdate = true;
                            }
                            
                            if (shouldUpdate) {
                                if (newSize) col.size = newSize;
                                if (normalizedNewType) {
                                    if (!col.settings) col.settings = {};
                                    col.settings.chart_type = normalizedNewType;
                                }
                            }
                        }
                    });
                }
            });
        }
        
        if (!window.chartSettings) {
            window.chartSettings = {};
        }
        
        if (normalizedNewType || newSize !== null) {
            if (!window.chartSettings[this.selectedChart]) {
                window.chartSettings[this.selectedChart] = {};
            }
            
            if (normalizedNewType) {
                window.chartSettings[this.selectedChart].chart_type = normalizedNewType;
            }
            
            if (newSize !== null) {
                window.chartSettings[this.selectedChart].size = newSize;
            }
            
            if (window.chartSettings[this.selectedChart].enabled === undefined) {
                window.chartSettings[this.selectedChart].enabled = true;
            }
        }
        
        if (!window.chartDefinitions || Object.keys(window.chartDefinitions).length === 0) {
            if (this.chartDefinitions && Object.keys(this.chartDefinitions).length > 0) {
                window.chartDefinitions = this.chartDefinitions;
            } 
            else {
                console.warn('Chart definitions not loaded, attempting to load...');
                this.loadLayout(false).then(() => {
                    if (this.chartDefinitions && Object.keys(this.chartDefinitions).length > 0) {
                        window.chartDefinitions = this.chartDefinitions;
                        setTimeout(() => this.applyChartSettings(), 100);
                    }
                });
                return;
            }
        }
        
        if (!window.chartDefinitions[this.selectedChart]) {
            console.error(`Chart definition not found for ${this.selectedChart}. Available charts:`, Object.keys(window.chartDefinitions || {}));
            console.error('Current window.chartDefinitions:', window.chartDefinitions);
            return;
        }
        
        if (shouldRerender && normalizedNewType && window.ChartRenderer && graphContainerId) {
            
            let graphContainerElement = document.getElementById(graphContainerId);
            if (!graphContainerElement) {
                console.warn(`Graph container not found: ${graphContainerId}, trying to find within column...`);
                const fallbackContainer = colElement.querySelector(`[id*="${baseGraphContainerId}"]`);
                if (fallbackContainer && fallbackContainer.id) {
                    graphContainerId = fallbackContainer.id;
                    graphContainerElement = fallbackContainer;
                } else {
                    console.error(`Could not find graph container for chart: ${this.selectedChart}`);
                }
            }
            
            if (graphContainerElement) {
                window.ChartRenderer.destroyChart(graphContainerId);
            }
            
            setTimeout(() => {
                const container = document.getElementById(graphContainerId);
                if (!container) {
                    console.error(`Graph container still not found after destroy: ${graphContainerId}`);
                    const retryContainer = colElement.querySelector(`[id*="${baseGraphContainerId}"]`);
                    if (retryContainer && retryContainer.id) {
                        graphContainerId = retryContainer.id;
                    } else {
                        return;
                    }
                }
                
                const chartTypeToRender = normalizedNewType;
                const success = window.ChartRenderer.renderChart(this.selectedChart, chartTypeToRender, graphContainerId, {});
                if (!success) {
                    console.error(`Failed to render chart: ${this.selectedChart} with type: ${chartTypeToRender}`);
                } else {
                    console.log(`Successfully re-rendered chart: ${this.selectedChart} with type: ${chartTypeToRender}`);
                }
            }, 150);
        } else if (sizeChanged && !shouldRerender) {   
            console.log(`Only size changed (${oldSize} -> ${newSize}), resizing chart: ${this.selectedChart} (NO re-render)`);
            setTimeout(() => {
                this.resizeChart(containerId);
            }, 100);
        } else if (!shouldRerender && !sizeChanged) {
            console.log(`No changes detected, skipping resize/render`);
        }
        
        if (applyBtn) {
            applyBtn.disabled = false;
            applyBtn.textContent = originalBtnText;
        }
        
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
        
        this.saveLayout();
    }
    
    getCurrentChartType(chartId, chartElement = null, uniqueId = null) {
        if (window.chartSettings && window.chartSettings[chartId] && window.chartSettings[chartId].chart_type) {
            return window.chartSettings[chartId].chart_type.toLowerCase().trim();
        }
        
        if (this.layout && this.layout.rows) {
            for (const row of this.layout.rows) {
                if (row.columns) {
                    for (const col of row.columns) {
                        if (col.chart_id === chartId && col.settings && col.settings.chart_type) {
                            if (uniqueId && col.id) {
                                const uniqueSuffix = uniqueId.split('-').pop();
                                if (col.id.includes(uniqueSuffix)) {
                                    const chartType = col.settings.chart_type;
                                    return chartType ? chartType.toLowerCase().trim() : null;
                                }
                            } else if (!uniqueId) {
                                const chartType = col.settings.chart_type;
                                return chartType ? chartType.toLowerCase().trim() : null;
                            }
                        }
                    }
                }
            }
        }
        
        if (chartElement) {
            const colElement = chartElement.closest('[class*="col-md-"]');
            if (colElement) {
                const columnId = colElement.dataset.columnId || colElement.id;
                if (columnId && this.layout && this.layout.rows) {
                    for (const row of this.layout.rows) {
                        if (row.columns) {
                            for (const col of row.columns) {
                                if (col.id === columnId && col.settings && col.settings.chart_type) {
                                    const chartType = col.settings.chart_type;
                                    return chartType ? chartType.toLowerCase().trim() : null;
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return null;
    }
    
    resizeChart(containerId) {
        const chartElement = document.getElementById(containerId);
        if (!chartElement) {
            console.warn(`Chart container not found: ${containerId}`);
            return;
        }
        
        const chartId = chartElement.dataset.chartId || containerId.replace('chart-', '');
        
        if (!chartId) {
            console.error('Could not determine chartId from element');
            return;
        }
        
        const chartContainerMap = {
            'monthly_active_users': 'monthly-active-users-graph-id',
            'users_by_origin_country': 'preference-origin-graph-id',
            'users_by_gender': 'preference-gender-chart-id',
            'users_by_destination_country': 'preference-destination-chart-id',
            'users_by_language': 'preference-language-graph-id',
            'users_by_country_state': 'users-by-country-state-graph-id',
            'users_by_immigration_status': 'preference-immigration-status-chart-id',
            'users_by_age': 'preference-age-chart-id',
            'users_by_sector': 'users-by-sector-graph-id',
            'work_code_usage': 'organisation-work-code-usage-graph-id',
            'new_monthly_users': 'preference-monthly-cumulative-users-graph-id',
            'link_clicks': 'link-clicks-graph-id',
            'user_route_map': 'user_route_map',
            'user_geolocation_map': 'user_geolocation_map',
            'user_geolocation_map_user_engagement': 'user_geolocation_map_user_engagement'
        };
        
        const graphContainerId = chartContainerMap[chartId];
        if (!graphContainerId) {
            console.warn(`No graph container ID mapped for chartId: ${chartId}`);
            return;
        }
        
        const graphContainer = chartElement.querySelector(`[id="${graphContainerId}"]`);
        if (!graphContainer) {
            console.warn(`Graph container not found: ${graphContainerId} within chart element`);
            const fallbackContainer = document.getElementById(graphContainerId);
            if (fallbackContainer) {
                this.resizeSingleContainer(fallbackContainer, chartId);
                return;
            }
            return;
        }
        
        this.resizeSingleContainer(graphContainer, chartId);
        
        const canvasElements = graphContainer.querySelectorAll('canvas');
        canvasElements.forEach(canvas => {
            this.resizeSingleContainer(canvas, chartId);
        });
        
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 150);
    }
    
    resizeSingleContainer(element, chartId) {
        if (!element || !element.id) return;
        
        let resizeAttempted = false;
        
        if (window.chartInstances && window.chartInstances[element.id]) {
            const chartInstance = window.chartInstances[element.id];
            if (chartInstance && typeof chartInstance.resize === 'function') {
                chartInstance.resize();
                resizeAttempted = true;
                console.log(`✓ Resized Chart.js instance for: ${element.id} (chart: ${chartId})`);
            }
        }
        
        if (window.Chart && typeof window.Chart.getChart === 'function') {
            const canvas = element.tagName === 'CANVAS' ? element : element.querySelector('canvas');
            if (canvas) {
                const chartInstance = window.Chart.getChart(canvas);
                if (chartInstance && typeof chartInstance.resize === 'function') {
                    chartInstance.resize();
                    resizeAttempted = true;
                    console.log(`✓ Resized Chart.js instance from registry for: ${canvas.id || 'canvas'} (chart: ${chartId})`);
                }
            }
        }
        
        if (typeof echarts !== 'undefined' && echarts.getInstanceByDom) {
            const echartsInstance = echarts.getInstanceByDom(element);
            if (echartsInstance && typeof echartsInstance.resize === 'function') {
                echartsInstance.resize();
                resizeAttempted = true;
                console.log(`✓ Resized ECharts instance for: ${element.id} (chart: ${chartId})`);
            }
        }
        
        if (!resizeAttempted) {
            console.log(`No resize method found for ${element.id}, attempting to re-render chart: ${chartId}`);
            const chartDef = this.chartDefinitions[chartId] || window.chartDefinitions?.[chartId];
            const chartType = chartDef?.default_type || 'bar';
            
            if (window.ChartRenderer) {
                window.ChartRenderer.destroyChart(element.id);
                setTimeout(() => {
                    window.ChartRenderer.renderChart(chartId, chartType, element.id, {});
                }, 100);
            }
        }
    }
    
    duplicateChart(chartId) {
        
        const chartElement = document.querySelector(`[data-chart-id="${chartId}"]`);
        if (!chartElement) {
            console.error(`Chart element not found for: ${chartId}`);
            return;
        }
        
        const row = chartElement.closest('.dashboard-row');
        if (!row) {
            console.error('Row not found for chart element');
            return;
        }
        
        const colElement = chartElement.closest('[class*="col-md-"]');
        if (!colElement) {
            console.error('Column element not found for chart');
            return;
        }
        
        let originalColData = null;
        if (this.layout && this.layout.rows) {
            for (const rowData of this.layout.rows) {
                if (rowData.columns) {
                    for (const col of rowData.columns) {
                        if (col.chart_id === chartId) {
                            originalColData = col;
                            break;
                        }
                    }
                }
                if (originalColData) break;
            }
        }
        
        if (!originalColData) {
            const currentSize = parseInt(colElement.className.match(/col-md-(\d+)/)?.[1] || '6');
            const chartDef = this.chartDefinitions[chartId] || window.CHART_DEFINITIONS?.[chartId];
            const currentType = this.getCurrentChartType(chartId) || chartDef?.default_type || 'bar';
            
            originalColData = {
                chart_id: chartId,
                size: currentSize,
                enabled: true,
                settings: {
                    chart_type: currentType
                }
            };
        }
        
        const timestamp = Date.now();
        const duplicateId = `duplicate_${timestamp}`;
        
        const newColData = {
            id: `col-${chartId}-${duplicateId}`,
            chart_id: chartId,
            size: originalColData.size || 6,
            enabled: originalColData.enabled !== false,
            settings: {
                ...originalColData.settings,
                chart_type: originalColData.settings?.chart_type || this.chartDefinitions[chartId]?.default_type || 'bar',
                is_duplicate: true,
                duplicate_id: duplicateId
            }
        };
        
        let columnsContainer = row.querySelector('.row:not(.dashboard-row)');
        if (!columnsContainer && row.classList.contains('row')) {
            columnsContainer = row;
        }
        
        if (!columnsContainer) {
            console.error('Columns container not found in row');
            return;
        }
        
        const baseGraphContainerId = this.getGraphContainerId(chartId);
        const graphContainerId = `${baseGraphContainerId}-${duplicateId}`;
        
        const colEl = this.createColumnElement(newColData, columnsContainer.children.length);
        
        const chartWrapper = colEl.querySelector(`[data-chart-id="${chartId}"]`);
        if (!chartWrapper) {
            console.error('Chart wrapper not found in duplicated column');
            return;
        }
        
        chartWrapper.id = `chart-${chartId}-${duplicateId}`;
        
        const existingGraphContainer = chartWrapper.querySelector(`#${baseGraphContainerId}`);
        if (existingGraphContainer) {
            existingGraphContainer.id = graphContainerId;
            console.log(`Updated graph container ID from ${baseGraphContainerId} to ${graphContainerId}`);
        } else {
            const graphContainer = document.createElement('div');
            graphContainer.id = graphContainerId;
            graphContainer.style.height = '500px';
            graphContainer.style.width = '100%';
            graphContainer.style.maxWidth = '100%';
            graphContainer.style.boxSizing = 'border-box';

            const chartHeader = chartWrapper.querySelector('.chart-header');
            if (chartHeader) {
                chartHeader.insertAdjacentElement('afterend', graphContainer);
            } else {
                chartWrapper.appendChild(graphContainer);
            }
            console.log(`Created unique graph container: ${graphContainerId}`);
        }
        
        columnsContainer.appendChild(colEl);
        
        if (!this.layout) this.layout = { rows: [] };
        if (!this.layout.rows) this.layout.rows = [];
        
        const rowId = row.dataset.rowId || `row-${timestamp}`;
        let rowData = this.layout.rows.find(r => r.id === rowId);
        if (!rowData) {
            rowData = { id: rowId, columns: [] };
            this.layout.rows.push(rowData);
        }
        if (!rowData.columns) rowData.columns = [];
        rowData.columns.push(newColData);

        this.updateChartSpacing(colEl, newColData.size);
        
        setTimeout(() => {
            if (window.ChartRenderer && graphContainerId) {
                const graphContainer = document.getElementById(graphContainerId);
                if (!graphContainer) {
                    console.error(`Graph container not found: ${graphContainerId}`);
                    return;
                }
                
                const chartType = newColData.settings?.chart_type || this.chartDefinitions[chartId]?.default_type || 'bar';
                
                console.log(`Rendering duplicate chart: ${chartId}, type: ${chartType}, container: ${graphContainerId}`);
                
                const success = window.ChartRenderer.renderChart(
                    chartId,
                    chartType,
                    graphContainerId,
                    newColData.settings || {}
                );
                
                if (!success) {
                    console.error(`Failed to render duplicated chart: ${chartId}`);
                } else {
                    console.log(`Successfully rendered duplicated chart: ${chartId} with type: ${chartType} in container: ${graphContainerId}`);
                }
            } else {
                console.error(`ChartRenderer not available or graph container ID not found: ${graphContainerId}`);
            }
        }, 200);
        
        this.setupChartSortable();
        
        setTimeout(() => {
            this.applySpacingToAllCharts();
        }, 100);
        
        this.saveLayout();
        
        const chartDef = this.chartDefinitions[chartId] || window.chartDefinitions?.[chartId];
        const chartName = chartDef ? chartDef.name : chartId;
        this.showNotification(`Chart "${chartName}" duplicated successfully`, 'success');
    }
    
    removeChartFromButton(button) {
        const chartInfo = this.getChartInfoFromButton(button);
        if (!chartInfo) {
            return;
        }
        
        this.removeChart(chartInfo.chartId, chartInfo.chartWrapper, chartInfo.uniqueId);
    }
    
    removeChart(chartId, chartElement = null, uniqueId = null) {
        if (!confirm('Remove this chart from dashboard?')) {
            return;
        }
        
        if (!chartElement) {
            if (uniqueId) {
                chartElement = document.getElementById(uniqueId);
            }
            
            if (!chartElement) {
                const allCharts = document.querySelectorAll(`[data-chart-id="${chartId}"]`);
                
                if (uniqueId) {
                    chartElement = Array.from(allCharts).find(el => {
                        const wrapperId = el.id || '';
                        return wrapperId === uniqueId || wrapperId.includes(uniqueId.split('-').pop());
                    });
                }
                
                if (!chartElement && allCharts.length > 0) {
                    chartElement = allCharts[0];
                }
            }
        }
        
        if (!chartElement) {
            console.error(`Chart element not found for chartId: ${chartId}, uniqueId: ${uniqueId}`);
            return;
        }
        
        const colElement = chartElement.closest('[class*="col-md-"]');
        if (!colElement) {
            console.error('Column element not found for chart');
            return;
        }
        
        const graphContainer = colElement.querySelector('[id*="-graph-id"], [id*="-chart-id"], [id*="user_route_map"], [id*="user_geolocation_map"], [id="link-clicks-graph-id"]');
        if (graphContainer && graphContainer.id) {
            const containerElement = document.getElementById(graphContainer.id);
            if (containerElement && window.ChartRenderer) {
                try {
                    window.ChartRenderer.destroyChart(graphContainer.id);
                } catch (error) {
                    console.warn(`Error destroying chart for container ${graphContainer.id}:`, error);
                }
            }
        }
        
        const columnId = colElement.dataset.columnId || colElement.id || null;
        
        colElement.remove();
        
        if (this.layout && this.layout.rows) {
            this.layout.rows.forEach(row => {
                if (row.columns) {
                    row.columns = row.columns.filter(col => {
                        if (columnId && col.id === columnId) {
                            return false;
                        }
                        
                        if (uniqueId && col.id) {
                            const uniqueSuffix = uniqueId.split('-').pop();
                            if (col.id.includes(uniqueSuffix)) {
                                return false;
                            }
                        }
                        
                        return true;
                    });
                }
            });
        }
        
        setTimeout(() => {
            this.applySpacingToAllCharts();
        }, 100);
        
        this.saveLayout();
        
        const chartDef = this.chartDefinitions[chartId] || window.chartDefinitions?.[chartId];
        const chartName = chartDef ? chartDef.name : chartId;
        this.showNotification(`Chart "${chartName}" removed successfully`, 'success');
    }
    
    deleteRow(button) {
        const row = button.closest('.dashboard-row');
        if (!row) return;
        
        if (!confirm('Delete this row and all its charts?')) {
            return;
        }
        
        row.remove();
        this.saveLayout();
    }
    
    updateColumnSizes() {
        document.querySelectorAll('.dashboard-row').forEach(row => {
            const columns = row.querySelectorAll('[class*="col-md-"]');
            const totalSize = Array.from(columns).reduce((sum, col) => {
                const size = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '6');
                return sum + size;
            }, 0);
            
            if (totalSize !== 12 && columns.length > 0) {
                const sizePerCol = Math.floor(12 / columns.length);
                columns.forEach(col => {
                    const oldSize = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '6');
                    col.className = col.className.replace(/col-md-\d+/, `col-md-${sizePerCol}`);
                });
            }
            
            columns.forEach(col => {
                const size = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '6');
                this.updateChartSpacing(col, size);
            });
        });
    }
    
    getGraphContainerId(chartId) {
        const chartContainerMap = {
            'monthly_active_users': 'monthly-active-users-graph-id',
            'users_by_origin_country': 'preference-origin-graph-id',
            'users_by_gender': 'preference-gender-chart-id',
            'users_by_destination_country': 'preference-destination-chart-id',
            'users_by_language': 'preference-language-graph-id',
            'users_by_country_state': 'users-by-country-state-graph-id',
            'users_by_immigration_status': 'preference-immigration-status-chart-id',
            'users_by_age': 'preference-age-chart-id',
            'users_by_sector': 'users-by-sector-graph-id',
            'work_code_usage': 'organisation-work-code-usage-graph-id',
            'new_monthly_users': 'preference-monthly-cumulative-users-graph-id',
            'link_clicks': 'link-clicks-graph-id',
            'user_route_map': 'user_route_map',
            'user_geolocation_map': 'user_geolocation_map',
            'user_geolocation_map_user_engagement': 'user_geolocation_map_user_engagement'
        };
        return chartContainerMap[chartId] || null;
    }
    
    updateChartSpacing(colElement, size) {
        if (!colElement) return;
        
        const rowElement = colElement.closest('.dashboard-row');
        if (!rowElement) {
            if (size === 12) {
                colElement.style.marginBottom = '25px';
            } else {
                colElement.style.marginBottom = '';
            }
            return;
        }
        
        const columns = rowElement.querySelectorAll('[class*="col-md-"]');
        let totalSize = 0;
        columns.forEach(col => {
            const colSize = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '0');
            totalSize += colSize;
        });
        
        if (totalSize > 12 || size === 12) {
            colElement.style.marginBottom = '25px';
        } else {
            colElement.style.marginBottom = '';
        }
    }
    
    togglePreview() {
        document.body.classList.toggle('dashboard-preview-mode');
        const isPreview = document.body.classList.contains('dashboard-preview-mode');
        this.showNotification(isPreview ? 'Preview mode enabled' : 'Preview mode disabled', 'info');
    }
    
    getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        if (cookieValue) return cookieValue;
        
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : '';
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `dashboard-notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#007bff'};
            color: white;
            border-radius: 5px;
            z-index: 10000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.3s';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.dashboardCustomizer = new DashboardCustomizer();
    setTimeout(() => {
        window.dashboardCustomizer.init();
    }, 500);
});

