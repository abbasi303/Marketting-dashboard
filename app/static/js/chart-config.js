// Global chart configuration
function getDefaultChartConfig() {
    return {
        responsive: true,
        maintainAspectRatio: true, // Change to true to respect container dimensions
        animation: {
            duration: 500 // Shorter animation time
        },
        devicePixelRatio: 1, // Force 1:1 pixel ratio to prevent scaling issues
        resizeDelay: 0, // Respond immediately to resize events
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    boxWidth: 12,
                    font: {
                        size: 11 // Smaller font for legend
                    }
                }
            }
        },
        layout: {
            padding: {
                top: 5,
                right: 10,
                bottom: 5,
                left: 10
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    maxTicksLimit: 8, // Limit the number of ticks on Y-axis
                    font: {
                        size: 10 // Smaller font for axis labels
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        size: 10 // Smaller font for axis labels
                    }
                }
            }
        }
    };
}
