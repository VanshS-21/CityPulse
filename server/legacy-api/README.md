# CityPulse REST API

The official REST API for the CityPulse platform, providing comprehensive services for urban issue reporting, data management, and user engagement.

## 🚀 Features

- **Event Management**: Full CRUD operations for urban events and reports
- **User Profiles**: User authentication and profile management with Firebase Auth
- **Feedback System**: User feedback collection and management
- **Analytics**: Comprehensive analytics and KPI endpoints
- **Real-time Data**: Integration with Firestore and BigQuery
- **AI Integration**: AI-powered event processing and insights
- **Role-based Access**: Granular permissions for citizens, authorities, and admins
- **Public API**: Limited public access with API keys

## 🏗️ Architecture

- **Framework**: FastAPI with Python 3.11
- **Authentication**: Firebase Authentication with JWT tokens
- **Database**: Google Cloud Firestore (primary) + BigQuery (analytics)
- **Deployment**: Google Cloud Run with Docker containers
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## 📋 Prerequisites

- Python 3.11+
- Google Cloud Project with enabled APIs:
  - Cloud Run API
  - Cloud Build API
  - Firestore API
  - BigQuery API
  - Firebase Authentication
- Docker (for deployment)
- gcloud CLI (for deployment)

## 🛠️ Installation

### Local Development

1. **Clone and navigate to API directory**:
   ```bash
   cd api
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   export PROJECT_ID="your-gcp-project-id"
   ```

5. **Run the development server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Production Deployment

1. **Make deployment script executable**:
   ```bash
   chmod +x deploy.sh
   ```

2. **Deploy to Cloud Run**:
   ```bash
   ./deploy.sh
   ```

3. **Or deploy with custom configuration**:
   ```bash
   PROJECT_ID="your-project" REGION="us-central1" ./deploy.sh
   ```

## 📚 API Documentation

### Base URL
- **Production**: `https://api.citypulse.example.com/v1`
- **Development**: `http://localhost:8000/v1`

### Authentication

The API supports two authentication methods:

1. **Firebase JWT Token** (for authenticated users):
   ```
   Authorization: Bearer <firebase-jwt-token>
   ```

2. **API Key** (for public endpoints):
   ```
   X-API-Key: <your-api-key>
   ```

### Core Endpoints

#### Events
- `GET /v1/events` - List events (with filtering and pagination)
- `GET /v1/events/{id}` - Get specific event
- `POST /v1/events` - Create new event
- `PUT /v1/events/{id}` - Update event
- `DELETE /v1/events/{id}` - Delete event (admin only)

#### Users
- `GET /v1/users/me` - Get current user profile
- `PUT /v1/users/me` - Update current user profile
- `GET /v1/users/{id}` - Get user profile (authorities only)
- `PUT /v1/users/{id}` - Update user profile (admin only)
- `DELETE /v1/users/{id}` - Delete user (admin only)

#### Feedback
- `GET /v1/feedback` - List all feedback (authorities only)
- `GET /v1/feedback/my` - List current user's feedback
- `GET /v1/feedback/{id}` - Get specific feedback
- `POST /v1/feedback` - Submit feedback
- `PUT /v1/feedback/{id}/status` - Update feedback status (authorities only)
- `DELETE /v1/feedback/{id}` - Delete feedback

#### Analytics
- `GET /v1/analytics/kpis` - Get key performance indicators
- `GET /v1/analytics/trends` - Get trend data
- `GET /v1/analytics/public/summary` - Get public summary (no auth required)
- `GET /v1/analytics/events/by-category` - Get events by category
- `GET /v1/analytics/events/by-location` - Get events by location
- `GET /v1/analytics/performance` - Get performance metrics (admin only)

### Filtering and Pagination

Most list endpoints support filtering and pagination:

```
GET /v1/events?category=infrastructure&status=pending&page=1&limit=20&sort_by=created_at&sort_order=desc
```

