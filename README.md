# RetailFlow | Industry-Grade Inventory Optimization System

RetailFlow is a professional pharmacy warehouse management system designed for scalability, security, and intelligence. It leverages ML to predict stock-outs and provides a modern, responsive dashboard for real-time inventory tracking.

## 🚀 Key Features

- **Modular Backend**: Clean Flask architecture with Service/Model/Route separation.
- **Intelligent Forecasting**: AI-powered stock-out risk prediction using Random Forest.
- **Modern UI**: Fully responsive dashboard with Chart.js visualization and glassmorphism design.
- **Security**: Robust authentication system with role-based access control placeholders.
- **RESTful API**: Standards-compliant API endpoints for external integrations.
- **DevOps Ready**: Full Docker support and automated ETL pipeline structure.
- **Cloud Scale**: Architected for AWS deployment (EC2/S3/RDS).

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Jinja2, HTML5/CSS3 (Inter Font, FontAwesome) |
| Backend | Flask, SQLAlchemy, Flask-Login |
| Database | PostgreSQL |
| ML/Data | Scikit-learn, Pandas, NumPy |
| DevOps | Docker, Docker-compose, Gunicorn |

## 📂 Project Structure

```text
app/
├── config/       # Configuration settings
├── ml/           # Machine Learning models & predictors
├── models/       # SQLAlchemy database models
├── routes/       # Blueprint-based routing
├── services/     # Business logic layer
├── static/       # CSS, JS, and generated reports
├── templates/    # UI components
└── utils/        # Helper functions
main.py           # Application entry point
Dockerfile        # Container definition
requirements.txt  # Dependencies
```

## 🚥 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```text
   DATABASE_URL=postgresql://user:password@localhost:5432/pharmacy_db
   SECRET_KEY=your_secret_key
   ```
4. Initialize the database and admin user:
   ```bash
   flask init-db
   ```
5. Run the application:
   ```bash
   python main.py
   ```

### Running with Docker

```bash
docker-compose up --build
```

## 📊 ML Model

The system uses a `RandomForestClassifier` trained on historical inventory data, daily sales averages, and lead times to predict the probability of a stock-out event.

---
Built for Enterprise Performance & Scalability.
