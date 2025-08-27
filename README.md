# Marketing Insights Dashboard

A Flask web application for marketing analytics and insights.

## Features

- Upload and analyze marketing event data
- Track user journey through the marketing funnel
- Calculate conversion rates and KPIs
- View campaign and channel performance
- Calculate Customer Acquisition Cost (CAC)
- Role-based access control

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Docker (optional)

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/marketing-dashboard.git
cd marketing-dashboard
```

2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run the application

```bash
python app.py
```

The application will be available at http://localhost:5000

### Docker

To run the application using Docker:

```bash
docker build -t marketing-dashboard .
docker run -p 5000:5000 marketing-dashboard
```

## Usage

1. Log in using one of the demo accounts:
   - Admin: username `admin`, password `adminpass`
   - Editor: username `editor`, password `editorpass`
   - Viewer: username `viewer`, password `viewerpass`

2. Navigate to the Upload Data page (requires admin or editor role)

3. Upload the sample marketing event data (CSV file)

4. View the dashboard to see the insights

## Testing

Run the tests with pytest:

```bash
python -m pytest
```

Run with coverage:

```bash
python -m pytest --cov=app tests/
```

## Data Format

### Marketing Events CSV

The marketing events CSV file should have the following columns:

- `user_id`: Unique identifier for each user
- `event_type`: One of: page_view, signup, purchase
- `campaign`: Campaign name
- `channel`: Marketing channel (e.g., Email, Social, Ads)
- `timestamp`: When the event occurred (ISO format)

### Campaign Costs CSV

The campaign costs CSV file should have the following columns:

- `campaign`: Campaign name (matching events data)
- `channel`: Marketing channel (matching events data)
- `cpc`: Cost per click
- `cpm`: Cost per thousand impressions

## License

This project is licensed under the MIT License.
