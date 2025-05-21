# Restaurant Management System

A comprehensive restaurant management system built with Django and Docker, featuring order management, menu management, staff management, and customer loyalty programs.

## 🌟 Features

### Core Features
- Customer order management
- Product and menu management
- Staff and department management
- Reports and analytics
- REST API integration
- Customer loyalty program
- Bonus points system
- Discount management
- Email notifications

### Technical Features
- Docker containerization
- Celery task queue
- Redis caching
- PostgreSQL database
- Elasticsearch integration
- Nginx reverse proxy
- Gunicorn application server
- JWT authentication
- Swagger API documentation

## 🛠 Technologies

### Backend
- Python 3.8+
- Django 4.2
- Django REST Framework
- Celery
- Redis
- PostgreSQL
- Elasticsearch

### Infrastructure
- Docker & Docker Compose
- Nginx
- Gunicorn
- Linux

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/MusfiqEmirov/restaurant_management_system.git
cd restaurant_management_system
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the application:
```bash
docker-compose up -d --build
```

4. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

5. Create superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

6. Collect static files:
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

## 📦 Docker Services

The project uses multiple Docker services:

| Service | Description | Port |
|---------|-------------|------|
| web | Django application | 8000 |
| db | PostgreSQL database | 5432 |
| redis | Redis cache & broker | 6379 |
| celery | Celery worker | - |
| celery-beat | Celery scheduler | - |
| elasticsearch | Search engine | 9200 |
| nginx | Web server | 80 |

## 🔧 Development

### Accessing Services
- Main application: http://pi.backend.az/restaurant
- Admin interface: http://pi.backend.az/restaurant/admin
- API documentation: http://pi.backend.az/restaurant/api/v1/docs/
- Swagger UI: http://pi.backend.az/restaurant/api/v1/schema/swagger-ui/
- ReDoc: http://pi.backend.az/restaurant/api/v1/schema/redoc/

### Common Commands

```bash
# View logs
docker-compose logs -f

# Run tests
docker-compose exec web python manage.py test

# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Shell access
docker-compose exec web python manage.py shell

# Stop containers
docker-compose down
```

## 📚 API Documentation

The API is documented using Swagger/OpenAPI. Access the documentation at:
- Swagger UI: http://pi.backend.az/api/v1/schema/swagger-ui/
- ReDoc: http://pi.backend.az/api/v1/schema/redoc/

# If the domain is not working and you want to access directly by IP:
- Swagger UI (IP ilə): http://85.132.18.12/api/v1/schema/swagger-ui/
- ReDoc (IP ilə): http://85.132.18.12/api/v1/schema/redoc/

### API Features
- JWT Authentication
- Role-based access control
- Rate limiting
- Request validation
- Response serialization
- Error handling

## 📝 Project Structure

```
restaurant_management_system/
├── restora_project/          # Django project
│   ├── project_apps/        # Django applications
│   │   ├── accounts/       # User management
│   │   ├── core/          # Core functionality
│   │   ├── customers/     # Customer management
│   │   ├── menu/         # Menu management
│   │   ├── notifications/ # Notification system
│   │   ├── orders/       # Order management
│   │   └── staff/        # Staff management
│   ├── api/              # API endpoints
│   └── restora_project/  # Project settings
├── nginx/                # Nginx configuration
├── docker/              # Docker configuration
├── tests/              # Test files
├── .env.example        # Environment template
├── docker-compose.yml  # Docker services
└── README.md          # Documentation
```

## 🧪 Testing

Run tests using:
```bash
docker-compose exec web python manage.py test
```

Test coverage includes:
- Unit tests
- Integration tests
- API tests
- Model tests
- View tests
- URL tests

## 📈 Monitoring

The system includes:
- Logging to files
- Error tracking
- Performance monitoring
- Database monitoring
- Celery task monitoring

## 🔄 CI/CD

The project includes:
- GitHub Actions workflow
- Automated testing
- Docker image building
- Deployment automation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For support, email support@restaurant.com or create an issue in the repository.
