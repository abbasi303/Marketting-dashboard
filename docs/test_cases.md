# Test Cases

## Smoke Tests

These tests verify that the basic functionality of the application is working as expected.

1. **Application Startup**
   - Start the application
   - Verify that the server starts successfully
   - Access the login page at http://localhost:5000/auth/login
   - Expected: Login page displays correctly

2. **Authentication**
   - Log in with valid credentials (e.g., username: admin, password: adminpass)
   - Expected: User is redirected to the dashboard page
   - Log out
   - Expected: User is redirected to the login page

3. **Dashboard Access**
   - Log in as a viewer
   - Navigate to the dashboard
   - Expected: Dashboard page loads with no data message
   - Upload sample data (admin or editor required)
   - Expected: Dashboard displays charts and metrics

4. **Health Check Endpoint**
   - Access the health check endpoint at http://localhost:5000/api/healthz
   - Expected: JSON response with status "ok"

## Regression Tests

These tests verify that the application behaves as expected when performing common tasks.

1. **Data Upload - Events**
   - Log in as an admin or editor
   - Navigate to the upload page
   - Select "Marketing Events" as the file type
   - Upload a valid events CSV file
   - Expected: Success message and summary of the uploaded data

2. **Data Upload - Campaign Costs**
   - Log in as an admin or editor
   - Navigate to the upload page
   - Select "Campaign Costs" as the file type
   - Upload a valid costs CSV file
   - Expected: Success message and summary of the uploaded data

3. **Data Validation**
   - Log in as an admin or editor
   - Try to upload an invalid CSV file (missing required columns)
   - Expected: Error message with details about the validation failures

4. **Dashboard Data Refresh**
   - Log in as any user
   - Upload new data
   - Navigate to the dashboard
   - Expected: Dashboard displays the updated data

5. **CAC Calculation**
   - Log in as any user
   - Upload both events and costs data
   - Navigate to the dashboard
   - Expected: CAC table displays calculated values

## Permissions Tests

These tests verify that the role-based access control works as expected.

1. **Admin Access**
   - Log in as admin
   - Expected: Can access the dashboard and upload pages
   - Expected: Can upload data

2. **Editor Access**
   - Log in as editor
   - Expected: Can access the dashboard and upload pages
   - Expected: Can upload data

3. **Viewer Access**
   - Log in as viewer
   - Expected: Can access the dashboard
   - Expected: Cannot access the upload page (redirected to dashboard)
   - Expected: Cannot upload data via API (403 Forbidden)

4. **Unauthenticated Access**
   - Attempt to access the dashboard without logging in
   - Expected: Redirected to the login page
   - Attempt to access the upload page without logging in
   - Expected: Redirected to the login page
   - Attempt to use the upload API without logging in
   - Expected: 401 Unauthorized
