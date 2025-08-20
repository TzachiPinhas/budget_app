# Budget App Backend

A FastAPI-based backend service for managing personal budgets, expenses, and incomes. Built with Python and MongoDB, containerized with Docker for easy deployment and development.

## Overview

This backend service provides RESTful APIs for:
- Managing expenses and incomes
- Budget tracking and categorization
- User management and data persistence
- API documentation with Swagger UI

## Requirements

- Python 3.11 or higher
- Docker and Docker Compose
- MongoDB (handled by Docker Compose)

## Running Locally

1. Clone the repository:
```bash
git clone https://github.com/yourusername/budget_app.git
cd budget_app
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

The application will be available at:
- API Endpoint: `http://localhost:8000`
- Swagger UI Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

## API Documentation

Once the application is running, you can explore the full API documentation using the Swagger UI interface at `http://localhost:8000/docs`. This interactive documentation allows you to:

- View all available endpoints
- Test API endpoints directly from the browser
- Understand request/response schemas
- Execute API calls with different parameters

## Project Structure

```
budget_app/
├── app/
│   ├── routers/          # API route handlers
│   ├── database.py       # Database configuration
│   ├── main.py          # Application entry point
│   ├── schemas.py       # Pydantic models
│   └── utils.py         # Utility functions
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Docker container configuration
└── requirements.txt     # Python dependencies
```

## Future Improvements

1. **Authentication & Authorization**
   - Implement JWT-based authentication
   - Role-based access control
   - User session management

2. **Frontend Development**
   - Create a React/Vue.js frontend application
   - Mobile-responsive design
   - Interactive dashboards and charts

3. **Enhanced Features**
   - Budget analytics and reporting
   - Recurring transactions
   - Export functionality (CSV, PDF)
   - Email notifications

4. **Deployment**
   - CI/CD pipeline setup
   - Cloud deployment (AWS, GCP, or Azure)
   - Production environment configuration
   - Monitoring and logging

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
