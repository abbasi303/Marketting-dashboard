// Enhanced visualization configuration and utilities
const VisualizationConfig = {
    // Color schemes for consistent branding
    colorSchemes: {
        primary: [
            'rgba(54, 162, 235, 0.7)',  // Blue
            'rgba(75, 192, 192, 0.7)',  // Teal
            'rgba(255, 99, 132, 0.7)',  // Red
            'rgba(255, 159, 64, 0.7)',  // Orange
            'rgba(255, 205, 86, 0.7)',  // Yellow
            'rgba(153, 102, 255, 0.7)', // Purple
            'rgba(201, 203, 207, 0.7)'  // Grey
        ],
        borders: [
            'rgba(54, 162, 235, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(255, 99, 132, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(255, 205, 86, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(201, 203, 207, 1)'
        ],
        funnel: {
            backgrounds: [
                'rgba(54, 162, 235, 0.7)',  // Impressions (Blue)
                'rgba(75, 192, 192, 0.7)',  // Clicks (Teal)
                'rgba(255, 99, 132, 0.7)'   // Conversions (Red)
            ],
            borders: [
                'rgba(54, 162, 235, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(255, 99, 132, 1)'
            ]
        }
    },
    
    // Chart type-specific default configurations
    chartDefaults: {
        funnel: {
            type: 'bar',
            options: {
                indexAxis: 'y',
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw || 0;
                                return `${context.label}: ${formatLargeNumber(value)}`;
                            },
                            afterLabel: function(context) {
                                const dataset = context.chart.data.datasets[0];
                                const currentIndex = context.dataIndex;
                                
                                // Don't show conversion rate for the first item (no previous step)
                                if (currentIndex === 0) return null;
                                
                                const currentValue = dataset.data[currentIndex];
                                const previousValue = dataset.data[currentIndex - 1];
                                const conversionRate = (currentValue / previousValue * 100).toFixed(2);
                                
                                return `Conversion from previous: ${conversionRate}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        },
        horizontalComparison: {
            type: 'bar',
            options: {
                indexAxis: 'y',
                maintainAspectRatio: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw || 0;
                                return `${context.dataset.label}: ${value.toFixed(2)}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        },
        conversionMetrics: {
            type: 'bar',
            options: {
                maintainAspectRatio: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw || 0;
                                return `${context.dataset.label}: ${value.toFixed(2)}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            drawBorder: false
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        }
    },
    
    // Data transformation functions
    transforms: {
        // Calculate funnel percentages for better visualization
        calculateFunnelPercentages: function(data) {
            if (!data || !data.impressions) return null;
            
            const result = {
                labels: ['Impressions', 'Clicks', 'Conversions'],
                values: [data.impressions, data.clicks, data.conversions],
                percentages: [100]
            };
            
            // Calculate percentages relative to the previous step
            if (data.impressions > 0) {
                result.percentages.push((data.clicks / data.impressions * 100).toFixed(2));
            } else {
                result.percentages.push(0);
            }
            
            if (data.clicks > 0) {
                result.percentages.push((data.conversions / data.clicks * 100).toFixed(2));
            } else {
                result.percentages.push(0);
            }
            
            return result;
        },
        
        // Format campaign data to include meaningful metrics
        enhanceCampaignData: function(data, maxItems = 6) {
            if (!data || data.length === 0) return null;
            
            // Sort by ROI descending
            const sorted = [...data].sort((a, b) => (b.roi || 0) - (a.roi || 0));
            const sliced = sorted.slice(0, maxItems);
            
            // Clean up campaign names
            return sliced.map(item => {
                return {
                    ...item,
                    campaign_name: item.campaign_name || item.campaign || 'Unnamed Campaign',
                    roi: item.roi || 0,
                    conversion_rate: item.conversion_rate || 0
                };
            });
        },
        
        // Format channel data to include cost metrics
        enhanceChannelData: function(data, maxItems = 6) {
            if (!data || data.length === 0) return null;
            
            // Sort by conversion rate descending
            const sorted = [...data].sort((a, b) => (b.conversion_rate || 0) - (a.conversion_rate || 0));
            const sliced = sorted.slice(0, maxItems);
            
            // Clean up channel names and ensure we have all needed metrics
            return sliced.map(item => {
                return {
                    ...item,
                    channel: item.channel || 'Unknown Channel',
                    conversion_rate: item.conversion_rate || 0,
                    acquisition_cost: item.acquisition_cost || 0,
                    efficiency: item.acquisition_cost ? (item.conversion_rate / item.acquisition_cost).toFixed(2) : 'N/A'
                };
            });
        }
    }
};

// Function to render enhanced funnel visualization
function renderEnhancedFunnel(elementId, data) {
    const processedData = VisualizationConfig.transforms.calculateFunnelPercentages(data);
    if (!processedData) return;
    
    // Create funnel with conversion percentages
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Destroy existing chart if it exists
    if (ChartManager.getChart(elementId)) {
        ChartManager.destroyChart(elementId);
    }
    
    // Create new chart with enhanced visualization
    return ChartManager.createChart(elementId, 'bar', {
        labels: processedData.labels,
        datasets: [{
            label: 'Count',
            data: processedData.values,
            backgroundColor: VisualizationConfig.colorSchemes.funnel.backgrounds,
            borderColor: VisualizationConfig.colorSchemes.funnel.borders,
            borderWidth: 1
        }]
    }, {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            title: {
                display: true,
                text: 'Marketing Funnel'
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const value = context.raw || 0;
                        return `Count: ${formatLargeNumber(value)}`;
                    },
                    afterLabel: function(context) {
                        const index = context.dataIndex;
                        if (index === 0) return null; // No conversion rate for first step
                        return `Conversion Rate: ${processedData.percentages[index]}%`;
                    }
                }
            },
            // Add custom plugin to display percentages on the bars
            datalabels: {
                display: true,
                align: 'end',
                formatter: function(value, context) {
                    const index = context.dataIndex;
                    if (index === 0) return formatLargeNumber(value);
                    return `${processedData.percentages[index]}%`;
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return formatLargeNumber(value);
                    }
                }
            }
        }
    });
}

// Function to render enhanced campaign comparison
function renderEnhancedCampaignComparison(elementId, data) {
    const processedData = VisualizationConfig.transforms.enhanceCampaignData(data);
    if (!processedData) return;
    
    const campaignNames = processedData.map(c => c.campaign_name);
    const rois = processedData.map(c => c.roi);
    const conversionRates = processedData.map(c => c.conversion_rate);
    
    // Destroy existing chart if it exists
    if (ChartManager.getChart(elementId)) {
        ChartManager.destroyChart(elementId);
    }
    
    // Create new chart with enhanced visualization
    return ChartManager.createChart(elementId, 'bar', {
        labels: campaignNames,
        datasets: [{
            label: 'ROI (%)',
            data: rois,
            backgroundColor: VisualizationConfig.colorSchemes.primary[0],
            borderColor: VisualizationConfig.colorSchemes.borders[0],
            borderWidth: 1
        }, {
            label: 'Conversion Rate (%)',
            data: conversionRates,
            backgroundColor: VisualizationConfig.colorSchemes.primary[2],
            borderColor: VisualizationConfig.colorSchemes.borders[2],
            borderWidth: 1
        }]
    }, {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            title: {
                display: true,
                text: 'Top Campaigns by ROI'
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const value = context.raw || 0;
                        return `${context.dataset.label}: ${value.toFixed(2)}%`;
                    }
                }
            }
        },
        scales: {
            x: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Percentage (%)'
                }
            }
        }
    });
}

// Function to render enhanced channel performance
function renderEnhancedChannelPerformance(elementId, data) {
    const processedData = VisualizationConfig.transforms.enhanceChannelData(data);
    if (!processedData) return;
    
    const channelNames = processedData.map(c => c.channel);
    const conversionRates = processedData.map(c => c.conversion_rate);
    const acquisitionCosts = processedData.map(c => c.acquisition_cost);
    
    // Calculate efficiency score (conversion rate / cost) - higher is better
    const efficiencyScores = processedData.map(c => 
        c.acquisition_cost > 0 ? c.conversion_rate / c.acquisition_cost * 5 : 0
    );
    
    // Destroy existing chart if it exists
    if (ChartManager.getChart(elementId)) {
        ChartManager.destroyChart(elementId);
    }
    
    // Create new chart with enhanced visualization
    return ChartManager.createChart(elementId, 'bar', {
        labels: channelNames,
        datasets: [{
            label: 'Conversion Rate (%)',
            data: conversionRates,
            backgroundColor: VisualizationConfig.colorSchemes.primary[2],
            borderColor: VisualizationConfig.colorSchemes.borders[2],
            borderWidth: 1,
            order: 1
        }, {
            label: 'Efficiency Score',
            data: efficiencyScores,
            backgroundColor: VisualizationConfig.colorSchemes.primary[1],
            borderColor: VisualizationConfig.colorSchemes.borders[1],
            borderWidth: 1,
            type: 'line',
            order: 0,
            yAxisID: 'y1'
        }]
    }, {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            title: {
                display: true,
                text: 'Channel Performance & Efficiency'
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const value = context.raw || 0;
                        const index = context.dataIndex;
                        
                        if (context.dataset.label === 'Efficiency Score') {
                            return `Efficiency Score: ${value.toFixed(2)} (higher is better)`;
                        } else {
                            return `Conversion Rate: ${value.toFixed(2)}%`;
                        }
                    },
                    afterLabel: function(context) {
                        const index = context.dataIndex;
                        return `Cost per Acquisition: $${acquisitionCosts[index].toFixed(2)}`;
                    }
                }
            }
        },
        scales: {
            x: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Conversion Rate (%)'
                }
            },
            y: {
                grid: {
                    display: false
                }
            },
            y1: {
                position: 'right',
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Efficiency Score'
                },
                grid: {
                    display: false
                }
            }
        }
    });
}
