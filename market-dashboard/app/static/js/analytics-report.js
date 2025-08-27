/**
 * Analytics Report JS
 * Handles the loading and rendering of the marketing analytics report
 */

// Configuration for charts
const chartColors = [
    'rgba(54, 162, 235, 0.8)', 
    'rgba(255, 99, 132, 0.8)',
    'rgba(255, 206, 86, 0.8)',
    'rgba(75, 192, 192, 0.8)',
    'rgba(153, 102, 255, 0.8)',
    'rgba(255, 159, 64, 0.8)',
    'rgba(199, 199, 199, 0.8)'
];

// Store chart instances
const chartInstances = {};

/**
 * Load the analytics report data from the server
 */
function loadAnalyticsReport() {
    showLoading();

    // Fetch report data from API
    fetch('/analytics-report')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            renderAnalyticsReport(data);
            hideLoading();
        })
        .catch(error => {
            console.error('Error fetching analytics report:', error);
            hideLoading();
            showError('Failed to load analytics report. Please try again later.');
        });
}

/**
 * Render the analytics report with the provided data
 * @param {Object} data - The analytics report data from the server
 */
function renderAnalyticsReport(data) {
    if (data.error) {
        showError(data.error);
        return;
    }

    // Update generated date
    document.getElementById('generatedDate').textContent = data.generated_at;

    // Render metrics summary
    renderMetricsSummary(data);

    // Render funnel analysis
    if (data.summary && data.summary.funnel) {
        renderFunnelAnalysis(data.summary.funnel);
    }

    // Render campaign analysis
    if (data.summary && data.summary.campaigns) {
        renderCampaignAnalysis(data.summary.campaigns);
    }

    // Render channel analysis
    if (data.summary && data.summary.channels) {
        renderChannelAnalysis(data.summary.channels);
    }

    // Render insights and recommendations
    renderInsights(data.insights || []);
    renderRecommendations(data.recommendations || []);

    // Render opportunity analysis
    renderOpportunityAnalysis(data);
}

/**
 * Render the metrics summary cards
 * @param {Object} data - The analytics report data
 */
function renderMetricsSummary(data) {
    const container = document.getElementById('metricsSummary');
    container.innerHTML = '';

    // Add conversion rate metric
    if (data.summary && data.summary.conversion_rates) {
        const conversionRates = data.summary.conversion_rates;
        const metrics = conversionRates.metrics || [];

        metrics.forEach(metric => {
            const card = document.createElement('div');
            card.className = 'metric-card';

            const statusClass = metric.status === 'good' ? 'positive' : 'negative';
            
            card.innerHTML = `
                <div class="metric-label">${metric.name}</div>
                <div class="metric-value">${metric.value.toFixed(2)}%</div>
                <div class="metric-change ${statusClass}">
                    ${metric.status === 'good' ? 
                        `<i class="fas fa-arrow-up"></i> Above benchmark (${metric.benchmark}%)` : 
                        `<i class="fas fa-arrow-down"></i> Below benchmark (${metric.benchmark}%)`}
                </div>
            `;
            container.appendChild(card);
        });
    }

    // Add campaign metrics
    if (data.summary && data.summary.campaigns) {
        const campaigns = data.summary.campaigns;
        
        if (campaigns.average_roi !== null) {
            const card = document.createElement('div');
            card.className = 'metric-card';
            card.innerHTML = `
                <div class="metric-label">Average Campaign ROI</div>
                <div class="metric-value">${campaigns.average_roi.toFixed(2)}%</div>
            `;
            container.appendChild(card);
        }

        if (campaigns.total_cost !== null) {
            const card = document.createElement('div');
            card.className = 'metric-card';
            card.innerHTML = `
                <div class="metric-label">Total Campaign Spend</div>
                <div class="metric-value">$${campaigns.total_cost.toLocaleString()}</div>
            `;
            container.appendChild(card);
        }
    }

    // Add channel metrics
    if (data.summary && data.summary.channels) {
        const channels = data.summary.channels;
        
        if (channels.average_acquisition_cost !== null) {
            const card = document.createElement('div');
            card.className = 'metric-card';
            card.innerHTML = `
                <div class="metric-label">Avg. Customer Acquisition Cost</div>
                <div class="metric-value">$${channels.average_acquisition_cost.toFixed(2)}</div>
            `;
            container.appendChild(card);
        }
    }
}

/**
 * Render the funnel analysis section
 * @param {Object} funnelData - The funnel analysis data
 */
