// Data validation and debugging utilities
const DataValidator = {
    // Check if required fields exist in data objects
    validateFunnelData: function(data) {
        console.log('Validating funnel data:', data);
        const requiredFields = ['impressions', 'clicks', 'conversions'];
        const missingFields = requiredFields.filter(field => data[field] === undefined);
        
        if (missingFields.length > 0) {
            console.error('Funnel data missing required fields:', missingFields);
            return false;
        }
        
        // Check for unreasonable values
        if (data.impressions <= 0) console.warn('Warning: Impressions should be positive');
        if (data.clicks > data.impressions) console.warn('Warning: Clicks exceed impressions');
        if (data.conversions > data.clicks) console.warn('Warning: Conversions exceed clicks');
        
        return true;
    },
    
    validateConversionRatesData: function(data) {
        console.log('Validating conversion rates data:', data);
        const requiredFields = ['click_through_rate', 'conversion_rate', 'roi'];
        const missingFields = requiredFields.filter(field => data[field] === undefined);
        
        if (missingFields.length > 0) {
            console.error('Conversion rates data missing required fields:', missingFields);
            return false;
        }
        
        // Check for unreasonable values
        if (data.click_through_rate < 0 || data.click_through_rate > 100) 
            console.warn('Warning: Click-through rate outside normal range (0-100%)');
        if (data.conversion_rate < 0 || data.conversion_rate > 100) 
            console.warn('Warning: Conversion rate outside normal range (0-100%)');
        
        return true;
    },
    
    validateCampaignData: function(data) {
        console.log('Validating campaign data:', data);
        if (!Array.isArray(data)) {
            console.error('Campaign data is not an array');
            return false;
        }
        
        if (data.length === 0) {
            console.warn('Campaign data array is empty');
            return true;
        }
        
        // Check required fields in first item
        const firstItem = data[0];
        const requiredFields = ['campaign_name', 'roi', 'conversion_rate'];
        const missingFields = requiredFields.filter(field => firstItem[field] === undefined);
        
        if (missingFields.length > 0) {
            console.error('Campaign data missing required fields:', missingFields);
            return false;
        }
        
        // Check for unreasonable values
        data.forEach((campaign, i) => {
            if (campaign.roi < 0 && campaign.roi !== 0) 
                console.warn(`Warning: Campaign ${i} has negative ROI`);
            if (campaign.roi > 1000) 
                console.warn(`Warning: Campaign ${i} has unusually high ROI (>1000%)`);
            if (campaign.conversion_rate < 0 || campaign.conversion_rate > 100) 
                console.warn(`Warning: Campaign ${i} has conversion rate outside normal range (0-100%)`);
        });
        
        return true;
    },
    
    validateChannelData: function(data) {
        console.log('Validating channel data:', data);
        if (!Array.isArray(data)) {
            console.error('Channel data is not an array');
            return false;
        }
        
        if (data.length === 0) {
            console.warn('Channel data array is empty');
            return true;
        }
        
        // Check required fields in first item
        const firstItem = data[0];
        const requiredFields = ['channel', 'roi', 'conversion_rate', 'acquisition_cost'];
        const missingFields = requiredFields.filter(field => firstItem[field] === undefined);
        
        if (missingFields.length > 0) {
            console.error('Channel data missing required fields:', missingFields);
            return false;
        }
        
        // Check for unreasonable values
        data.forEach((channel, i) => {
            if (channel.roi < 0 && channel.roi !== 0) 
                console.warn(`Warning: Channel ${i} has negative ROI`);
            if (channel.roi > 1000) 
                console.warn(`Warning: Channel ${i} has unusually high ROI (>1000%)`);
            if (channel.conversion_rate < 0 || channel.conversion_rate > 100) 
                console.warn(`Warning: Channel ${i} has conversion rate outside normal range (0-100%)`);
            if (channel.acquisition_cost < 0) 
                console.warn(`Warning: Channel ${i} has negative acquisition cost`);
            if (channel.acquisition_cost === 0) 
                console.warn(`Warning: Channel ${i} has zero acquisition cost`);
        });
        
        return true;
    },
    
    // Fix common data issues
    sanitizeFunnelData: function(data) {
        if (!data) return null;
        
        // Create a clean copy
        const clean = { ...data };
        
        // Ensure all required fields exist and are positive numbers
        clean.impressions = Math.max(0, Number(clean.impressions || 0));
        clean.clicks = Math.max(0, Number(clean.clicks || 0));
        clean.conversions = Math.max(0, Number(clean.conversions || 0));
        
        // Ensure logical progression
        clean.clicks = Math.min(clean.clicks, clean.impressions);
        clean.conversions = Math.min(clean.conversions, clean.clicks);
        
        return clean;
    },
    
    sanitizeConversionRatesData: function(data) {
        if (!data) return null;
        
        // Create a clean copy
        const clean = { ...data };
        
        // Ensure all required fields exist and are within reasonable ranges
        clean.click_through_rate = Math.max(0, Math.min(100, Number(clean.click_through_rate || 0)));
        clean.conversion_rate = Math.max(0, Math.min(100, Number(clean.conversion_rate || 0)));
        clean.roi = Number(clean.roi || 0); // ROI can be negative
        
        return clean;
    },
    
    sanitizeCampaignData: function(data) {
        if (!Array.isArray(data)) return [];
        
        // Create a clean copy and ensure all fields are valid
        return data.map(campaign => ({
            campaign_name: campaign.campaign_name || campaign.campaign || 'Unknown Campaign',
            roi: Number(campaign.roi || 0),
            conversion_rate: Math.max(0, Math.min(100, Number(campaign.conversion_rate || 0))),
            cost: Number(campaign.cost || 0),
            revenue: Number(campaign.revenue || 0)
        }));
    },
    
    sanitizeChannelData: function(data) {
        if (!Array.isArray(data)) return [];
        
        // Create a clean copy and ensure all fields are valid
        return data.map(channel => ({
            channel: channel.channel || 'Unknown Channel',
            roi: Number(channel.roi || 0),
            conversion_rate: Math.max(0, Math.min(100, Number(channel.conversion_rate || 0))),
            acquisition_cost: Math.max(0, Number(channel.acquisition_cost || 0))
        }));
    },
    
    // Validate and sanitize CAC data
    validateCACData: function(data) {
        console.log('Validating CAC data:', data);
        
        if (!Array.isArray(data)) {
            console.warn('CAC data is not an array');
            return [];
        }
        
        return data.map(item => {
            const validated = {};
            
            // Required string fields
            validated.campaign = this.validateString(item.campaign, 'Unknown Campaign');
            validated.channel = this.validateString(item.channel, 'Unknown Channel');
            
            // Numeric fields - handle both original and enhanced data
            validated.acquisitions = this.validateNumber(item.acquisitions, 0);
            validated.clicks = this.validateNumber(item.clicks, 0);
            validated.impressions = this.validateNumber(item.impressions, 0);
            validated.total_cost = this.validateNumber(item.total_cost, 0);
            
            // Enhanced fields (may not be present in original data)
            validated.cac = this.validateNumber(item.cac, 0);
            validated.roi = this.validateNumber(item.roi, 0);
            validated.conversion_rate = this.validateNumber(item.conversion_rate, 0);
            validated.ctr = this.validateNumber(item.ctr, 0);
            
            // If CAC is 0 but we have cost and acquisitions, calculate it
            if (validated.cac === 0 && validated.total_cost > 0 && validated.acquisitions > 0) {
                validated.cac = validated.total_cost / validated.acquisitions;
            }
            
            // If we still don't have valid data, set reasonable defaults
            if (validated.acquisitions === 0 && validated.clicks > 0) {
                validated.acquisitions = Math.max(1, Math.floor(validated.clicks * 0.15));
            }
            
            if (validated.total_cost === 0 && validated.impressions > 0) {
                validated.total_cost = validated.impressions * 0.05;
            }
            
            // Recalculate CAC if needed
            if (validated.cac === 0 && validated.total_cost > 0 && validated.acquisitions > 0) {
                validated.cac = validated.total_cost / validated.acquisitions;
            }
            
            return validated;
        }).filter(item => {
            // Filter out items that still have no meaningful data
            return item.cac > 0 || item.total_cost > 0 || item.acquisitions > 0;
        });
    },
    
    // Helper functions for validation
    validateString: function(value, defaultValue = '') {
        return (typeof value === 'string' && value.trim().length > 0) ? value.trim() : defaultValue;
    },
    
    validateNumber: function(value, defaultValue = 0) {
        const num = Number(value);
        return (isNaN(num) || !isFinite(num)) ? defaultValue : num;
    },
    
    // Generate meaningful sample data if needed
    generateSampleFunnelData: function() {
        return {
            impressions: 100000,
            clicks: 15000,
            conversions: 3000
        };
    },
    
    generateSampleConversionRatesData: function() {
        return {
            click_through_rate: 15.0,
            conversion_rate: 20.0,
            roi: 175.0
        };
    },
    
    generateSampleCampaignData: function() {
        return [
            {
                campaign_name: "Summer Sale",
                roi: 185.5,
                conversion_rate: 22.3,
                cost: 12000,
                revenue: 34260
            },
            {
                campaign_name: "Holiday Special",
                roi: 210.3,
                conversion_rate: 28.5,
                cost: 15000,
                revenue: 46545
            },
            {
                campaign_name: "New Customer Promo",
                roi: 135.2,
                conversion_rate: 18.8,
                cost: 8500,
                revenue: 20000
            },
            {
                campaign_name: "Back to School",
                roi: 95.7,
                conversion_rate: 15.3,
                cost: 10000,
                revenue: 19570
            }
        ];
    },
    
    generateSampleChannelData: function() {
        return [
            {
                channel: "Email",
                roi: 230.1,
                conversion_rate: 28.4,
                acquisition_cost: 5.20
            },
            {
                channel: "Social Media",
                roi: 175.3,
                conversion_rate: 23.7,
                acquisition_cost: 12.50
            },
            {
                channel: "Search",
                roi: 160.8,
                conversion_rate: 18.9,
                acquisition_cost: 15.75
            },
            {
                channel: "Display",
                roi: 95.6,
                conversion_rate: 10.2,
                acquisition_cost: 25.30
            },
            {
                channel: "Affiliate",
                roi: 120.4,
                conversion_rate: 15.8,
                acquisition_cost: 18.90
            }
        ];
    }
};

// Export the utilities
window.DataValidator = DataValidator;
