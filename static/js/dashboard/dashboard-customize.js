/**
 * Dashboard Customizer
 * Main class for managing dashboard customization functionality
 * WPBakery Page Builder style implementation
 */

class DashboardCustomizer {
    constructor() {
        this.isCustomizing = false;
        this.layout = null;
        this.sortableInstances = [];
        this.selectedChart = null;
        this.chartDefinitions = {};
        this.availableCharts = [];
    }
    
    /**
     * Initialize the customizer
     */
    async init() {
        this.setupEventListeners();
        // Only load layout if user has saved preferences, otherwise let existing charts render
        await this.loadLayout(true); // Pass flag to indicate initial load
        
        // CRITICAL: Ensure chart definitions are available globally after initial load
        if (this.chartDefinitions && Object.keys(this.chartDefinitions).length > 0) {
            window.CHART_DEFINITIONS = this.chartDefinitions;
            console.log('Initialized window.CHART_DEFINITIONS on init:', Object.keys(window.CHART_DEFINITIONS));
        } else {
            console.warn('Chart definitions not loaded on init');
        }
        
        // Apply spacing to existing charts on initial load
        setTimeout(() => {
            this.applySpacingToAllCharts();
        }, 600);
    }
    
    /**
     * Setup event listeners for toolbar buttons
     */
    setupEventListeners() {
        // Customize button
        const customizeBtn = document.getElementById('customize-dashboard-btn');
        if (customizeBtn) {
            customizeBtn.addEventListener('click', () => this.enterCustomizeMode());
        }
        
        // Toolbar buttons
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
    
    /**
     * Load layout from API or use default
     * @param {boolean} isInitialLoad - If true, don't render if no custom layout exists
     */
    async loadLayout(isInitialLoad = false) {
        try {
            console.log('Loading dashboard layout from API...');
            const response = await fetch('/preference/api/dashboard/customize/');
            
            if (!response.ok) {
                console.error(`API response not OK: ${response.status} ${response.statusText}`);
                throw new Error(`API request failed: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('API response received:', {
                hasLayout: !!data.layout,
                hasChartDefinitions: !!data.chart_definitions,
                chartDefinitionsCount: data.chart_definitions ? Object.keys(data.chart_definitions).length : 0,
                availableChartsCount: data.available_charts ? data.available_charts.length : 0,
                chartDefinitions: data.chart_definitions
            });
            
            this.layout = data.layout || { rows: [] };
            this.chartDefinitions = data.chart_definitions || {};
            this.availableCharts = data.available_charts || [];
            
            // Store chart definitions globally for ChartRenderer
            if (this.chartDefinitions && Object.keys(this.chartDefinitions).length > 0) {
                window.CHART_DEFINITIONS = this.chartDefinitions;
                console.log('✓ Set window.CHART_DEFINITIONS with', Object.keys(this.chartDefinitions).length, 'charts');
            } else {
                console.warn('⚠ No chart definitions received from API!');
            }
            
            // Check if user has a custom layout saved
            const hasCustomLayout = this.layout && this.layout.rows && this.layout.rows.length > 0;
            
            // On initial load, NEVER render - just extract structure for later use
            if (isInitialLoad) {
                if (!hasCustomLayout) {
                    // Extract structure from existing DOM
                    this.layout = this.extractLayoutFromDOM();
                }
                // Don't render on initial load - let existing charts stay
                return;
            }
            
            // Only render if explicitly requested (not initial load) and not in customize mode
            if (!this.isCustomizing && hasCustomLayout) {
                this.renderLayout();
            } else if (!hasCustomLayout) {
                // Extract structure if needed
                this.layout = this.extractLayoutFromDOM();
            }
        } catch (error) {
            console.error('Error loading dashboard layout:', error);
            if (!isInitialLoad) {
                this.layout = this.extractLayoutFromDOM();
            }
        }
    }
    
    /**
     * Enter customization mode
     */
    async enterCustomizeMode() {
        this.isCustomizing = true;
        document.body.classList.add('dashboard-customize-mode');
        
        const toolbar = document.getElementById('dashboard-toolbar');
        if (toolbar) {
            toolbar.style.display = 'flex';
        }
        
        // Load chart definitions if not already loaded
        if (!this.chartDefinitions || Object.keys(this.chartDefinitions).length === 0) {
            await this.loadLayout(false);
        }
        
        // Ensure chart definitions are available globally
        if (!window.CHART_DEFINITIONS || Object.keys(window.CHART_DEFINITIONS).length === 0) {
            if (this.chartDefinitions && Object.keys(this.chartDefinitions).length > 0) {
                window.CHART_DEFINITIONS = this.chartDefinitions;
                console.log('Set window.CHART_DEFINITIONS on entering customize mode');
            }
        }
        
        // Ensure we have the latest layout structure
        if (!this.layout || !this.layout.rows || this.layout.rows.length === 0) {
            this.layout = this.extractLayoutFromDOM();
        }
        
        this.addCustomizationControls();
        this.initializeDragAndDrop();
        
        // Apply spacing to all charts when entering customization mode
        setTimeout(() => {
            this.applySpacingToAllCharts();
        }, 100);
        
        // Show notification
        this.showNotification('Customization mode enabled', 'info');
    }
    
    /**
     * Exit customization mode
     */
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
        
        // Reload layout but don't re-render - let existing charts stay
        this.loadLayout(false).then(() => {
            // Only re-render if user has a custom layout saved
            const hasCustomLayout = this.layout && this.layout.rows && this.layout.rows.length > 0;
            if (hasCustomLayout) {
                this.renderLayout();
            }
            // Otherwise, just let the existing DOM structure remain
        });
    }
    
    /**
     * Add customization controls to rows and charts - WPBakery Style
     */
    addCustomizationControls() {
        // Add row toolbars and badges
        document.querySelectorAll('.dashboard-row').forEach((row, index) => {
            if (!row.querySelector('.row-toolbar')) {
                row.appendChild(this.createRowToolbar(row, index));
            }
            // Add row number badge
            if (!row.querySelector('.row-number-badge')) {
                const badge = document.createElement('div');
                badge.className = 'row-number-badge';
                badge.textContent = index + 1;
                row.appendChild(badge);
            }
        });
        
        // Add chart toolbars - only to outermost dashboard-chart elements (not nested ones)
        // Find all dashboard-chart elements that are direct children of dashboard-row or within a col
        document.querySelectorAll('.dashboard-row').forEach(row => {
            // Find all dashboard-chart elements within this row
            row.querySelectorAll('.dashboard-chart').forEach(chart => {
                // Skip if this chart is nested inside another dashboard-chart
                const parentChart = chart.parentElement.closest('.dashboard-chart');
                if (parentChart && parentChart !== chart) {
                    return; // This is a nested chart, skip it
                }
                
                // Skip if toolbar already exists
                if (chart.querySelector('.chart-toolbar')) {
                    return;
                }
                
                // Find the actual chart element with data-chart-id (may be a child of dashboard-chart)
                const chartElementWithId = chart.querySelector('[data-chart-id]') || chart;
                
                // Only add toolbar to the outermost dashboard-chart element
                chart.appendChild(this.createChartToolbar(chartElementWithId));
            });
        });
        
        // Also wrap charts in cards that don't have dashboard-chart wrapper
        // BUT only if the card doesn't already contain a dashboard-chart
        document.querySelectorAll('.dashboard-row .card').forEach(card => {
            // Skip if already wrapped in dashboard-chart
            if (card.closest('.dashboard-chart')) return;
            
            // Skip if card already contains a dashboard-chart (it's already properly wrapped)
            if (card.querySelector('.dashboard-chart')) return;
            
            // Check if this card contains a chart (but doesn't have dashboard-chart wrapper)
            const chartId = this.detectChartId(card);
            if (chartId) {
                // Wrap the card in dashboard-chart
                const wrapper = document.createElement('div');
                wrapper.className = 'dashboard-chart';
                wrapper.dataset.chartId = chartId;
                card.parentNode.insertBefore(wrapper, card);
                wrapper.appendChild(card);
                
                // Add chart toolbar (only if not already added)
                if (!wrapper.querySelector('.chart-toolbar')) {
                    wrapper.appendChild(this.createChartToolbar(wrapper));
                }
            }
        });
    }
    
    /**
     * Detect chart ID from card element
     */
    detectChartId(card) {
        // Try to find chart ID from various selectors
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
                // Extract chart ID from selector
                return selector.replace('#', '').replace('-graph-id', '').replace('-chart-id', '');
            }
        }
        
        // Try data attributes
        if (card.dataset.chartId) return card.dataset.chartId;
        if (card.id) {
            const idMatch = card.id.match(/(\w+)-(card|chart)/);
            if (idMatch) return idMatch[1];
        }
        
        return null;
    }
    
    /**
     * Remove customization controls
     */
    removeCustomizationControls() {
        document.querySelectorAll('.row-toolbar, .chart-toolbar, .row-number-badge').forEach(ctrl => {
            ctrl.remove();
        });
    }
    
    /**
     * Create row toolbar - WPBakery Style
     */
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
    
    /**
     * Create chart toolbar - WPBakery Style
     */
    createChartToolbar(chartElement) {
        const toolbar = document.createElement('div');
        toolbar.className = 'chart-toolbar';
        
        // Get chart ID from multiple sources
        // First, check if this element itself has data-chart-id
        let chartId = chartElement.dataset.chartId;
        
        // If not, look for a child element with data-chart-id (common structure)
        if (!chartId) {
            const childWithId = chartElement.querySelector('[data-chart-id]');
            if (childWithId) {
                chartId = childWithId.dataset.chartId;
            }
        }
        
        // If still not found, try to find it from closest parent with data-chart-id
        if (!chartId) {
            const parentWithId = chartElement.closest('[data-chart-id]');
            if (parentWithId) {
                chartId = parentWithId.dataset.chartId;
            }
        }
        
        // If still no chart ID, try to detect from the chart element's ID or content
        if (!chartId) {
            // Try to extract from element ID
            if (chartElement.id && chartElement.id.startsWith('chart-')) {
                chartId = chartElement.id.replace('chart-', '');
            } else {
                // Try to detect from chart content
                chartId = this.detectChartId(chartElement);
            }
        }
        
        console.log(`Creating toolbar for chart element:`, chartElement, `detected chartId:`, chartId);
        
        // Get chart name from multiple sources
        let chartName = 'Chart';
        
        // First try this.chartDefinitions (loaded from API)
        if (chartId && this.chartDefinitions && this.chartDefinitions[chartId]) {
            chartName = this.chartDefinitions[chartId].name;
        }
        // Fallback to window.CHART_DEFINITIONS (global)
        else if (chartId && window.CHART_DEFINITIONS && window.CHART_DEFINITIONS[chartId]) {
            chartName = window.CHART_DEFINITIONS[chartId].name;
        }
        // Try to extract from chart title in DOM
        else if (chartElement) {
            const titleElement = chartElement.querySelector('.chart-main-title, .chart-title, h4');
            if (titleElement) {
                chartName = titleElement.textContent.trim();
            }
        }
        // Fallback to formatted chart ID
        if (chartName === 'Chart' && chartId) {
            chartName = chartId.replace(/_/g, ' ')
                .replace(/\b\w/g, l => l.toUpperCase())
                .replace(/\bUsers\b/g, 'Users')
                .replace(/\bBy\b/g, 'by');
        }
        
        // Ensure we have a chart ID for the buttons
        if (!chartId) {
            console.warn('Could not determine chart ID for element:', chartElement);
            chartId = 'unknown';
        }
        
        toolbar.innerHTML = `
            <span class="chart-toolbar-label" title="${chartName}">${chartName}</span>
            <button class="chart-toolbar-btn drag-handle" title="Drag Chart" onclick="event.stopPropagation();">
                <i class="fe-move"></i>
            </button>
            <button class="chart-toolbar-btn edit-btn" title="Edit Chart" onclick="event.stopPropagation(); dashboardCustomizer.editChart('${chartId}');">
                <i class="fe-edit"></i>
            </button>
            <button class="chart-toolbar-btn duplicate-btn" title="Duplicate Chart" onclick="event.stopPropagation(); dashboardCustomizer.duplicateChart('${chartId}');">
                <i class="fe-copy"></i>
            </button>
            <button class="chart-toolbar-btn remove-btn" title="Remove Chart" onclick="event.stopPropagation(); dashboardCustomizer.removeChart('${chartId}');">
                <i class="fe-x"></i>
            </button>
        `;
        return toolbar;
    }
    
    /**
     * Initialize drag and drop using SortableJS
     */
    initializeDragAndDrop() {
        // Get SortableJS library
        const sortableScript = document.createElement('script');
        sortableScript.src = '/static/themes/modern/libs/sortablejs/Sortable.min.js';
        sortableScript.onload = () => {
            this.setupRowSortable();
            this.setupChartSortable();
        };
        
        // Check if already loaded
        if (window.Sortable) {
            this.setupRowSortable();
            this.setupChartSortable();
        } else {
            document.head.appendChild(sortableScript);
        }
    }
    
    /**
     * Setup row sorting
     */
    setupRowSortable() {
        const rowsContainer = document.getElementById('dashboard-rows-container');
        if (!rowsContainer || !window.Sortable) return;
        
        // Destroy existing instance
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
    
    /**
     * Setup chart sorting
     */
    setupChartSortable() {
        if (!window.Sortable) return;
        
        document.querySelectorAll('.dashboard-row').forEach((row, rowIndex) => {
            // Handle both cases:
            // 1. When .dashboard-row has a nested .row container (dynamically created)
            // 2. When .dashboard-row IS the .row (existing HTML - same element has both classes)
            let columnsContainer = row.querySelector('.row:not(.dashboard-row)');
            
            // If no nested .row found, check if this row itself is a .row
            // In existing HTML: <div class="row dashboard-row">
            if (!columnsContainer && row.classList.contains('row')) {
                // The row itself is the container, columns are direct children
                columnsContainer = row;
            }
            
            if (!columnsContainer) {
                console.warn('No columns container found for row:', row);
                return;
            }
            
            const instanceKey = `chart-row-${rowIndex}`;
            
            // Destroy existing instance
            if (this.sortableInstances[instanceKey]) {
                this.sortableInstances[instanceKey].destroy();
            }
            
            // When using the row itself as container, we need to filter out non-column elements
            const draggableSelector = row === columnsContainer 
                ? '[class*="col-md-"]' 
                : null; // Let SortableJS auto-detect children when using nested .row
            
            this.sortableInstances[instanceKey] = new Sortable(columnsContainer, {
                animation: 150,
                handle: '.chart-toolbar .drag-handle',
                group: 'charts', // Allow dragging between rows
                ghostClass: 'sortable-ghost',
                chosenClass: 'sortable-chosen',
                dragClass: 'sortable-drag',
                draggable: draggableSelector, // Only drag columns when row itself is container
                filter: '.row-toolbar, .row-number-badge', // Filter out row controls
                onEnd: () => {
                    this.updateColumnSizes();
                    this.saveLayout();
                }
            });
        });
    }
    
    /**
     * Destroy drag and drop instances
     */
    destroyDragAndDrop() {
        Object.values(this.sortableInstances).forEach(instance => {
            if (instance && instance.destroy) {
                instance.destroy();
            }
        });
        this.sortableInstances = [];
    }
    
    /**
     * Render layout from JSON structure
     */
    renderLayout() {
        const container = document.getElementById('dashboard-rows-container');
        if (!container) return;
        
        // Don't clear if charts are already rendered and we're not in customize mode
        const hasExistingCharts = container.querySelectorAll('.dashboard-chart, .card').length > 0;
        if (!this.isCustomizing && !hasExistingCharts) {
            // Only clear if there's nothing there
            container.innerHTML = '';
        } else if (!this.isCustomizing && hasExistingCharts) {
            // If charts exist, don't clear - just update structure
            console.log('Charts already rendered, skipping layout render');
            return;
        } else if (this.isCustomizing) {
            // In customize mode, we can clear and re-render
            container.innerHTML = '';
        }
        
        if (!this.layout || !this.layout.rows || this.layout.rows.length === 0) {
            return;
        }
        
        this.layout.rows.forEach((rowData, rowIndex) => {
            const rowEl = this.createRowElement(rowData, rowIndex);
            container.appendChild(rowEl);
        });
        
        // Apply spacing to all charts after layout is rendered
        setTimeout(() => {
            this.applySpacingToAllCharts();
        }, 50);
        
        // Render all charts
        setTimeout(() => {
            this.renderAllCharts();
        }, 100);
    }
    
    /**
     * Apply spacing to all charts in the dashboard
     * This method recalculates spacing for all charts based on their row's total column size
     */
    applySpacingToAllCharts() {
        document.querySelectorAll('.dashboard-row').forEach(row => {
            // First, calculate total size for this row
            const columns = row.querySelectorAll('[class*="col-md-"]');
            let totalSize = 0;
            columns.forEach(col => {
                const colSize = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '0');
                totalSize += colSize;
            });
            
            // Then apply spacing to each column based on row total
            columns.forEach(col => {
                const size = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '6');
                this.updateChartSpacing(col, size);
            });
        });
    }
    
    /**
     * Create row element
     */
    createRowElement(rowData, rowIndex) {
        const row = document.createElement('div');
        row.className = 'dashboard-row';
        row.dataset.rowId = rowData.id || `row-${rowIndex}`;
        
        // Add row toolbar and badge (always created, shown only in customize mode via CSS)
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
    
    /**
     * Create column element
     */
    createColumnElement(colData, colIndex) {
        const col = document.createElement('div');
        const colSize = colData.size || 6;
        col.className = `col-md-${colSize}`;
        col.dataset.columnId = colData.id || `col-${colIndex}`;
        
        // Apply spacing for full-width charts
        this.updateChartSpacing(col, colSize);
        
        // Create card structure similar to existing charts
        const card = document.createElement('div');
        card.className = 'card h-100';
        
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body dashboard-chart';
        
        const chartContainer = document.createElement('div');
        chartContainer.className = 'dashboard-chart';
        // Don't set ID on chartContainer - the wrapper will have it
        chartContainer.dataset.chartId = colData.chart_id;
        
        // Create inner chart wrapper (matches existing structure)
        const chartWrapper = document.createElement('div');
        chartWrapper.dataset.chartId = colData.chart_id;
        chartWrapper.id = `chart-${colData.chart_id}`;
        
        // Get chart definition for name
        const chartDef = this.chartDefinitions[colData.chart_id] || window.CHART_DEFINITIONS?.[colData.chart_id];
        const chartName = chartDef ? chartDef.name : colData.chart_id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        // Create chart header
        const chartHeader = document.createElement('div');
        chartHeader.className = 'chart-header';
        chartHeader.innerHTML = `
            <div class="chart-header-left">
                <h4 class="chart-main-title">${chartName}</h4>
            </div>
        `;
        chartWrapper.appendChild(chartHeader);
        
        // Create graph container placeholder (will be used by ChartRenderer)
        const graphContainerId = this.getGraphContainerId(colData.chart_id);
        if (graphContainerId) {
            const graphContainer = document.createElement('div');
            graphContainer.id = graphContainerId;
            graphContainer.style.height = '500px';
            graphContainer.style.width = '100%';
            chartWrapper.appendChild(graphContainer);
        }
        
        // Add chart toolbar (always created, shown only in customize mode)
        chartWrapper.appendChild(this.createChartToolbar(chartWrapper));
        
        chartContainer.appendChild(chartWrapper);
        cardBody.appendChild(chartContainer);
        card.appendChild(cardBody);
        col.appendChild(card);
        
        return col;
    }
    
    /**
     * Render all charts
     */
    renderAllCharts() {
        if (!this.layout || !this.layout.rows) return;
        
        this.layout.rows.forEach(row => {
            if (row.columns) {
                row.columns.forEach(col => {
                    if (col.enabled !== false && col.chart_id) {
                        const settings = col.settings || {};
                        const containerId = `chart-${col.chart_id}`;
                        
                        // Check if chart container exists
                        const container = document.getElementById(containerId);
                        if (!container) {
                            console.warn(`Chart container not found: ${containerId}`);
                            return;
                        }
                        
                        // Destroy existing chart if any
                        if (window.ChartRenderer) {
                            window.ChartRenderer.destroyChart(containerId);
                        }
                        
                        // Render new chart
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
    
    /**
     * Extract current layout from DOM
     */
    extractLayoutFromDOM() {
        const rows = [];
        const rowsContainer = document.getElementById('dashboard-rows-container');
        
        if (!rowsContainer) {
            // Fallback: extract from existing structure
            document.querySelectorAll('.dashboard-row').forEach((rowEl, rowIndex) => {
                const row = { id: rowEl.dataset.rowId || `row-${rowIndex}`, columns: [] };
                
                // Find all column elements (col-md-X) that contain charts
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
                
                // Find all column elements (col-md-X) that contain charts
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
    
    /**
     * Detect chart ID from element
     */
    detectChartId(element) {
        // Try to detect from container IDs or classes
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
    
    /**
     * Save current layout
     */
    async saveLayout() {
        const layout = this.extractLayoutFromDOM();
        
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
    
    /**
     * Reset dashboard to default
     */
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
    
    /**
     * Add new row
     */
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
        
        // Reinitialize sortable
        this.setupRowSortable();
        this.setupChartSortable();
    }
    
    /**
     * Add column to row
     */
    addColumnToRow(button) {
        this.showChartLibrary(button);
    }
    
    /**
     * Show chart library modal
     */
    async showChartLibrary(button = null) {
        const modal = document.getElementById('chart-library-modal');
        if (!modal) {
            console.error('Chart library modal not found');
            return;
        }
        
        // Ensure chart definitions are loaded
        if (!this.chartDefinitions || Object.keys(this.chartDefinitions).length === 0) {
            console.log('Loading chart definitions for chart library...');
            await this.loadLayout(false);
        }
        
        // Use all available charts or fallback to all chart definitions
        const chartsToShow = this.availableCharts.length > 0 
            ? this.availableCharts 
            : Object.keys(this.chartDefinitions || window.CHART_DEFINITIONS || {});
        
        // Populate available charts
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
                const chartDef = this.chartDefinitions[chartId] || window.CHART_DEFINITIONS?.[chartId];
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
        
        // Store target button for adding chart
        if (button) {
            modal.dataset.targetButton = 'true';
        }
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    /**
     * Add chart to dashboard
     */
    addChartToDashboard(chartId, targetButton = null) {
        console.log(`Adding chart to dashboard: ${chartId}`);
        
        let targetRow = null;
        
        if (targetButton) {
            targetRow = targetButton.closest('.dashboard-row');
        } else {
            // Add to last row or create new row
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
        
        // Find the columns container - it might be a nested .row or the dashboard-row itself
        let columnsContainer = targetRow.querySelector('.row:not(.dashboard-row)');
        if (!columnsContainer && targetRow.classList.contains('row')) {
            // The dashboard-row itself is the container
            columnsContainer = targetRow;
        }
        
        if (!columnsContainer) {
            console.error('Columns container not found in target row');
            return;
        }
        
        // Create new column with 50% width (col-md-6) as requested
        const colData = {
            id: `col-${chartId}-${Date.now()}`,
            chart_id: chartId,
            size: 6, // 50% width (col-md-6)
            enabled: true,
            settings: {
                chart_type: chartDef.default_type || 'bar'
            }
        };
        
        const colEl = this.createColumnElement(colData, columnsContainer.children.length);
        columnsContainer.appendChild(colEl);
        
        // Get the chart wrapper element (the one with data-chart-id)
        const chartWrapper = colEl.querySelector(`[data-chart-id="${chartId}"]`);
        if (!chartWrapper) {
            console.error('Chart wrapper not found in column element');
            return;
        }
        
        // Apply spacing to the new column
        this.updateChartSpacing(colEl, 6);
        
        // Update layout data
        if (!this.layout) this.layout = { rows: [] };
        if (!this.layout.rows) this.layout.rows = [];
        
        // Find or create row in layout
        const rowId = targetRow.dataset.rowId || `row-${Date.now()}`;
        let rowData = this.layout.rows.find(r => r.id === rowId);
        if (!rowData) {
            rowData = { id: rowId, columns: [] };
            this.layout.rows.push(rowData);
        }
        if (!rowData.columns) rowData.columns = [];
        rowData.columns.push(colData);
        
        // Get graph container ID
        const graphContainerId = this.getGraphContainerId(chartId);
        console.log(`Rendering chart ${chartId} in container: ${graphContainerId}`);
        
        // Render chart - use the actual graph container ID
        setTimeout(() => {
            if (window.ChartRenderer && graphContainerId) {
                // Ensure the graph container exists
                let graphContainer = chartWrapper.querySelector(`#${graphContainerId}`);
                if (!graphContainer && graphContainerId) {
                    // Create the graph container element if it wasn't created in createColumnElement
                    graphContainer = document.createElement('div');
                    graphContainer.id = graphContainerId;
                    graphContainer.style.height = '500px';
                    graphContainer.style.width = '100%';
                    // Insert before the toolbar
                    const toolbar = chartWrapper.querySelector('.chart-toolbar');
                    if (toolbar) {
                        chartWrapper.insertBefore(graphContainer, toolbar);
                    } else {
                        chartWrapper.appendChild(graphContainer);
                    }
                    console.log(`Created graph container: ${graphContainerId}`);
                }
                
                // Render the chart
                const success = window.ChartRenderer.renderChart(
                    chartId,
                    chartDef.default_type || 'bar',
                    graphContainerId,
                    {}
                );
                
                if (!success) {
                    console.error(`Failed to render chart: ${chartId}`);
                } else {
                    console.log(`Successfully rendered chart: ${chartId}`);
                }
            } else {
                console.error(`ChartRenderer not available or graph container ID not found for: ${chartId}`);
            }
        }, 200);
        
        // Reinitialize sortable
        this.setupChartSortable();
        
        // Update spacing for all charts in the row
        setTimeout(() => {
            this.applySpacingToAllCharts();
        }, 100);
        
        // Save layout
        this.saveLayout();
        
        // Show notification
        this.showNotification(`Chart "${chartDef.name}" added successfully`, 'success');
    }
    
    /**
     * Edit chart settings
     */
    editChart(chartId) {
        console.log(`Editing chart: ${chartId}`);
        this.selectedChart = chartId;
        
        // Ensure chart definitions are loaded
        if (!this.chartDefinitions || Object.keys(this.chartDefinitions).length === 0) {
            console.warn('Chart definitions not loaded, attempting to load...');
            this.loadLayout(false).then(() => {
                this.showChartSettingsModal(chartId);
            });
            return;
        }
        
        this.showChartSettingsModal(chartId);
    }
    
    /**
     * Show chart settings modal
     */
    showChartSettingsModal(chartId) {
        console.log(`showChartSettingsModal called for: ${chartId}`);
        const modal = document.getElementById('chart-settings-modal');
        if (!modal) {
            console.error('Chart settings modal not found in DOM');
            return;
        }
        
        // Try multiple sources for chart definition
        let chartDef = this.chartDefinitions?.[chartId];
        if (!chartDef) {
            chartDef = window.CHART_DEFINITIONS?.[chartId];
        }
        
        if (!chartDef) {
            console.error(`Chart definition not found for: ${chartId}`);
            console.error('Available in this.chartDefinitions:', Object.keys(this.chartDefinitions || {}));
            console.error('Available in window.CHART_DEFINITIONS:', Object.keys(window.CHART_DEFINITIONS || {}));
            
            // Try to load definitions and retry
            if (!this.chartDefinitions || Object.keys(this.chartDefinitions).length === 0) {
                console.warn('Loading chart definitions and retrying...');
                this.loadLayout(false).then(() => {
                    if (this.chartDefinitions && this.chartDefinitions[chartId]) {
                        window.CHART_DEFINITIONS = this.chartDefinitions;
                        this.showChartSettingsModal(chartId); // Retry
                    } else {
                        alert(`Chart settings not available for this chart. Please try again.`);
                    }
                });
                return;
            }
            alert(`Chart settings not available for this chart. Please try again.`);
            return;
        }
        
        console.log('Chart definition found:', chartDef);
        const chartElement = document.querySelector(`[data-chart-id="${chartId}"]`);
        
        // Populate modal with current settings
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
                
                // Set current selected type
                const currentType = this.getCurrentChartType(chartId) || chartDef.default_type;
                typeSelect.value = currentType;
            } else {
                console.warn('supported_types not found in chartDef:', chartDef);
            }
        }
        
