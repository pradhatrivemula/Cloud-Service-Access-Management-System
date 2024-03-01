# FastAPI Subscription Management System

This project is a subscription management system built with FastAPI and SQLAlchemy, designed to handle user subscriptions, permissions, and API usage tracking. It offers a comprehensive solution for managing subscription plans, user roles, and API access permissions, making it ideal for SaaS platforms or any application requiring subscription-based access control.

## Features

- **User Management:** Securely create and authenticate users.
- **Subscription Plans:** Create, update, and delete subscription plans.
- **Permissions Management:** Assign permissions to different API endpoints.
- **API Usage Tracking:** Track and limit the number of API requests based on the subscription plan.
- **Role-Based Access Control:** Implement role-based access control to restrict API endpoints based on user roles.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or later
- FastAPI
- Uvicorn (ASGI server)
- SQLAlchemy (Async version for async database operations)
- Passlib (for password hashing)
- JWT (for generating and decoding JSON Web Tokens)
- A database (SQLite for development, PostgreSQL recommended for production)

## Installation

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   ```
   
## Install Dependencies:
Navigate to the project directory and install the required Python packages:
```
pip install fastapi uvicorn sqlalchemy async-sqlalchemy passlib python-jwt
```

## Database Setup:

Ensure your database is running and accessible.
Configure your database connection settings in the models.py file or a separate configuration file.

## Running the Application
To start the application, use Uvicorn with the following command:
```
uvicorn main:app --reload
```

## Using the API
## API Documentation:
FastAPI automatically generates Swagger UI documentation. Visit http://127.0.0.1:8000/docs to explore and test the available endpoints.

## Creating Users and Plans:
Use the /users/ endpoint to create new users and /plans/ to create subscription plans.

## Managing Permissions and Usage:

Add permissions with /permissions and assign them to different plans.
Track API usage per user and plan with /track-usage/{user_id}/{api_name}.

## Authentication:

Implement OAuth2 with Password (and hashing), including JWT for secure authentication.


## Development
## Add More Features:
Consider implementing more advanced features like email verification, multi-factor authentication, or integrating payment gateways for subscription management.
## Optimize for Production:
Ensure your database and server configurations are optimized for production environments.

## Contributing
Contributions are welcome! If you have suggestions for improving the application, please fork the repository and submit a pull request.
