# Bug Report Template

## Bug #1: Invalid event types not rejected during validation

**Priority:** High  
**Severity:** Medium  
**Status:** Open  
**Reported By:** QA Team  
**Date:** August 25, 2025

### Description
When uploading a CSV file with invalid event types (not in the allowed list: page_view, signup, purchase), the validation doesn't reject these events.

### Steps to Reproduce
1. Login as admin or editor
2. Go to Upload Data page
3. Select "Marketing Events" file type
4. Upload a CSV with an invalid event type (e.g., "click" instead of "page_view")
5. Submit the form

### Expected Behavior
The system should reject the file with a validation error message specifying that "click" is not a valid event type.

### Actual Behavior
The system accepts the file and processes it, treating the invalid event types as valid ones.

### Environment
- Browser: Chrome 111.0.5563.64
- OS: Windows 11
- App Version: 1.0.0

### Attachments
- [invalid_events.csv]

---

## Bug #2: CAC calculation shows infinity when no acquisitions

**Priority:** Medium  
**Severity:** Low  
**Status:** Open  
**Reported By:** QA Team  
**Date:** August 25, 2025

### Description
When calculating Customer Acquisition Cost (CAC) for campaigns with no purchases/acquisitions, the dashboard displays "Infinity" instead of a more user-friendly message.

### Steps to Reproduce
1. Login as admin
2. Upload an events CSV with campaigns that have no purchases
3. Upload a costs CSV with costs for those campaigns
4. Navigate to the dashboard

### Expected Behavior
The CAC column should show "N/A" or "No acquisitions" for campaigns with no purchases.

### Actual Behavior
The CAC column shows "Infinity" for campaigns with no purchases.

### Environment
- Browser: Firefox 99.0
- OS: macOS 12.6
- App Version: 1.0.0

### Attachments
- [Screenshot of CAC table]

---

## Bug #3: Session timeout does not redirect to login page

**Priority:** Medium  
**Severity:** Medium  
**Status:** Open  
**Reported By:** QA Team  
**Date:** August 26, 2025

### Description
When a user's session times out, attempting to upload data doesn't redirect to the login page but instead shows an error.

### Steps to Reproduce
1. Login as editor
2. Wait for session timeout (approx. 1 hour)
3. Attempt to upload a file

### Expected Behavior
User should be redirected to the login page with a message that their session has expired.

### Actual Behavior
The user sees a 401 error in the API response, but stays on the upload page with a generic error message.

### Environment
- Browser: Safari 16.3
- OS: iOS 16.4
- App Version: 1.0.0

### Attachments
- [Screenshot of error]