        // Set current size in size select
        const sizeSelect = modal.querySelector('#chart-size-select');
        if (sizeSelect && chartElement) {
            const colElement = chartElement.closest('[class*="col-md-"]');
            if (colElement) {
                const currentSize = parseInt(colElement.className.match(/col-md-(\d+)/)?.[1] || '6');
                sizeSelect.value = currentSize;
            }
        }
        
        console.log('Showing chart settings modal');
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    /**
     * Apply chart settings
     */
    applyChartSettings() {
        if (!this.selectedChart) {
            console.error('No chart selected');
            return;
        }
        
        console.log(`Applying settings for chart: ${this.selectedChart}`);
        
        const modal = document.getElementById('chart-settings-modal');
        const type = modal.querySelector('#chart-type-select')?.value;
        const size = modal.querySelector('#chart-size-select')?.value;
        
        console.log(`Settings - Type: ${type}, Size: ${size}`);
        
        // Find the chart element using the selected chart ID
        const chartElement = document.querySelector(`[data-chart-id="${this.selectedChart}"]`);
        if (!chartElement) {
            console.error(`Chart element not found for chartId: ${this.selectedChart}`);
            return;
        }
        
        console.log(`Found chart element: ${chartElement.id || 'no-id'}, data-chart-id: ${chartElement.dataset.chartId}`);
        
        const colElement = chartElement.closest('[class*="col-md-"]');
        const oldSize = colElement ? parseInt(colElement.className.match(/col-md-(\d+)/)?.[1] || '6') : null;
        const newSize = size ? parseInt(size) : null;
        const sizeChanged = oldSize !== null && newSize !== null && oldSize !== newSize;
        
        // Get current chart type from layout or default
        const chartDef = this.chartDefinitions[this.selectedChart] || window.CHART_DEFINITIONS?.[this.selectedChart];
        const currentType = this.getCurrentChartType(this.selectedChart) || chartDef?.default_type || 'bar';
        const typeChanged = type && type !== currentType;
        
        console.log(`Size change - Old: ${oldSize}, New: ${newSize}, Changed: ${sizeChanged}`);
        console.log(`Type change - Current: ${currentType}, New: ${type}, Changed: ${typeChanged}`);
        
        // Update column size
        if (colElement && newSize) {
            colElement.className = colElement.className.replace(/col-md-\d+/, `col-md-${newSize}`);
            console.log(`Updated column size to: col-md-${newSize}`);
            
            // After updating this column, recalculate spacing for ALL columns in the row
            // This ensures spacing is correct if total exceeds 12 or wrapping occurs
            const rowElement = colElement.closest('.dashboard-row');
            if (rowElement) {
                const columns = rowElement.querySelectorAll('[class*="col-md-"]');
                columns.forEach(col => {
                    const colSize = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '6');
                    this.updateChartSpacing(col, colSize);
                });
            } else {
                // Fallback: just update this column if row not found
                this.updateChartSpacing(colElement, newSize);
            }
        }
        
