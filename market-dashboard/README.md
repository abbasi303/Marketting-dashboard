# Marketing Insights Dashboard

A comprehensive Flask web application for analyzing marketing campaign performance with advanced KPI calculations, role-based access control, and interactive visualizations.

## Features

### 📊 Core Analytics
- **KPI Calculations**: Views, Signups, Purchases, Conversion Rates
- **Customer Acquisition Cost (CAC)**: Weighted average calculation with optional costs CSV
- **Campaign Performance**: Top campaigns by Purchase/Signup rate
- **Data Validation**: Comprehensive CSV validation and data cleaning

### 🔐 Security & Access Control
- **Role-Based Access Control (RBAC)**: Admin, Editor, Viewer roles
- **Permission Management**: Upload restrictions based on roles
- **Session Management**: Secure role switching interface

### 📈 Visualizations
- **Interactive Dashboard**: Bootstrap + Chart.js integration
- **KPI Cards**: Real-time metric displays
- **Funnel Chart**: 3-bar marketing funnel visualization
- **Campaign Charts**: Top-performing campaigns by conversion rate

### 🛠️ Technical Features
- **File Upload**: Drag-and-drop CSV upload with validation
- **RESTful API**: JSON endpoints for dashboard data
- **Health Monitoring**: Built-in health check endpoint
- **Responsive Design**: Mobile-friendly Bootstrap interface

## API Endpoints

### Data Upload
```
POST /upload
Content-Type: multipart/form-data

Required:
- events_csv: Marketing campaign dataset

Optional:
- costs_csv: Cost breakdown by campaign/channel
```

### Dashboard Data
```
GET /dashboard.json
Returns: {
  "views": int,
  "signups": int, 
  "purchases": int,
  "signup_view_rate": float,
  "purchase_signup_rate": float,
  "estimated_cac": float,
  "top_campaigns": [...],
  "last_update": "ISO datetime"
}
```

### Health Check
```
GET /healthz
Returns: {
  "status": "healthy",
  "timestamp": "ISO datetime",
  "data_loaded": boolean
}
```

### Role Management
```
GET/POST /set-role
Manage user role permissions (Admin/Editor/Viewer)
```

## Data Requirements

### Events CSV (Required)
```csv
Campaign_ID,Channel_Used,Clicks,Impressions,Conversion_Rate,Date,Acquisition_Cost
1,Google Ads,100,1000,0.1,2021-01-01,"$100.00"
```

**Required Columns:**
- `Campaign_ID`: Unique campaign identifier
- `Channel_Used`: Marketing channel (Google Ads, Facebook, etc.)
- `Clicks`: Number of clicks (Signups)
- `Impressions`: Number of impressions (Views)
- `Conversion_Rate`: Click-to-purchase conversion rate
- `Date`: Campaign date (YYYY-MM-DD format)

**Optional Columns:**
- `Acquisition_Cost`: Cost per campaign (supports currency symbols)

### Costs CSV (Optional)
```csv
campaign,channel,cpc,cpm
1,Google Ads,1.5,10.0
```

**Required Columns:**
- `campaign`: Campaign ID (matches Events CSV)
- `channel`: Channel name (matches Events CSV)
- `cpc`: Cost per click
- `cpm`: Cost per thousand impressions

## KPI Logic

### Core Metrics
- **Views** = sum(Impressions)
- **Signups** = sum(Clicks)  
- **Purchases** ≈ sum(round(Clicks × Conversion_Rate))

### Conversion Rates
- **Signup/View Rate** = Total Clicks ÷ Total Impressions × 100
- **Purchase/Signup Rate** ≈ Conversion_Rate × 100

### Customer Acquisition Cost (CAC)
**With Costs CSV:**
```
CAC = (Impressions/1000 × CPM + Clicks × CPC) ÷ Purchases
```

**With Acquisition_Cost column:**
```
CAC = Weighted average of Acquisition_Cost (weighted by purchases)
```

### Top Campaigns
Ranked by Purchase/Signup rate, grouped by Campaign_ID + Channel_Used

## Installation & Setup

### Prerequisites
- Python 3.9+
- pip

### Local Development
```bash
# Clone repository
git clone <repository-url>
cd market-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Visit `http://localhost:5000` to access the dashboard.

### Docker Deployment
```bash
# Build image
docker build -t marketing-insights-dashboard .

# Run container
docker run -p 5000:5000 marketing-insights-dashboard
```

## Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-cov flake8

# Run all tests with coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Run linting
flake8 app.py tests/ --max-line-length=120
```

### Security & License Auditing
```bash
# Security audit
pip-audit

# License report
pip-licenses --format=json --output-file=licenses.json
```

## CI/CD Pipeline

The project includes an Azure DevOps pipeline (`azure-pipelines.yml`) that:

1. **Quality Checks**:
   - Runs flake8 linting
   - Executes pytest with coverage reporting
   - Performs pip-audit security scanning
   - Generates license reports

2. **Build Stage**:
   - Creates Docker images
   - Pushes to container registry

3. **Deployment**:
   - Deploys to staging environment
   - Runs health checks

### Pipeline Artifacts
- Test results (JUnit XML)
- Code coverage reports (Cobertura XML + HTML)
- Flake8 lint reports
- Security scan results
- License compliance reports

## Architecture

### Components
- **Flask Application**: Core web framework
- **Data Processing**: Pandas for CSV handling and KPI calculations
- **Frontend**: Bootstrap 5 + Chart.js for responsive UI
- **Session Management**: Flask sessions for RBAC
- **File Handling**: Werkzeug for secure file uploads

### Data Flow
1. **Upload**: CSV files validated and processed
2. **Storage**: Data stored in memory (production should use database)
3. **Calculation**: KPIs computed on-demand
4. **Visualization**: Real-time charts updated via AJAX

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `FLASK_ENV`: Environment (development/production)
- `MAX_CONTENT_LENGTH`: Maximum upload file size

### Security Considerations
- Input validation for all uploaded data
- CSRF protection via Flask-WTF (recommended for production)
- File type restrictions (.csv only)
- Size limits on uploads
- Non-root Docker container execution

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Run tests (`pytest`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

---

Built with ❤️ for marketing teams to make data-driven decisions.
