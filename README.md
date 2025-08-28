# Broadcast IT Management System

A comprehensive web-based management system for broadcasting companies, designed for IT asset management, employee administration, and knowledge base management.

## Features

### Employee Management
- Complete employee registration and authentication system
- Role-based access control (Admin, Manager, User)
- Employee profile management with department assignments
- Secure login/logout functionality

### Asset Management
- Equipment inventory tracking
- Equipment assignment to employees
- Status monitoring (in use, in stock, under repair, scrap)
- Purchase date and warranty tracking
- Category-based organization

### License Management
- Software license tracking and monitoring
- Expiration date alerts
- Vendor and version management
- Equipment-license associations
- License key management

### Knowledge Base
- Document upload and management
- Category-based organization
- Search and filtering capabilities
- File preview and download
- Version control and metadata

### Analytics Dashboard
- Real-time statistics and visualizations
- Equipment utilization charts
- License expiration tracking
- Activity monitoring
- System health indicators

### Advanced Features
- Activity logging and audit trails
- Export functionality (CSV)
- Bulk operations
- Search and filtering across all modules
- Responsive design for mobile and desktop

## Tech Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Flask-Login** - User session management
- **Werkzeug** - Password hashing and security

### Frontend
- **HTML5/CSS3** - Modern responsive design
- **JavaScript** - Interactive functionality
- **Font Awesome** - Icons
- **CSS Grid/Flexbox** - Layout system

### Analytics
- **Dash** - Interactive dashboard
- **Plotly** - Data visualization
- **Pandas** - Data analysis

## Installation

### Prerequisites
- Python 3.7+
- PostgreSQL 12+
- pip (Python package manager)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/broadcast-it-management.git
cd broadcast-it-management
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
1. Install PostgreSQL and create a database
2. Update database configuration in `Project/config.py`:
```python
SQLALCHEMY_DATABASE_URI = "postgresql://username:password@localhost:5432/database_name"
```

### 5. Initialize Database
```bash
python -c "from Project import create_app; from Project.models import init_database; app = create_app(); app.app_context().push(); init_database()"
```

### 6. Run the Application
```bash
python run.py
```

The application will be available at:
- Main Application: `http://localhost:5000`
- Analytics Dashboard: `http://localhost:8050`

## Default Users

The system creates default test users on first run:

| Role | Email | Password | Description |
|------|--------|----------|-------------|
| Admin | admin@trt.gov.tr | admin123 | Full system access |
| Manager | manager@trt.gov.tr | manager123 | Limited management access |
| User | user@trt.gov.tr | user123 | Basic user access |

## Project Structure

```
broadcast-it-management/
├── Project/
│   ├── __init__.py              # Flask app initialization
│   ├── config.py                # Database and app configuration
│   ├── models.py                # SQLAlchemy database models
│   ├── routes.py                # Application routes and logic
│   ├── static/                  # CSS, JS, and static files
│   ├── templates/               # HTML templates
│   └── uploads/                 # File upload directory
├── dash_dashboard.py            # Analytics dashboard
├── register.py                  # Standalone registration utility
├── run.py                       # Application launcher
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## Usage

### Admin Panel
1. Login with admin credentials
2. Navigate through the sidebar menu:
   - **Dashboard**: System overview and statistics
   - **Employees**: Manage staff and user accounts
   - **Inventory**: Equipment and license management
   - **Knowledge Base**: Document management
   - **Analytics**: Data visualization and reports
   - **Settings**: System configuration

### Employee Management
- Add new employees with role assignments
- Edit employee information and permissions
- View detailed employee profiles
- Export employee data

### Asset Management
- Add equipment with detailed specifications
- Assign equipment to employees
- Track equipment status and location
- Monitor warranty information

### License Management
- Register software licenses with expiration tracking
- Associate licenses with equipment or employees
- Receive notifications for expiring licenses
- Manage vendor relationships

## API Endpoints

The system provides REST API endpoints for integration:

- `GET /api/admin/employees` - Employee data
- `GET /api/admin/stats` - System statistics
- `GET /api/settings/load` - User settings
- `POST /api/settings/save` - Save user preferences

## Configuration

### Database Configuration
Update `Project/config.py` with your database settings:

```python
class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://username:password@localhost:5432/database"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your-secret-key-here"
```

### File Upload Configuration
Create upload directories:
```bash
mkdir -p Project/uploads/knowledge_base
```

## Security Features

- Password hashing with Werkzeug
- Session management with Flask-Login
- Role-based access control
- CSRF protection
- Input validation and sanitization
- Activity logging and audit trails

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python run.py
```

### Database Migrations
For schema changes, use SQLAlchemy migrations:
```bash
# Initialize migrations (first time only)
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## Deployment

### Production Deployment
1. Set environment variables:
```bash
export FLASK_ENV=production
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="your-production-database-url"
```

2. Use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "Project:create_app()"
```

3. Set up reverse proxy with Nginx for static files and SSL

## Troubleshooting

### Common Issues

**Database Connection Error**
- Verify PostgreSQL is running
- Check database credentials in config.py
- Ensure database exists

**Port Already in Use**
- The app automatically tries alternative ports (8051, 8052, etc.)
- Or specify a different port in run.py

**File Upload Issues**
- Check upload directory permissions
- Verify UPLOAD_FOLDER path in routes.py

### Logging
Application logs are printed to console. For production, configure proper logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` directory
- Review the code comments and docstrings

## Acknowledgments

- Flask community for excellent documentation
- Plotly/Dash for powerful data visualization tools
- PostgreSQL team for robust database engine
- Bootstrap and Font Awesome for UI components
