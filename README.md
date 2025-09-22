# Flask API Practice Project

This repository contains practice implementations of **RESTful APIs using Flask**, covering basic, intermediate, and advanced endpoints. It’s designed to help understand core Flask features like routing, request handling, JWT authentication, file uploads, pagination, external API integration, caching, and streaming large datasets.

This project follows **RESTful API principles**, including:

- **Resource-based URLs:** Endpoints represent resources like `/users` or `/files/upload`.
- **HTTP verbs for CRUD:** `GET`, `POST`, `PUT`, `DELETE` match the action on the resource.
- **Statelessness:** Each request contains all necessary info; authentication is via JWT tokens.
- **Query parameters:** Filtering and pagination implemented via query strings.
- **Standard HTTP status codes:** `200 OK`, `201 Created`, `404 Not Found`, etc.
- **JSON responses:** All endpoints return structured JSON.
- **JWT authentication:** Protects resources in a stateless manner.

---

## ✅ Basic Endpoint Examples

| # | Endpoint | Method | Description |
|---|----------|--------|-------------|
| 1 | `/users` | GET | Return all users |
| 2 | `/users` | POST | Create a new user |
| 3 | `/users/<int:user_id>` | PUT | Update a user's information by ID |
| 4 | `/users/<int:user_id>` | DELETE | Delete a user by ID |
| 5 | `/users/search` | GET | Filter users by name |

---

## ✅ Intermediate Endpoint Examples

| # | Endpoint | Method | Description |
|---|----------|--------|-------------|
| 1 | `/users/paginate` | GET | Return users with pagination |
| 2 | `/users/<int:user_id>/upload` | POST | Upload a profile picture and save it locally |
| 3 | `/users` | POST | Accept JSON data to create a new user and validate input |
| 4 | `/login` | POST | Authenticate a user using username and password |
| 5 | `/users/<int:user_id>` | GET | Return a custom error if the user is not found (404) |

---

## ✅ Advanced Endpoint Examples

| # | Endpoint | Method | Description |
|---|----------|--------|-------------|
| 1 | `/external-data` | GET | Integrate with an external API (e.g., GitHub) and return combined user data |
| 2 | `/cached-users` | GET | Cache the response using an in-memory dictionary for faster access |
| 3 | `/protected` | GET | Restrict access using JWT authentication |
| 4 | `/files/upload` | POST | Handle file uploads and store files in cloud storage (AWS S3 / Google Cloud Storage) |
| 5 | `/stream-data` | GET | Stream large datasets using Python generators |

---

## Features Practiced

- **Flask Routing & CRUD operations**
- **Request parsing:** Form data, JSON payloads, query parameters
- **File uploads:** Local storage and cloud storage (S3)
- **JWT Authentication & Protected Routes**
- **Pagination & Filtering**
- **External API integration (GitHub example)**
- **Caching using Python dictionaries**
- **Streaming large datasets with generators**
- **Error handling and custom error messages**

---

This project is perfect for learning **RESTful API design in Flask** and demonstrates how to structure APIs for real-world applications.