**Filter Parameters**:
- `category`, `status`, `severity`, `source`
- `latitude`, `longitude`, `radius` (for location-based filtering)
- `start_date`, `end_date` (for date range filtering)
- `search` (text search in title and description)
- `user_id` (filter by user)

**Pagination Parameters**:
- `page` (page number, default: 1)
- `limit` (items per page, default: 20, max: 100)
- `cursor` (for cursor-based pagination)

**Sorting Parameters**:
- `sort_by` (field to sort by, default: created_at)
- `sort_order` (asc/desc, default: desc)

## 🔐 Permissions

### User Roles
- **Public**: Limited read access with API key
- **Citizen**: Can create events and feedback, manage own profile
- **Authority**: Can update event status, read all feedback, access analytics
- **Admin**: Full access to all operations

### Permission Matrix
| Operation | Public | Citizen | Authority | Admin |
|-----------|--------|---------|-----------|-------|
| Read Events | ✓ (limited) | ✓ | ✓ | ✓ |
| Create Events | ✗ | ✓ | ✓ | ✓ |
| Update Events | ✗ | ✓ (own) | ✓ | ✓ |
| Update Event Status | ✗ | ✗ | ✓ | ✓ |
| Delete Events | ✗ | ✗ | ✗ | ✓ |
| Read User Profiles | ✗ | ✓ (own) | ✓ | ✓ |
| Update User Profiles | ✗ | ✓ (own) | ✗ | ✓ |
| Read Feedback | ✗ | ✓ (own) | ✓ | ✓ |
| Create Feedback | ✗ | ✓ | ✓ | ✓ |
| Update Feedback | ✗ | ✗ | ✓ | ✓ |
| Read Analytics | ✗ | ✗ | ✓ | ✓ |
| Read Detailed Analytics | ✗ | ✗ | ✗ | ✓ |

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Manual Testing
Use the interactive API documentation at `/docs` to test endpoints manually.

## 📊 Monitoring

### Health Checks
- **Endpoint**: `/health`
- **Response**: Service status and version information

### Logging
- Structured logging with correlation IDs
- Error tracking and performance monitoring
- Integration with Google Cloud Logging

### Metrics
- Request/response metrics
- Error rates and latency
- Custom business metrics

## 🔧 Configuration

### Environment Variables
- `PROJECT_ID`: Google Cloud Project ID
- `GCP_REGION`: Google Cloud Region
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key
- `VALID_API_KEYS`: Comma-separated list of valid API keys
- `PORT`: Server port (default: 8080)

### Firebase Configuration
Ensure Firebase Authentication is properly configured with:
- Authorized domains
- Sign-in methods
- Custom claims for user roles

## 🚨 Error Handling

The API returns standardized error responses:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "status_code": 422,
  "path": "/v1/events",
  "details": {
    "field_errors": [
      {
        "field": "title",
        "message": "Title is required"
      }
    ]
  },
  "timestamp": "2025-01-07T12:00:00Z"
}
```

### Common Error Codes
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error

## 📈 Performance

### Optimization Features
- Async/await for non-blocking operations
- Connection pooling for database clients
- Efficient pagination with cursor support
- Caching for frequently accessed data
- Optimized BigQuery queries for analytics

### Rate Limiting
- Per-user rate limiting
- Different limits for different user roles
- Graceful degradation under load

## 🔄 Development Workflow

1. **Feature Development**:
   - Create feature branch
   - Implement changes with tests
   - Update documentation
   - Submit pull request

2. **Testing**:
   - Unit tests for business logic
   - Integration tests for API endpoints
   - End-to-end tests for critical flows

3. **Deployment**:
   - Automated deployment via Cloud Build
   - Blue-green deployment strategy
   - Rollback capabilities

## 📞 Support

For issues and questions:
- Check the API documentation at `/docs`
- Review error messages and logs
- Contact the development team

## 📄 License

MIT License - see LICENSE file for details.
