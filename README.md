# NanoLink — URL Shortening Service

**NanoLink** is an educational URL shortening service built on an asynchronous Python stack.

The project is designed to practice REST API design, caching strategies, working with asynchronous databases, and containerization.

## Status
Under active development

## Tech Stack
- Python 3.12+
- FastAPI
- PostgreSQL (planned)
- Redis (planned)
- SQLAlchemy (async)
- Pytest
- JWT Authentication
- bcrypt

## Features

### Implemented
- URL shortening with auto-generated 6-character codes
- Redirect to original URLs with click logging
- User registration and authentication (JWT-based)
- Password hashing with bcrypt
- Link ownership and access control
- Click statistics per link
- Protected endpoints with token validation
- Async database operations
- Comprehensive test coverage (40+ tests)

### Planned
- User profile management
- Custom short codes (user-defined aliases)
- Advanced statistics (daily, devices, locations)
- Link expiration dates
- Redis caching
- Docker containerization

## API Endpoints

### Public
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/ping` | Health check |
| POST | `/users/register` | Register new user |
| POST | `/users/login` | Login and get JWT token |
| POST | `/links/` | Create short link (auth optional) |
| GET | `/links/{short_code}` | Redirect to original URL |

### Protected (JWT required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stats/{short_code}` | Get click statistics for your link |
| POST | `/links/` | Create link with user ownership |

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

1. Register a user: `POST /users/register`
2. Login: `POST /users/login` — receive `access_token`
3. Include token in requests: `Authorization: Bearer <token>`