        const containerId = chartElement.id || `chart-${this.selectedChart}`;
        
        // Map chart IDs to their actual graph container IDs
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
        
        const graphContainerId = chartContainerMap[this.selectedChart];
        console.log(`Graph container ID: ${graphContainerId}`);
        
        // Update layout data
        if (this.layout && this.layout.rows) {
            this.layout.rows.forEach(row => {
                if (row.columns) {
                    row.columns.forEach(col => {
                        if (col.chart_id === this.selectedChart) {
                            if (newSize) col.size = newSize;
                            if (type) {
                                if (!col.settings) col.settings = {};
                                col.settings.chart_type = type;
                            }
                        }
                    });
                }
            });
        }
        
        // Ensure chart definitions are available globally BEFORE rendering
        // CRITICAL: Set window.CHART_DEFINITIONS with full definitions from dashboard_config.py
        if (!window.CHART_DEFINITIONS || Object.keys(window.CHART_DEFINITIONS).length === 0) {
            // Try to get from this.chartDefinitions first
            if (this.chartDefinitions && Object.keys(this.chartDefinitions).length > 0) {
                window.CHART_DEFINITIONS = this.chartDefinitions;
                console.log('Set window.CHART_DEFINITIONS from this.chartDefinitions');
            } 
            // Fallback: Try to load from API
            else {
                console.warn('Chart definitions not loaded, attempting to load...');
                this.loadLayout(false).then(() => {
                    if (this.chartDefinitions && Object.keys(this.chartDefinitions).length > 0) {
                        window.CHART_DEFINITIONS = this.chartDefinitions;
                        console.log('Loaded and set window.CHART_DEFINITIONS from API');
                        // Retry applying settings after definitions are loaded
                        setTimeout(() => this.applyChartSettings(), 100);
                    }
                });
                return; // Exit early, will retry after loading
            }
        }
        
