# JWT Authentication Guide

## Overview

This guide explains how to use JWT (JSON Web Token) authentication in the KMA Chatbot application.

## Setup

1. JWT authentication has been implemented using the following components:
   - JWT token generation and validation
   - Protected endpoints
   - User authentication

2. Configuration:
   - JWT settings are directly loaded from `.env` file in each module:
     ```
     JWT_SECRET_KEY=your-secret-key
     JWT_ALGORITHM=HS256
     JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
     JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
     ```
   - Make sure to change `JWT_SECRET_KEY` to a secure random string in production.

## How to Use

### 1. Login to Get JWT Token

```
POST /api/auth/login
```

**Request Body (Form Data):**
```
username: <your_username>
password: <your_password>
```

**Response:**
```json
{
  "statusCode": 200,
  "message": "Đăng nhập thành công",
  "data": {
    "access_token": "<your_jwt_token>",
    "refresh_token": "<your_refresh_token>",
    "token_type": "bearer"
  }
}
```

### 2. Use JWT Token in Requests

Add the JWT token to the `Authorization` header for protected endpoints:

```
Authorization: Bearer <your_jwt_token>
```

### 3. Refresh Token

When your access token expires, use the refresh token to get a new pair of tokens:

```
POST /api/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "<your_refresh_token>"
}
```

**Response:**
```json
{
  "statusCode": 200,
  "message": "Token đã được làm mới thành công",
  "data": {
    "access_token": "<new_access_token>",
    "refresh_token": "<new_refresh_token>",
    "token_type": "bearer"
  }
}
```

### 4. Get Current User Info

```
GET /api/auth/me
```

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
{
  "statusCode": 200,
  "message": "Lấy thông tin người dùng thành công",
  "data": {
    "_id": "user_id",
    "username": "username",
    "student_code": "student_code",
    "student_name": "student_name",
    "student_class": "student_class",
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
}
```

## For Frontend Developers

1. Store the JWT token securely (e.g., in localStorage or httpOnly cookies)
2. Add the token to all API requests that require authentication
3. Implement token refresh mechanism if needed
4. Handle authentication errors (401 Unauthorized)

## Protected Endpoints

The following endpoints require authentication:

- `GET /api/chat/conversations` - Get user's conversations
- Other endpoints can be protected by adding `current_user: UserResponse = Depends(require_auth)` parameter

## Implementation Details

1. JWT authentication is implemented in:
   - `src/backend/auth/jwt.py` - JWT utilities (loads settings directly from .env)
   - `src/backend/auth/dependencies.py` - Authentication dependencies
   - `src/backend/api/auth.py` - Authentication endpoints (loads settings directly from .env)

2. To protect an endpoint, add the `require_auth` dependency:

```python
@router.get("/your-endpoint")
async def your_endpoint(current_user: UserResponse = Depends(require_auth)):
    # Your code here
    # You can use current_user._id to get the user ID
    return {"message": "Protected endpoint"}
```
