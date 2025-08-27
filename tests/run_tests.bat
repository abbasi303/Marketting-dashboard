@echo off
echo Running Marketing Dashboard Tests

echo.
echo ========================================
echo Running Python Unit Tests
echo ========================================
python -m pytest -v

echo.
echo ========================================
echo Test cases summary:
echo ========================================
echo 1. Backend API Tests:
echo    - Ensures the dashboard API endpoints work
echo    - Verifies section-specific endpoints return proper data
echo    - Tests pagination and data sorting
echo    - Tests error handling for missing sections

echo.
echo 2. Chart Rendering Tests:
echo    - Verifies the chart styles are properly loaded
echo    - Tests chart containers have proper structure
echo    - Ensures chart dimensions stay fixed (no vertical growth)

echo.
echo 3. Excel Compatibility Tests:
echo    - Tests support for .xls (Excel 97-2003) files
echo    - Tests support for .xlsx (Excel 2007+) files
echo    - Verifies both events and costs data can be loaded

echo.
echo 4. JavaScript Unit Tests:
echo    - Tests for ChartManager.js functionality
echo    - Tests for chart-reset.js functions
echo    - Tests for utility functions

echo.
echo ========================================
echo To run JavaScript tests, open:
echo tests/chart_manager_tests.html
echo.
echo To test chart growth fix, open:
echo tests/chart_growth_test.html
echo ========================================
