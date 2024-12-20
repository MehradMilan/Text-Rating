# Text Rating System Documentation
### Mehrad Milanloo
---

### **Introduction**
This project is a robust **text-rating system** built using `Django`, `Kafka`, `Redis`, `Celery`, `PostgreSQL`, and `Docker`. It is designed to efficiently handle a large number of user interactions and provide features like dynamic average rating updates, anomaly detection, and scalable backend processing.
The system focuses on user-generated posts that can be rated by other users. Key functionalities include buffering and processing ratings to ensure integrity, detecting and mitigating spam or anomalies, and providing real-time analytics of posts based on user engagement.

### **Key Features**

- **User Authentication**: Secure user registration and login.

- **Post Management**: Create, retrieve, and display posts with detailed analytics.

- **Rating System**:

  - Users can rate posts.

  - Ratings are buffered and processed asynchronously.

  - Average ratings are calculated efficiently with database-backed storage.

  - Anomaly detection prevents spam or malicious behavior.

- **Analytics**:

  - Display top-rated and most-rated posts.

- **Scalability**:

  - Multiple Django replicas managed via Docker Compose.

  - Nginx as a load balancer.

- **Periodic Tasks**:

  - Celery-Beat schedules tasks like rating anomaly detection and average rating updates.

- **Monitoring**:

  - Prometheus integration for metrics collection and analysis.


## **2. Handling Requirements**

### **2.1 Scalability**
The system supports high traffic by:

1. Running **Django replicas** using Docker Compose, ensuring multiple backend instances handle requests concurrently.

2. **Nginx as a load balancer**: Efficiently distributes incoming requests among Django replicas.

3. Stateless design ensures horizontal scaling by adding replicas as needed.

### **2.2 High Request Load**
Redis caching minimizes database queries for frequently accessed data, such as post details and average ratings. Celery workers handle resource-intensive operations asynchronously to prevent bottlenecks in request processing.

### **2.3 Anomaly and Spam Detection**

#### Problem
Users can spam ratings, skewing the average score and reducing the reliability of ratings.

#### Solution

1. **Buffering Ratings**:

   - User's Rating to the post is immediately updated.

   - Ratings effects on the Average rating are temporarily stored in Redis with timestamps.

   - This allows processing ratings in batches, ensuring real-time performance.

2. **Anomaly Detection**:

   - A threshold (e.g., 60% identical scores in a buffer) is defined to detect spam.

   - If an anomaly is detected, buffered ratings are discarded, protecting the integrity of the system.

3. **Improved Rating Calculation**:

   - Processed ratings update a dedicated database table (`PostAverageRating`) to store average scores directly.

#### Why This Is Better

- **Efficiency**: By buffering and batch-processing ratings, we avoid excessive database writes.

- **Real-time Monitoring**: Immediate detection of anomalies ensures timely action.

- **Accuracy**: Prevents malicious users from distorting post ratings.

- **Open to enhancements**: Anomaly Detection and ML models can easily be adopted.

### **2.4 Kafka for Message Brokering**

Kafka serves as the backbone for handling real-time events in the system:

1. **Asynchronous Processing**: Ratings are sent to Kafka topics, ensuring the system can handle many concurrent requests without blocking.

2. **Scalability**: Kafka’s partitioning allows distributing the load across multiple consumers.

3. **Durability**: Guarantees message delivery even in cases of service interruptions.

## **3. Project Architecture**

### **System Components**

- **Django**: The backend framework.

- **Celery**: Manages asynchronous tasks, such as processing ratings.

- **Kafka**: Handles event-driven communication for ratings.

- **Redis**: Buffers user ratings and caches frequently accessed data.

- **PostgreSQL**: Stores persistent data, including posts and ratings.

- **Nginx**: Load balancer and reverse proxy for scaling.

- **Prometheus**: Collects and visualizes performance metrics.


## **4. Setup and Installation**

### **Prerequisites**
- Docker and Docker Compose installed.

### **Starting the Project**

1. Build and run the Docker containers:

   ```bash
   docker-compose up --build
   ```

2. Access the application at `http://localhost:8080`.


## **5. Features**

### **5.1 Authentication**

- **Registration and Login APIs** enable user authentication.

- **JWToken**: The project uses `JWToken` for authentication.

### **5.2 Post Management**

- Users can create and view posts.

- Each post displays its average rating and the user’s rating, if applicable.

- **Pagination**: The project provides pagination in every url that returns a list of items.

