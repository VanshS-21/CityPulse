# CityPulse API Documentation

## Overview

The CityPulse API provides endpoints for managing urban issues, user authentication, analytics, and real-time notifications. This RESTful API supports JSON requests and responses.

## Base URL

```
Production: https://api.citypulse.com
Development: http://localhost:3000/api
```

## Authentication

All API requests require authentication using Bearer tokens:

```
Authorization: Bearer <your-token>
```

## Endpoints

### Authentication

#### POST /api/auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "jwt-token",
    "user": {
      "id": "user-id",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "citizen"
    }
  }
}
```

#### POST /api/auth/register
Register a new user account.

#### POST /api/auth/logout
Logout and invalidate token.

### Issues

#### GET /api/issues
Get paginated list of issues.

**Query Parameters:**
- `page` (number): Page number (default: 1)
- `limit` (number): Items per page (default: 20)
- `category` (string): Filter by category
- `status` (string): Filter by status
- `priority` (string): Filter by priority

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "issue-id",
      "title": "Pothole on Main Street",
      "description": "Large pothole causing traffic issues",
      "category": "infrastructure",
      "priority": "high",
      "status": "open",
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "123 Main St, New York, NY"
      },
      "images": ["image-url-1", "image-url-2"],
      "reportedBy": "user-id",
      "createdAt": "2024-01-01T00:00:00Z",
      "upvotes": 15,
      "downvotes": 2
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

#### POST /api/issues
Create a new issue.

#### GET /api/issues/:id
Get specific issue details.

#### PUT /api/issues/:id
Update an issue (admin/moderator only).

#### DELETE /api/issues/:id
Delete an issue (admin only).

#### POST /api/issues/:id/vote
Vote on an issue (upvote/downvote).

### Analytics

#### GET /api/analytics/overview
Get dashboard analytics overview.

#### GET /api/analytics/trends
Get trend data for charts.

#### GET /api/analytics/insights
Get AI-powered insights.

### Notifications

#### GET /api/notifications
Get user notifications.

#### POST /api/notifications/mark-read
Mark notifications as read.

### File Upload

#### POST /api/upload
Upload files (images, documents).

**Request:** Multipart form data with file field.

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://storage.example.com/file-id",
    "filename": "original-filename.jpg",
    "size": 1024000,
    "type": "image/jpeg"
  }
}
```

## Error Handling

All errors follow this format:

```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

### Common Error Codes

- `UNAUTHORIZED` (401): Invalid or missing authentication
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `VALIDATION_ERROR` (400): Invalid request data
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error

## Rate Limiting

API requests are limited to:
- 1000 requests per hour per user
- 50 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Webhooks

CityPulse supports webhooks for real-time notifications:

### Events
- `issue.created`
- `issue.updated`
- `issue.resolved`
- `user.registered`

### Webhook Payload
```json
{
  "event": "issue.created",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "issue": { /* issue object */ }
  }
}
```

## SDKs and Libraries

- JavaScript/TypeScript: `@citypulse/js-sdk`
- Python: `citypulse-python`
- React Hooks: `@citypulse/react-hooks`

## Support

For API support, contact: api-support@citypulse.com
