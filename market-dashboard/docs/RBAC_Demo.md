# RBAC Demo - Marketing Insights Dashboard

## Header-Based Role Authentication

The app now supports role-based access via **X-Role header** for API clients:

### Supported Roles:
- **Admin**: Full access (view, upload, role management)
- **Editor**: Upload + view access  
- **Viewer**: Read-only access

### Demo Commands:

```bash
# Test Viewer role (should get 403 on upload)
curl -X POST http://localhost:5000/upload -H "X-Role: Viewer"
# Expected: 403 Forbidden

# Test Admin role (should allow upload, fail on missing file)  
curl -X POST http://localhost:5000/upload -H "X-Role: Admin"
# Expected: 400 Bad Request (no file provided)

# Test invalid role (defaults to Viewer)
curl -X POST http://localhost:5000/upload -H "X-Role: InvalidRole"  
# Expected: 403 Forbidden

# Test dashboard access with role header
curl -H "X-Role: Admin" http://localhost:5000/dashboard.json
# Expected: 200 OK with KPI data
```

### Browser Demo:
1. **Login as Viewer** (`viewer/viewer123`)
2. **Try to upload** → Should see "Permission denied" 
3. **Login as Admin** (`admin/admin123`) 
4. **Access /set-role** → Should load role management page
5. **Change to Editor role** → Upload should work, role management should be blocked

### Test Verification:
```bash
# Run RBAC-specific tests
python -m pytest tests/test_auth.py::TestRBAC -v

# Verify 403 forbidden test specifically
python -m pytest tests/test_auth.py::TestRBAC::test_header_based_role_viewer_403 -v
```

## Implementation Details

### Code Changes:
- **`get_current_role()`**: Now checks `X-Role` header before session
- **Upload protection**: Validates role before processing files
- **Fallback logic**: Invalid headers default to Viewer role

### Security Notes:
- Header-based auth is for **demo/API purposes**
- Production should use **JWT tokens** or **OAuth**
- Session-based auth remains primary for web UI
- All role validations maintain **least privilege principle**
