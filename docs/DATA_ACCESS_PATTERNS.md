# Data Access Patterns

This document outlines the primary patterns for accessing and manipulating data in the CityPulse application. Understanding these patterns is crucial for developing new features and maintaining data consistency across the clients (web and mobile) and backend services.

## 1. Hybrid Data Access Model

CityPulse employs a hybrid data access model to balance real-time responsiveness with the need for complex business logic and security. Clients use a combination of direct database access and a dedicated backend API.

-   **Direct Firestore Access**: For real-time features where low latency is critical.
-   **Backend REST API**: For all other operations, including complex queries, business logic, and secure data manipulation.

## 2. Direct Firestore Access (for Real-Time Features)

Direct access to Firestore from the client is reserved for specific real-time use cases.

-   **Usage**: Primarily for subscribing to live data updates, such as displaying real-time event markers on the map or updating live KPI dashboards.
-   **Mechanism**: The frontend and mobile applications use the Firebase SDK to establish real-time listeners (`onSnapshot`) on specific Firestore collections or documents.
-   **Security**: Access is controlled by a robust set of **Firestore Security Rules**. These rules enforce authentication, ensuring that users can only read or write data they are authorized to access. **It is critical that these rules are meticulously maintained to prevent unauthorized data access.**

### Example: Subscribing to Live Events

```typescript
// Example in a Next.js component
import { collection, onSnapshot } from 'firebase/firestore';
import { db } from '../lib/firebase'; // Your Firebase config

useEffect(() => {
  const q = collection(db, 'events');
  const unsubscribe = onSnapshot(q, (querySnapshot) => {
    const events = [];
    querySnapshot.forEach((doc) => {
      events.push({ id: doc.id, ...doc.data() });
    });
    // Update the UI with the new events
    setLiveEvents(events);
  });

  // Unsubscribe when the component unmounts
  return () => unsubscribe();
}, []);
```

## 3. Backend REST API (for Business Logic & CRUD)

The backend REST API (planned, to be built on Cloud Run/Functions) will be the primary method for most data interactions.

-   **Usage**: All create, update, and delete (CUD) operations, as well as complex read operations (queries with joins, aggregations) that are not suitable for Firestore's security model.
-   **Mechanism**: Clients make standard HTTPS requests to the API endpoints (e.g., `POST /api/v1/events`).
-   **Responsibilities of the API**:
    -   **Authentication & Authorization**: Validating the user's identity token and checking their role (Citizen, Authority, Admin) before performing any action.
    -   **Input Validation**: Ensuring all incoming data conforms to the required schema.
    -   **Business Logic**: Executing complex logic that should not reside on the client (e.g., calculating analytics, triggering notifications).
    -   **Data Orchestration**: Interacting with multiple services (e.g., writing to BigQuery, publishing to Pub/Sub, updating Firestore) in a single transaction.

### Example: Submitting a New Event

```typescript
// Example of submitting a new event from the client
async function submitNewEvent(eventData) {
  const token = await getAuthToken(); // Get the user's Firebase auth token

  const response = await fetch('/api/v1/events', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(eventData),
  });

  if (!response.ok) {
    throw new Error('Failed to submit event');
  }

  return await response.json();
}
```

## Summary of Patterns

| Use Case | Recommended Pattern | Rationale |
| :--- | :--- | :--- |
| **Displaying live map data** | Direct Firestore Access | Lowest latency for real-time updates. |
| **Submitting a new report** | Backend REST API | Enforces business logic, validation, and triggers async workflows. |
| **Updating a user profile** | Backend REST API | Ensures security and data integrity. |
| **Fetching historical analytics**| Backend REST API | Allows for complex queries on BigQuery that are not possible with the Firestore SDK. |
| **Real-time chat/notifications**| Direct Firestore Access | Ideal for low-latency, subscription-based features. |

By adhering to these patterns, we ensure that the CityPulse application remains secure, scalable, and maintainable as it evolves.
