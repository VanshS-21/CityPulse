# CityPulse Performance Optimization Guide

**Version**: 1.0.0  
**Last Updated**: July 9, 2025
**Target Audience**: DevOps Engineers, System Administrators, Developers  

---

## Table of Contents

1. [Performance Overview](#performance-overview)
2. [Frontend Optimization](#frontend-optimization)
3. [Backend Optimization](#backend-optimization)
4. [Database Optimization](#database-optimization)
5. [Infrastructure Optimization](#infrastructure-optimization)
6. [Monitoring and Alerting](#monitoring-and-alerting)
7. [Performance Testing](#performance-testing)
8. [Troubleshooting](#troubleshooting)

---

## Performance Overview

### 🎯 Performance Targets

| Metric | Target | Critical Threshold |
|--------|--------|--------------------|
| **Page Load Time** | < 2 seconds | < 3 seconds |
| **API Response Time** | < 500ms | < 1 second |
| **Database Query Time** | < 100ms | < 500ms |
| **Uptime** | 99.9% | 99.5% |
| **Error Rate** | < 0.1% | < 1% |

### 📊 Current Performance Baseline

```bash
# Performance monitoring dashboard
https://monitoring.citypulse.example.com/performance

# Key metrics to track:
- Average response time: 245ms
- 95th percentile: 890ms
- 99th percentile: 1.2s
- Error rate: 0.03%
- Throughput: 1,200 requests/minute
```

---

## Frontend Optimization

### ⚡ Next.js Optimization

#### Code Splitting and Lazy Loading

```javascript
// Implement dynamic imports for large components
const EventMap = dynamic(() => import('../components/EventMap'), {
  loading: () => <MapSkeleton />,
  ssr: false // Disable SSR for client-only components
});

// Route-based code splitting
const AdminDashboard = dynamic(() => import('../pages/admin/Dashboard'), {
  loading: () => <AdminSkeleton />
});
```

#### Image Optimization

```javascript
// Use Next.js Image component with optimization
import Image from 'next/image';

const EventImage = ({ src, alt }) => (
  <Image
    src={src}
    alt={alt}
    width={400}
    height={300}
    priority={false}
    placeholder="blur"
    blurDataURL="data:image/jpeg;base64,..."
    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  />
);
```

#### Bundle Analysis and Optimization

```bash
# Analyze bundle size
npm run build
npm run analyze

# Key optimizations:
# 1. Remove unused dependencies
npm uninstall unused-package

# 2. Use tree shaking
import { debounce } from 'lodash/debounce'; // Instead of entire lodash

# 3. Optimize third-party libraries
# Replace moment.js with date-fns (smaller bundle)
npm uninstall moment
npm install date-fns
```

### 🚀 Caching Strategies

#### Browser Caching

```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/static/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          }
        ]
      },
      {
        source: '/api/events',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, s-maxage=60, stale-while-revalidate=300'
          }
        ]
      }
    ];
  }
};
```

#### Service Worker Caching

```javascript
// sw.js - Service Worker for offline caching
const CACHE_NAME = 'citypulse-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/api/events?limit=50'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
  );
});
```

### 📱 Mobile Optimization

```javascript
// Implement virtual scrolling for large lists
import { FixedSizeList as List } from 'react-window';

const EventList = ({ events }) => (
  <List
    height={600}
    itemCount={events.length}
    itemSize={80}
    itemData={events}
  >
    {EventRow}
  </List>
);

// Optimize touch interactions
const useOptimizedTouch = () => {
  useEffect(() => {
    // Add passive event listeners for better scroll performance
    document.addEventListener('touchstart', handleTouchStart, { passive: true });
    document.addEventListener('touchmove', handleTouchMove, { passive: true });
    
    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchmove', handleTouchMove);
    };
  }, []);
};
```

---

## Backend Optimization

### 🔧 API Performance

#### Response Optimization

```python
# Implement response compression
from flask import Flask
from flask_compress import Compress

app = Flask(__name__)
Compress(app)

# Use pagination for large datasets
@app.route('/api/events')
def get_events():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    events = Event.query.paginate(
        page=page, 
        per_page=per_page,
        error_out=False
    )
    
    return {
        'data': [event.to_dict() for event in events.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': events.total,
            'pages': events.pages
        }
    }
```

#### Caching Layer

```python
# Implement Redis caching
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=600)  # Cache for 10 minutes
def get_event_analytics(category, start_date, end_date):
    # Expensive analytics calculation
    return calculate_analytics(category, start_date, end_date)
```

### 🌊 Apache Beam Optimization

#### Pipeline Performance

```python
# Optimize Beam pipeline performance
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

def optimize_beam_pipeline():
    pipeline_options = PipelineOptions([
        '--runner=DataflowRunner',
        '--project=citypulse-project',
        '--region=us-central1',
        '--temp_location=gs://citypulse-temp/temp',
        '--staging_location=gs://citypulse-temp/staging',
        '--num_workers=10',
        '--max_num_workers=50',
        '--autoscaling_algorithm=THROUGHPUT_BASED',
        '--worker_machine_type=n1-standard-4',
        '--disk_size_gb=100'
    ])
    
    with beam.Pipeline(options=pipeline_options) as pipeline:
        (pipeline
         | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(subscription=subscription)
         | 'Parse JSON' >> beam.Map(parse_json)
         | 'Window into fixed intervals' >> beam.WindowInto(
             beam.window.FixedWindows(60))  # 1-minute windows
         | 'Group by category' >> beam.GroupBy(lambda x: x['category'])
         | 'Aggregate data' >> beam.CombinePerKey(AggregateFn())
         | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
             table_spec,
             write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
             create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED))
```

#### Batch Processing Optimization

```python
# Implement efficient batch processing
class OptimizedEventProcessor(beam.DoFn):
    def __init__(self, batch_size=1000):
        self.batch_size = batch_size
        self.batch = []
    
    def process(self, element):
        self.batch.append(element)
        
        if len(self.batch) >= self.batch_size:
            # Process batch
            processed_batch = self.process_batch(self.batch)
            for item in processed_batch:
                yield item
            self.batch = []
    
    def finish_bundle(self):
        # Process remaining items
        if self.batch:
            processed_batch = self.process_batch(self.batch)
            for item in processed_batch:
                yield item
            self.batch = []
    
    def process_batch(self, batch):
        # Efficient batch processing logic
        return [self.process_single_item(item) for item in batch]
```

---

## Database Optimization

### 🔥 Firestore Optimization

#### Query Optimization

```javascript
// Optimize Firestore queries
const optimizeFirestoreQueries = () => {
  // Use composite indexes for complex queries
  const eventsRef = db.collection('events');
  
  // Efficient query with proper indexing
  const query = eventsRef
    .where('category', '==', 'traffic')
    .where('status', '==', 'active')
    .orderBy('created_at', 'desc')
    .limit(20);
  
  // Use pagination for large datasets
  const paginatedQuery = eventsRef
    .orderBy('created_at', 'desc')
    .startAfter(lastDocument)
    .limit(20);
  
  return { query, paginatedQuery };
};

// Implement connection pooling
const initializeFirestore = () => {
  const settings = {
    cacheSizeBytes: 100 * 1024 * 1024, // 100 MB cache
    experimentalForceLongPolling: false,
    merge: true
  };
  
  db.settings(settings);
};
```

#### Data Structure Optimization

```javascript
// Optimize document structure for performance
const optimizedEventDocument = {
  // Flatten nested objects when possible
  title: 'Traffic Accident',
  category: 'traffic',
  severity: 'high',
  status: 'active',
  
  // Use arrays for tags instead of nested objects
  tags: ['accident', 'traffic', 'emergency'],
  
  // Separate large fields into subcollections
  // Instead of storing all comments in the document:
  // comments: [] // This can grow large
  
  // Use subcollection:
  // /events/{eventId}/comments/{commentId}
  
  // Use map for location data
  location: {
    lat: 34.0522,
    lng: -118.2437,
    geohash: '9q5ctr' // For geospatial queries
  },
  
  // Optimize timestamps
  created_at: admin.firestore.FieldValue.serverTimestamp(),
  updated_at: admin.firestore.FieldValue.serverTimestamp()
};
```

### 📊 BigQuery Optimization

#### Query Performance

```sql
-- Optimize BigQuery queries for performance

-- Use partitioning and clustering
CREATE TABLE city_intelligence.events_optimized (
  event_id STRING NOT NULL,
  event_type STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  location_lat FLOAT64,
  location_lng FLOAT64,
  ward_name STRING,
  severity_level STRING,
  metadata JSON
)
PARTITION BY DATE(timestamp)
CLUSTER BY ward_name, event_type, severity_level;

-- Efficient query patterns
-- Good: Use partition pruning
SELECT event_type, COUNT(*) as count
FROM city_intelligence.events_optimized
WHERE DATE(timestamp) BETWEEN '2025-01-01' AND '2025-01-31'
  AND ward_name = 'Downtown'
GROUP BY event_type;

-- Good: Use clustering columns in WHERE clause
SELECT *
FROM city_intelligence.events_optimized
WHERE ward_name = 'Downtown'
  AND event_type = 'traffic'
  AND severity_level = 'high'
  AND DATE(timestamp) = '2025-01-15';

-- Avoid: Full table scans
-- SELECT * FROM city_intelligence.events_optimized; -- Don't do this
```

#### Cost Optimization

```sql
-- Implement cost-effective querying strategies

-- Use approximate aggregation for large datasets
SELECT 
  event_type,
  APPROX_COUNT_DISTINCT(event_id) as unique_events,
  APPROX_QUANTILES(severity_score, 100)[OFFSET(50)] as median_severity
FROM city_intelligence.events_optimized
WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY event_type;

-- Use materialized views for frequently accessed aggregations
CREATE MATERIALIZED VIEW city_intelligence.daily_event_summary
PARTITION BY event_date
CLUSTER BY ward_name, event_type
AS
SELECT 
  DATE(timestamp) as event_date,
  ward_name,
  event_type,
  COUNT(*) as event_count,
  AVG(severity_score) as avg_severity,
  COUNT(DISTINCT user_id) as unique_reporters
FROM city_intelligence.events_optimized
WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
GROUP BY 1, 2, 3;
```

---

## Infrastructure Optimization

### ☁️ Google Cloud Optimization

#### Compute Optimization

```yaml
# Cloud Run optimization
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: citypulse-api
  annotations:
    run.googleapis.com/cpu-throttling: "false"
    run.googleapis.com/execution-environment: gen2
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "2"
        autoscaling.knative.dev/maxScale: "100"
        run.googleapis.com/memory: "2Gi"
        run.googleapis.com/cpu: "2"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
      - image: gcr.io/citypulse/api:latest
        resources:
          limits:
            memory: "2Gi"
            cpu: "2"
        env:
        - name: NODE_ENV
          value: "production"
```

#### CDN Configuration

```yaml
# Cloud CDN setup for static assets
apiVersion: v1
kind: ConfigMap
metadata:
  name: cdn-config
data:
  cdn.yaml: |
    name: citypulse-cdn
    description: "CDN for CityPulse static assets"
    defaultService: citypulse-backend
    hostRules:
    - hosts:
      - "static.citypulse.example.com"
      pathMatcher: "static-matcher"
    pathMatchers:
    - name: "static-matcher"
      defaultService: citypulse-storage
      pathRules:
      - paths:
        - "/static/*"
        - "/images/*"
        - "/js/*"
        - "/css/*"
        service: citypulse-storage
    backends:
    - name: citypulse-storage
      bucketName: "citypulse-static-assets"
      enableCdn: true
      cdnPolicy:
        cacheMode: "CACHE_ALL_STATIC"
        defaultTtl: 3600
        maxTtl: 86400
        clientTtl: 3600
```

### 🔄 Load Balancing

```yaml
# Application Load Balancer configuration
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: citypulse-ssl-cert
spec:
  domains:
  - citypulse.example.com
  - api.citypulse.example.com
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: citypulse-ingress
  annotations:
    kubernetes.io/ingress.global-static-ip-name: "citypulse-ip"
    networking.gke.io/managed-certificates: "citypulse-ssl-cert"
    kubernetes.io/ingress.class: "gce"
    cloud.google.com/backend-config: '{"default": "citypulse-backend-config"}'
spec:
  rules:
  - host: citypulse.example.com
    http:
      paths:
      - path: /*
        pathType: ImplementationSpecific
        backend:
          service:
            name: citypulse-frontend
            port:
              number: 80
  - host: api.citypulse.example.com
    http:
      paths:
      - path: /*
        pathType: ImplementationSpecific
        backend:
          service:
            name: citypulse-api
            port:
              number: 8080
```

---

## Monitoring and Alerting

### 📊 Performance Monitoring

```yaml
# Prometheus monitoring configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
    - "citypulse_rules.yml"
    
    scrape_configs:
    - job_name: 'citypulse-api'
      static_configs:
      - targets: ['citypulse-api:8080']
      metrics_path: '/metrics'
      scrape_interval: 10s
    
    - job_name: 'citypulse-frontend'
      static_configs:
      - targets: ['citypulse-frontend:3000']
      metrics_path: '/api/metrics'
      scrape_interval: 30s
```

### 🚨 Alerting Rules

```yaml
# Alert rules for performance issues
groups:
- name: citypulse_performance
  rules:
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }}s"
  
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }}"
  
  - alert: DatabaseSlowQueries
    expr: mysql_slow_queries > 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Database slow queries detected"
      description: "{{ $value }} slow queries in the last 5 minutes"
```

---

## Performance Testing

### 🧪 Load Testing

```javascript
// K6 load testing script
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 200 }, // Ramp up to 200 users
    { duration: '5m', target: 200 }, // Stay at 200 users
    { duration: '2m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% of requests under 1s
    http_req_failed: ['rate<0.01'],    // Error rate under 1%
  },
};

export default function() {
  // Test event listing endpoint
  let response = http.get('https://api.citypulse.example.com/v1/events?limit=20');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
  
  // Test event creation
  let payload = JSON.stringify({
    title: 'Load test event',
    category: 'traffic',
    location: { lat: 34.0522, lng: -118.2437 }
  });
  
  let params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer test-token'
    },
  };
  
  response = http.post('https://api.citypulse.example.com/v1/events', payload, params);
  check(response, {
    'event created': (r) => r.status === 201,
  });
  
  sleep(2);
}
```

### 📈 Performance Benchmarking

```bash
#!/bin/bash
# Performance benchmarking script

echo "Starting CityPulse Performance Benchmark..."

# Frontend performance test
echo "Testing frontend performance..."
lighthouse https://citypulse.example.com \
  --output=json \
  --output-path=./reports/lighthouse-report.json \
  --chrome-flags="--headless"

# API performance test
echo "Testing API performance..."
ab -n 1000 -c 10 -H "X-API-Key: test-key" \
  https://api.citypulse.example.com/v1/events > ./reports/api-benchmark.txt

# Database performance test
echo "Testing database performance..."
k6 run --out json=./reports/db-performance.json ./tests/db-load-test.js

# Generate performance report
echo "Generating performance report..."
node ./scripts/generate-performance-report.js

echo "Performance benchmark complete. Check ./reports/ for results."
```

---

## Troubleshooting

### 🔍 Common Performance Issues

#### Slow API Responses

```bash
# Diagnose slow API responses
# 1. Check application logs
kubectl logs -f deployment/citypulse-api --tail=100

# 2. Monitor database queries
# Enable slow query log in Cloud SQL
gcloud sql instances patch citypulse-db \
  --database-flags=slow_query_log=on,long_query_time=1

# 3. Check memory usage
kubectl top pods -l app=citypulse-api

# 4. Analyze request patterns
# Check Cloud Monitoring for request distribution
```

#### High Memory Usage

```javascript
// Memory leak detection and prevention
const memwatch = require('memwatch-next');

// Monitor memory leaks
memwatch.on('leak', (info) => {
  console.error('Memory leak detected:', info);
  // Send alert to monitoring system
});

// Periodic garbage collection
setInterval(() => {
  if (global.gc) {
    global.gc();
  }
}, 60000); // Every minute

// Monitor heap usage
const monitorMemory = () => {
  const usage = process.memoryUsage();
  console.log('Memory usage:', {
    rss: Math.round(usage.rss / 1024 / 1024) + ' MB',
    heapTotal: Math.round(usage.heapTotal / 1024 / 1024) + ' MB',
    heapUsed: Math.round(usage.heapUsed / 1024 / 1024) + ' MB',
    external: Math.round(usage.external / 1024 / 1024) + ' MB'
  });
};

setInterval(monitorMemory, 30000); // Every 30 seconds
```

#### Database Connection Issues

```python
# Database connection pool optimization
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Optimize connection pool settings
engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=20,          # Number of connections to maintain
    max_overflow=30,       # Additional connections allowed
    pool_pre_ping=True,    # Validate connections before use
    pool_recycle=3600,     # Recycle connections every hour
    echo=False             # Disable SQL logging in production
)

# Monitor connection pool
def monitor_connection_pool():
    pool = engine.pool
    return {
        'size': pool.size(),
        'checked_in': pool.checkedin(),
        'checked_out': pool.checkedout(),
        'overflow': pool.overflow(),
        'invalid': pool.invalid()
    }
```

### 📋 Performance Checklist

```markdown
## Daily Performance Checks
- [ ] Check response time metrics (< 500ms average)
- [ ] Monitor error rates (< 0.1%)
- [ ] Verify database query performance
- [ ] Check memory and CPU usage
- [ ] Review slow query logs

## Weekly Performance Reviews
- [ ] Analyze performance trends
- [ ] Review and optimize slow queries
- [ ] Check cache hit rates
- [ ] Monitor storage usage
- [ ] Update performance baselines

## Monthly Performance Optimization
- [ ] Conduct load testing
- [ ] Review and update performance targets
- [ ] Optimize database indexes
- [ ] Review and clean up unused resources
- [ ] Plan capacity scaling
```

---

*This performance guide provides comprehensive strategies for optimizing CityPulse across all layers of the application stack.*
