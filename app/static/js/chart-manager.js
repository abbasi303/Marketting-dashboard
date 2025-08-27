// Enhanced chart rendering manager to prevent the growing chart issue
const ChartManager = {
    // Store chart instances for cleanup
    instances: {},
    
    // Create a new chart with proper cleanup of old instances
    createChart(canvasId, type, data, options = {}) {
        // Combine with default options from our config
        const combinedOptions = Object.assign({}, getDefaultChartConfig(), options);
        
        // If there's an old chart instance with this ID, destroy it
        if (this.instances[canvasId]) {
            console.log(`Destroying old chart instance for ${canvasId}`);
            this.instances[canvasId].destroy();
            delete this.instances[canvasId];
        }
        
        // Reset canvas to ensure clean state
        const ctx = resetCanvas(canvasId);
        
        // Create and store new chart instance
        console.log(`Creating new ${type} chart for ${canvasId}`);
        this.instances[canvasId] = new Chart(ctx, {
            type: type,
            data: data,
            options: combinedOptions
        });
        
        return this.instances[canvasId];
    },
    
    // Get an existing chart instance or null if not found
    getChart(canvasId) {
        return this.instances[canvasId] || null;
    },
    
    // Destroy a specific chart instance
    destroyChart(canvasId) {
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
            delete this.instances[canvasId];
            return true;
        }
        return false;
    },
    
    // Clear all chart instances
    clearAll() {
        Object.keys(this.instances).forEach(id => {
            this.instances[id].destroy();
        });
        this.instances = {};
    }
};

// Function to safely calculate chart Y-axis max to prevent excessive growth
function calculateYAxisMax(values, scaleFactor = 1.2) {
    const maxValue = Math.max(...values);
    return Math.ceil(maxValue * scaleFactor);
}

// Format large numbers for readability in charts
function formatLargeNumber(value) {
    if (value >= 1000000) {
        return (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
        return (value / 1000).toFixed(1) + 'K';
    }
    return value;
}
