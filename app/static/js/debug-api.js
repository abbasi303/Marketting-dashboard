// API debugging script
(function() {
    console.log('API Debug script loaded');
    
    // Function to test API endpoints
    async function testApiEndpoints() {
        try {
            console.group('API Endpoint Tests');
            
            // Test health check endpoint
            try {
                console.log('Testing /api/healthz...');
                const healthResponse = await fetch('/api/healthz');
                if (healthResponse.ok) {
                    const healthData = await healthResponse.json();
                    console.log('✓ Health check passed:', healthData);
                } else {
                    console.error('✗ Health check failed:', healthResponse.status);
                }
            } catch (err) {
                console.error('✗ Health check error:', err);
            }
            
            // Test main dashboard endpoint
            try {
                console.log('Testing /api/dashboard.json...');
                const dashboardResponse = await fetch('/api/dashboard.json');
                if (dashboardResponse.ok) {
                    const dashboardData = await dashboardResponse.json();
                    console.log('✓ Dashboard API passed:', dashboardData);
                    
                    // List available sections
                    if (dashboardData.sections_available) {
                        console.log('Available sections:', dashboardData.sections_available);
                        
                        // Test each section
                        for (const section of dashboardData.sections_available) {
                            try {
                                console.log(`Testing section: /api/dashboard/${section}.json...`);
                                const sectionResponse = await fetch(`/api/dashboard/${section}.json`);
                                if (sectionResponse.ok) {
                                    const sectionData = await sectionResponse.json();
                                    console.log(`✓ Section ${section} passed:`, sectionData);
                                } else {
                                    console.error(`✗ Section ${section} failed:`, sectionResponse.status);
                                }
                            } catch (err) {
                                console.error(`✗ Section ${section} error:`, err);
                            }
                        }
                    }
                } else {
                    console.error('✗ Dashboard API failed:', dashboardResponse.status);
                    // Try to read error message
                    try {
                        const errorData = await dashboardResponse.json();
                        console.error('Error details:', errorData);
                    } catch {
                        console.error('Could not parse error response');
                    }
                }
            } catch (err) {
                console.error('✗ Dashboard API error:', err);
            }
            
            console.groupEnd();
        } catch (err) {
            console.error('Error running API tests:', err);
        }
    }
    
    // Run tests when the page loads
    window.addEventListener('load', testApiEndpoints);
})();