function renderFunnelAnalysis(funnelData) {
    // Render funnel chart
    if (funnelData.stages && funnelData.stages.length > 0) {
        renderFunnelChart(funnelData.stages);
    }

    // Render drop-offs
    if (funnelData.drop_offs && funnelData.drop_offs.length > 0) {
        const dropoffsList = document.getElementById('dropoffsList');
        dropoffsList.innerHTML = '';

        funnelData.drop_offs.forEach(dropoff => {
            const item = document.createElement('div');
            item.className = 'dropoff-item';
            
            // Determine severity class based on drop-off percentage
            let severityClass = 'info';
            if (dropoff.percent > 80) {
                severityClass = 'danger';
            } else if (dropoff.percent > 50) {
                severityClass = 'warning';
            }
            
            item.classList.add(severityClass);
            
            item.innerHTML = `
                <strong>${dropoff.from} → ${dropoff.to}:</strong> 
                ${dropoff.percent.toFixed(2)}% drop-off 
                (${dropoff.absolute.toLocaleString()} users)
            `;
            
            dropoffsList.appendChild(item);
        });
    }
}

/**
 * Render the funnel chart
 * @param {Array} stages - The funnel stages data
 */
function renderFunnelChart(stages) {
    const ctx = document.getElementById('funnelChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (chartInstances.funnelChart) {
        chartInstances.funnelChart.destroy();
    }
    
    const labels = stages.map(stage => stage.name);
    const values = stages.map(stage => stage.value);
    
    chartInstances.funnelChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Users',
                data: values,
                backgroundColor: chartColors,
                borderColor: chartColors.map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Marketing Funnel'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toLocaleString();
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

/**
 * Render the campaign analysis section
 * @param {Object} campaignData - The campaign analysis data
 */
function renderCampaignAnalysis(campaignData) {
    // Render campaign ROI chart
    if (campaignData.top_campaigns && campaignData.bottom_campaigns) {
        renderCampaignRoiChart(campaignData);
    }
    
    // Render campaign performance table
    const campaignTable = document.getElementById('campaignTable');
    const tbody = campaignTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    if (campaignData.top_campaigns) {
        campaignData.top_campaigns.forEach(campaign => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${campaign}</td>
                <td>High</td>
                <td><span class="status-indicator status-good"></span> Good</td>
            `;
            tbody.appendChild(row);
        });
    }
    
    if (campaignData.bottom_campaigns) {
        campaignData.bottom_campaigns.forEach(campaign => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${campaign}</td>
                <td>Low</td>
                <td><span class="status-indicator status-poor"></span> Needs Improvement</td>
            `;
            tbody.appendChild(row);
        });
    }
}

/**
 * Render the campaign ROI chart
 * @param {Object} campaignData - The campaign analysis data
 */
function renderCampaignRoiChart(campaignData) {
    const ctx = document.getElementById('campaignRoiChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (chartInstances.campaignRoiChart) {
        chartInstances.campaignRoiChart.destroy();
    }
    
    // Combine top and bottom campaigns
    const campaigns = [...(campaignData.top_campaigns || []), ...(campaignData.bottom_campaigns || [])];
    
    // Create mock ROI values for visualization
    // In a real app, you would use actual ROI values from the data
    const mockRoiValues = campaignData.top_campaigns.map(() => Math.floor(Math.random() * 100) + 150);
    mockRoiValues.push(...campaignData.bottom_campaigns.map(() => Math.floor(Math.random() * 80) + 20));
    
    const colors = campaigns.map((_, index) => {
        return index < campaignData.top_campaigns.length ? chartColors[0] : chartColors[1];
    });
    
    chartInstances.campaignRoiChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: campaigns,
            datasets: [{
                label: 'Campaign ROI (%)',
                data: mockRoiValues,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Campaign ROI Comparison'
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'ROI (%)'
                    }
                }
            }
        }
    });
}

/**
 * Render the channel analysis section
 * @param {Object} channelData - The channel analysis data
 */
function renderChannelAnalysis(channelData) {
    // Render channel efficiency chart
    if (channelData.most_efficient_channels) {
        renderChannelEfficiencyChart(channelData);
    }
    
    // Render channel cost chart
    if (channelData.lowest_cac_channels && channelData.highest_cac_channels) {
        renderChannelCostChart(channelData);
    }
}

/**
 * Render the channel efficiency chart
 * @param {Object} channelData - The channel analysis data
 */