        // Double-check the specific chart definition exists
        if (!window.CHART_DEFINITIONS[this.selectedChart]) {
            console.error(`Chart definition not found for ${this.selectedChart}. Available charts:`, Object.keys(window.CHART_DEFINITIONS || {}));
            console.error('Current window.CHART_DEFINITIONS:', window.CHART_DEFINITIONS);
            return;
        }
        
        // Re-render chart with new type ONLY if type actually changed
        if (typeChanged && window.ChartRenderer && graphContainerId) {
            console.log(`Chart type changed from ${currentType} to ${type}, re-rendering chart: ${this.selectedChart}`);
            
            // Destroy existing chart instance
            window.ChartRenderer.destroyChart(graphContainerId);
            
            // Wait for destruction to complete, then re-render
            setTimeout(() => {
                const success = window.ChartRenderer.renderChart(this.selectedChart, type, graphContainerId, {});
                if (!success) {
                    console.error(`Failed to render chart: ${this.selectedChart} with type: ${type}`);
                } else {
                    console.log(`Successfully re-rendered chart: ${this.selectedChart} with type: ${type}`);
                }
            }, 100);
        } else if (sizeChanged && !typeChanged) {
            // If only size changed, resize existing charts without re-rendering
            console.log(`Only size changed (${oldSize} -> ${newSize}), resizing chart: ${this.selectedChart} (NO re-render)`);
            setTimeout(() => {
                this.resizeChart(containerId);
            }, 100);
        } else if (!typeChanged && !sizeChanged) {
            console.log(`No changes detected, skipping resize/render`);
        }
        
