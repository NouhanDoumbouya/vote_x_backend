# VoteX Backend

[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/NouhanDoumbouya/vote_x_backend)

This repository contains the backend service for VoteX, a real-time online polling application. It is built with Django and Django REST Framework, providing a robust API for user management, poll creation, and voting.

## Features

*   **User Authentication**: Secure user registration and login using JSON Web Tokens (JWT).
*   **Role-Based Access**: Differentiated user roles (`admin`, `voter`).
*   **Poll Management**: Create, view, and delete polls.
*   **Flexible Poll Visibility**:
    *   `public`: Accessible to everyone.
    *   `private`: Only visible to the poll owner.
    *   `restricted`: Visible only to a specific list of allowed users.
*   **Voting System**: Supports voting for both authenticated users and guests (with IP-based duplicate vote prevention).
*   **Real-time Updates**: Utilizes Django Channels and WebSockets to provide real-time updates for poll results.
*   **API Documentation**: Interactive API documentation available via Swagger (drf-yasg).
*   **Containerized**: Fully containerized with Docker and Docker Compose for easy setup and deployment.
*   **CI/CD**: Automated workflows with GitHub Actions for running tests and publishing Docker images.

## Technology Stack

*   **Backend**: Python, Django, Django REST Framework
*   **Real-time**: Django Channels, Redis
*   **Database**: PostgreSQL
*   **Authentication**: djangorestframework-simplejwt
*   **Containerization**: Docker, Docker Compose
*   **API Documentation**: drf-yasg (Swagger)
*   **CI/CD**: GitHub Actions

## Getting Started

### Prerequisites

*   Git
*   Docker
*   Docker Compose

### Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/nouhandoumbouya/vote_x_backend.git
    cd vote_x_backend
    ```

2.  **Create an environment file:**

    Create a `.env` file in the project root and add the following configuration. These credentials will be used by Docker Compose to set up the PostgreSQL database.

    ```env
    # Django Settings
    SECRET_KEY=your-strong-secret-key-here
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    # PostgreSQL Database
    POSTGRES_DB=vote_x_db
    POSTGRES_USER=vote_x_user
    POSTGRES_PASSWORD=your_postgres_password
    ```

3.  **Build and run the containers:**
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker images for the web service, set up the PostgreSQL database and Redis containers, and start the application.

4.  **Run database migrations:**
    Open another terminal and run:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Seed the database (Optional):**
    To populate the database with initial sample data (an admin user, a voter user, and a poll), run:
    ```bash
    docker-compose exec web python manage.py seed
    ```
    *   Admin: `admin@example.com` / `admin123`
    *   Voter: `voter@example.com` / `voter123`

The application will be available at `http://localhost:8000`.

## API Documentation

Once the application is running, you can access the interactive Swagger API documentation at:

*   **Swagger UI**: `http://localhost:8000/api/docs/`
*   **ReDoc**: `http://localhost:8000/api/redoc/`

## API Endpoints

A summary of the main available API endpoints:

| Method | Endpoint                          | Description                                |
| :----- | :-------------------------------- | :----------------------------------------- |
| `POST` | `/api/auth/register/`             | Register a new user.                       |
| `POST` | `/api/auth/login/`                | Log in and receive JWT access/refresh tokens. |
| `GET`  | `/api/auth/profile/`              | Get the current authenticated user's profile. |
| `POST` | `/api/polls/`                     | Create a new poll (Authenticated users only). |
| `GET`  | `/api/polls/`                     | List all accessible polls.                 |
| `GET`  | `/api/polls/<id>/`                | Retrieve details of a specific poll.       |
| `DELETE`| `/api/polls/<id>/delete/`        | Delete a poll (Owner only).                |
| `GET`  | `/api/polls/share/<share_id>/`    | Access a poll via its unique shareable link. |
| `POST` | `/api/votes/`                     | Cast a vote on a poll option.              |
| `GET`  | `/api/votes/results/<poll_id>/`   | Get the results for a specific poll.       |
| `GET`  | `/api/votes/me/<poll_id>/`        | Check which option the user has voted for. |

## CI/CD

This project uses GitHub Actions for continuous integration and deployment.

*   **`ci.yml`**: This workflow runs on every push and pull request to the `main` branch. It installs dependencies and runs the test suite using an in-memory SQLite database.
*   **`docker.yml`**: This workflow triggers on every push to the `main` branch. It builds a new Docker image and pushes it to Docker Hub, ready for deployment.