function renderChannelEfficiencyChart(channelData) {
    const ctx = document.getElementById('channelEfficiencyChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (chartInstances.channelEfficiencyChart) {
        chartInstances.channelEfficiencyChart.destroy();
    }
    
    // Create mock efficiency values for visualization
    // In a real app, you would use actual efficiency values from the data
    const channels = channelData.most_efficient_channels;
    const mockEfficiencyValues = channels.map(() => Math.floor(Math.random() * 50) + 50);
    
    chartInstances.channelEfficiencyChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: channels,
            datasets: [{
                label: 'Channel Efficiency',
                data: mockEfficiencyValues,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Channel Efficiency'
                }
            },
            scales: {
                r: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Render the channel cost chart
 * @param {Object} channelData - The channel analysis data
 */
function renderChannelCostChart(channelData) {
    const ctx = document.getElementById('channelCostChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (chartInstances.channelCostChart) {
        chartInstances.channelCostChart.destroy();
    }
    
    // Combine lowest and highest CAC channels
    const channels = [...(channelData.lowest_cac_channels || []), ...(channelData.highest_cac_channels || [])];
    
    // Create mock CAC values for visualization
    // In a real app, you would use actual CAC values from the data
    const mockCacValues = channelData.lowest_cac_channels.map(() => Math.floor(Math.random() * 30) + 10);
    mockCacValues.push(...channelData.highest_cac_channels.map(() => Math.floor(Math.random() * 70) + 80));
    
    const colors = channels.map((_, index) => {
        return index < channelData.lowest_cac_channels.length ? chartColors[2] : chartColors[1];
    });
    
    chartInstances.channelCostChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: channels,
            datasets: [{
                label: 'Customer Acquisition Cost ($)',
                data: mockCacValues,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Customer Acquisition Cost by Channel'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'CAC ($)'
                    }
                }
            }
        }
    });
}

/**
 * Render the insights list
 * @param {Array} insights - The insights data
 */
function renderInsights(insights) {
    const insightsList = document.getElementById('insightsList');
    insightsList.innerHTML = '';
    
    if (insights.length === 0) {
        insightsList.innerHTML = '<p>No insights available for the current data.</p>';
        return;
    }
    
    insights.forEach(insight => {
        const item = document.createElement('div');
        item.className = 'insight-item';
        
        if (insight.type) {
            item.classList.add(insight.type);
        }
        
        item.textContent = insight.message;
        insightsList.appendChild(item);
    });
}

/**
 * Render the recommendations list
 * @param {Array} recommendations - The recommendations data
 */
function renderRecommendations(recommendations) {
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    
    if (recommendations.length === 0) {
        recommendationsList.innerHTML = '<p>No recommendations available for the current data.</p>';
        return;
    }
    
    recommendations.forEach(recommendation => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';
        
        if (recommendation.priority) {
            item.classList.add(recommendation.priority);
        }
        
        item.textContent = recommendation.message;
        recommendationsList.appendChild(item);
    });
}

/**
 * Render the opportunity analysis section
 * @param {Object} data - The complete analytics report data
 */
function renderOpportunityAnalysis(data) {
    const container = document.getElementById('opportunityAnalysis');
    container.innerHTML = '';
    
    // Create a simple opportunity analysis based on the available data
    let content = '<h3>Identified Opportunities</h3>';
    
    // Check funnel data for opportunities
    if (data.summary && data.summary.funnel) {
        const funnel = data.summary.funnel;
        
        if (funnel.drop_offs && funnel.drop_offs.length > 0) {
            const highestDropOff = funnel.drop_offs.reduce((prev, current) => 
                (prev.percent > current.percent) ? prev : current
            );
            
            content += `<p><strong>Funnel Optimization:</strong> Focus on improving the transition from 
                ${highestDropOff.from} to ${highestDropOff.to} where you're losing ${highestDropOff.percent.toFixed(1)}% 
                of your potential customers.</p>`;
        }
    }
    
    // Check campaigns data for opportunities
    if (data.summary && data.summary.campaigns) {
        const campaigns = data.summary.campaigns;
        
        if (campaigns.top_campaigns && campaigns.top_campaigns.length > 0) {
            content += `<p><strong>Campaign Scaling:</strong> Your top-performing campaigns 
                (${campaigns.top_campaigns.join(', ')}) have potential for scaling. 
                Consider increasing budget allocation to these campaigns.</p>`;
        }
    }
    
    // Check channels data for opportunities
    if (data.summary && data.summary.channels) {
        const channels = data.summary.channels;
        
        if (channels.most_efficient_channels && channels.most_efficient_channels.length > 0) {
            content += `<p><strong>Channel Optimization:</strong> The ${channels.most_efficient_channels.join(', ')} 
                channels show the best efficiency. Consider reallocating budget from less efficient channels 
                to these top performers.</p>`;
        }
    }
    
    // Add general opportunity analysis
    content += `<p><strong>Market Expansion:</strong> Based on current conversion rates and customer 
        acquisition costs, expanding into similar market segments could yield positive ROI 
        if you maintain similar performance metrics.</p>`;
    
    container.innerHTML = content;
}

/**
 * Show loading overlay
 */
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

/**
 * Show error message
 * @param {string} message - The error message to display
 */
function showError(message) {
    alert('Error: ' + message);
}

/**
 * Download the analytics report as PDF
 * Placeholder function - in a real implementation, this would generate a PDF
 */
function downloadReport() {
    alert('PDF export functionality would be implemented here in a production environment.');
}