        // IMPORTANT: Only close modal if settings were successfully applied
        // Don't close if there were errors
        
        // Close modal
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
        
        this.saveLayout();
    }
    
    /**
     * Get current chart type from layout
     */
    getCurrentChartType(chartId) {
        if (!this.layout || !this.layout.rows) return null;
        
        for (const row of this.layout.rows) {
            if (row.columns) {
                for (const col of row.columns) {
                    if (col.chart_id === chartId && col.settings && col.settings.chart_type) {
                        return col.settings.chart_type;
                    }
                }
            }
        }
        
        return null;
    }
    
    /**
     * Resize chart after container size change
     */
    resizeChart(containerId) {
        console.log(`Resizing chart with containerId: ${containerId}`);
        
        // Find the actual chart container element (the wrapper with data-chart-id)
        const chartElement = document.getElementById(containerId);
        if (!chartElement) {
            console.warn(`Chart container not found: ${containerId}`);
            return;
        }
        
        // Get the chart ID from the element - this is the KEY to identify the correct chart
        const chartId = chartElement.dataset.chartId || containerId.replace('chart-', '');
        console.log(`Detected chartId: ${chartId}`);
        
        if (!chartId) {
            console.error('Could not determine chartId from element');
            return;
        }
        
        // Map chart IDs to their actual graph container IDs
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
        
        // Find the specific graph container ID for this chart
        const graphContainerId = chartContainerMap[chartId];
        if (!graphContainerId) {
            console.warn(`No graph container ID mapped for chartId: ${chartId}`);
            return;
        }
        
        console.log(`Looking for graph container: ${graphContainerId}`);
        
        // Find the specific graph container WITHIN this chart element (scoped search)
        const graphContainer = chartElement.querySelector(`[id="${graphContainerId}"]`);
        if (!graphContainer) {
            console.warn(`Graph container not found: ${graphContainerId} within chart element`);
            // Try to find it by ID anywhere (fallback)
            const fallbackContainer = document.getElementById(graphContainerId);
            if (fallbackContainer) {
                console.log(`Found graph container outside chart element, using fallback`);
                this.resizeSingleContainer(fallbackContainer, chartId);
                return;
            }
            return;
        }
        
        console.log(`Found graph container: ${graphContainer.id}`);
        
        // Resize this specific container
        this.resizeSingleContainer(graphContainer, chartId);
        
        // Also try to find canvas elements within this specific container
        const canvasElements = graphContainer.querySelectorAll('canvas');
        canvasElements.forEach(canvas => {
            this.resizeSingleContainer(canvas, chartId);
        });
        
        // Trigger window resize event to help charts that listen to it
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 150);
    }
    
    /**
     * Resize a single chart container element
     */
    resizeSingleContainer(element, chartId) {
        if (!element || !element.id) return;
        
        let resizeAttempted = false;
        
        // Try Chart.js resize from window.chartInstances
        if (window.chartInstances && window.chartInstances[element.id]) {
            const chartInstance = window.chartInstances[element.id];
            if (chartInstance && typeof chartInstance.resize === 'function') {
                chartInstance.resize();
                resizeAttempted = true;
                console.log(`✓ Resized Chart.js instance for: ${element.id} (chart: ${chartId})`);
            }
        }
        
        // Try Chart.js global registry (using canvas element)
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
        
        // Try ECharts resize
        if (typeof echarts !== 'undefined' && echarts.getInstanceByDom) {
            const echartsInstance = echarts.getInstanceByDom(element);
            if (echartsInstance && typeof echartsInstance.resize === 'function') {
                echartsInstance.resize();
                resizeAttempted = true;
                console.log(`✓ Resized ECharts instance for: ${element.id} (chart: ${chartId})`);
            }
        }
        
        // If no resize was attempted, try to re-render the chart
        if (!resizeAttempted) {
            console.log(`No resize method found for ${element.id}, attempting to re-render chart: ${chartId}`);
            const chartDef = this.chartDefinitions[chartId] || window.CHART_DEFINITIONS?.[chartId];
            const chartType = chartDef?.default_type || 'bar';
            
            if (window.ChartRenderer) {
                window.ChartRenderer.destroyChart(element.id);
                setTimeout(() => {
                    window.ChartRenderer.renderChart(chartId, chartType, element.id, {});
                }, 100);
            }
        }
    }
    
    /**
     * Duplicate chart
     */
    duplicateChart(chartId) {
        const chartElement = document.querySelector(`[data-chart-id="${chartId}"]`);
        if (!chartElement) return;
        
        const row = chartElement.closest('.dashboard-row');
        if (!row) return;
        
        this.addChartToDashboard(chartId);
    }
    
    /**
     * Remove chart
     */
    removeChart(chartId) {
        if (!confirm('Remove this chart from dashboard?')) {
            return;
        }
        
        const chartElement = document.querySelector(`[data-chart-id="${chartId}"]`);
        if (!chartElement) return;
        
        const colElement = chartElement.closest('[class*="col-md-"]');
        if (colElement) {
            colElement.remove();
        }
        
        this.saveLayout();
    }
    
    /**
     * Delete row
     */
    deleteRow(button) {
        const row = button.closest('.dashboard-row');
        if (!row) return;
        
        if (!confirm('Delete this row and all its charts?')) {
            return;
        }
        
        row.remove();
        this.saveLayout();
    }
    
    /**
     * Update column sizes after drag
     */
    updateColumnSizes() {
        document.querySelectorAll('.dashboard-row').forEach(row => {
            const columns = row.querySelectorAll('[class*="col-md-"]');
            const totalSize = Array.from(columns).reduce((sum, col) => {
                const size = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '6');
                return sum + size;
            }, 0);
            
            // If total size is not 12, adjust
            if (totalSize !== 12 && columns.length > 0) {
                const sizePerCol = Math.floor(12 / columns.length);
                columns.forEach(col => {
                    const oldSize = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '6');
                    col.className = col.className.replace(/col-md-\d+/, `col-md-${sizePerCol}`);
                });
            }
            
            // Always update spacing for all columns after size changes
            // This ensures spacing is correct even if total exceeds 12
            columns.forEach(col => {
                const size = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '6');
                this.updateChartSpacing(col, size);
            });
        });
    }
    
    /**
     * Get graph container ID for a chart
     */
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
    
    /**
     * Update chart spacing based on column size
     * Adds margin-bottom for charts that:
     * - Are full width (size 12), OR
     * - Are in a row where total column size exceeds 12 (wrapping occurs)
     */
    updateChartSpacing(colElement, size) {
        if (!colElement) return;
        
        // Find the parent row
        const rowElement = colElement.closest('.dashboard-row');
        if (!rowElement) {
            // If no row found, just apply basic logic
            if (size === 12) {
                colElement.style.marginBottom = '25px';
            } else {
                colElement.style.marginBottom = '';
            }
            return;
        }
        
        // Calculate total column size in the row
        const columns = rowElement.querySelectorAll('[class*="col-md-"]');
        let totalSize = 0;
        columns.forEach(col => {
            const colSize = parseInt(col.className.match(/col-md-(\d+)/)?.[1] || '0');
            totalSize += colSize;
        });
        
        // If total size exceeds 12 OR chart is full width (size 12), add margin-bottom
        if (totalSize > 12 || size === 12) {
            colElement.style.marginBottom = '25px';
        } else {
            // Remove margin-bottom for charts that don't need spacing
            colElement.style.marginBottom = '';
        }
    }
    
    /**
     * Toggle preview mode
     */
    togglePreview() {
        document.body.classList.toggle('dashboard-preview-mode');
        const isPreview = document.body.classList.contains('dashboard-preview-mode');
        this.showNotification(isPreview ? 'Preview mode enabled' : 'Preview mode disabled', 'info');
    }
    
    /**
     * Get CSRF token
     */
    getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        if (cookieValue) return cookieValue;
        
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : '';
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Simple notification implementation
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

// Initialize on page load - but delay to let existing charts render first
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardCustomizer = new DashboardCustomizer();
    // Wait for existing charts to render before initializing
    setTimeout(() => {
        window.dashboardCustomizer.init();
    }, 500);
});