### **5.3 Rating System**

1. **Add Rating**:

   - Users can rate a post between 0 and 5.

2. **Buffered Ratings**:

   - User's Rating is immediately updated, but the Post's average rating update needs to pass suspicious examination.

   - Ratings are stored temporarily in Redis for processing.

3. **Anomaly Detection**:

   - Detects and removes spam ratings.

4. **Average Rating Calculation**:

   - Uses the `PostAverageRating` table for efficiency.

### **5.4 Analytics**

- **Top-Rated Posts**:

  - Displays posts with the highest average rating.

- **Most-Rated Posts**:

  - Displays posts with the most user engagement.

### **5.5 Scalability**

- **Docker Compose Replicas**:

  - Multiple Django services handle concurrent requests.

- **Nginx**:

  - Manages load balancing and secure traffic routing.

### **5.6 Kafka Integration**

- **Real-time Rating Processing**:

  - Kafka handles asynchronous message passing for ratings.

- **Event Resilience**:

  - Guarantees delivery of rating events with retries in case of failure.

### **5.7. Monitoring and Logging**

- **Prometheus Integration**

  - Monitors metrics like request rates, task completion times, and system health.

  - Accessible at `http://localhost:9090`.

- **Log Management**

  - All service logs are accessible via `docker logs <container-name>`.

---

## **7. API Documentation**

### **Using Swagger for API Documentation**

- Access Swagger UI at `http://localhost:8080/swagger/`.

## **8. Endpoints**

### Auth APIs

#### Register User

- **URL**: `/api/register/`

- **Method**: `POST`

- **Description**: Registers a new user.

- **Request Body**:

```
{
    "username": "string",
    "password": "string",
    "email": "string"
}
```

- **Response**:

  - **201 Created**:

```
{
    "message": "User registered successfully"
}

```

  - **400 Bad Request**:

```
{
    "error": "Validation error details"
}
```

#### Login User

- **URL**: `/api/login/`

- **Method**: `POST`

- **Description**: Authenticates a user and provides a JWT token.

- **Request Body**:

```
{
    "username": "string",
    "password": "string"
}
```

- **Response**:

  - **200 OK**:

```
{
    "token": "JWT token string"
}
```

  - **400 Bad Request**:

```
{
    "error": "Invalid credentials"
}
```

### Post APIs

#### List Posts

- **URL**: `/api/posts/`

- **Method**: `GET`

- **Description**: Retrieves a list of all posts.

- **Pagination Parameters**:

  - `?page=<page_number>`

  - `?page_size=<page_size>`

- **Response**:

  - **200 OK**:

```
{
    "count": "total number of posts",
    "next": "URL for next page",
    "previous": "URL for previous page",
    "results": [
        {
            "id": "post_id",
            "title": "string",
            "content": "string",
            "average_rating": "float",
            "user_rating": "integer (user-specific)"
        }
    ]
}
```

#### Create Post

- **URL**: `/api/create-post/`

- **Method**: `POST`

- **Headers**: 

  - `Authorization: Bearer <token>`

- **Description**: Creates a new post.

- **Request Body**:

```
{
    "title": "string",
    "content": "string"
}
```

- **Response**:

  - **201 Created**:

```
{
    "message": "Post created successfully",
    "data": {
        "id": "post_id",
        "title": "string",
        "content": "string",
        "average_rating": "float",
        "user_rating": null
    }
}
```

  - **400 Bad Request**:

```
{
    "error": "Validation error details"
}
```

### Rating APIs

#### Add/Update Rating

- **URL**: `/api/ratings/`

- **Method**: `POST`

- **Headers**: 

  - `Authorization: Bearer <token>`

- **Description**: Adds or updates a user's rating for a specific post.

- **Request Body**:

```
{
    "post": "post_id",
    "score": "integer (0-5)"
}
```

- **Response**:

  - **200 OK**:

```
{
    "message": "Rating buffered successfully"
}
```

  - **400 Bad Request**:

```
{
    "error": "Score must be between 0 and 5"
}
```

### Analytics APIs

#### Get Analytics

- **URL**: `/analytics/`

- **Method**: `GET`

- **Description**: Retrieves analytics for posts, including the most rated and top-rated posts.

- **Response**:

  - **200 OK**:

```
{
    "most_rated": [
        ["post_id", "number_of_ratings"]
    ],
    "top_rated": [
        {
            "post_id": "post_id",
            "average_rating": "float"
        }
    ]
}
```