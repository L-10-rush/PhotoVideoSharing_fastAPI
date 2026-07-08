# 📸 Simple Social — Photo & Video Sharing App

Welcome to **Simple Social**, a full-stack photo and video sharing application built with a FastAPI backend and a Streamlit frontend. It supports secure JWT-based authentication, media uploads to ImageKit.io with on-the-fly transformations (including caption overlays), and a live feed where users can share and delete their own posts. 🚀

This is Live and Deployed:- https://photovideosharing.streamlit.app/
pls GO through it and Give feed back

## ✨ Features

* **User Authentication** — Secure register, login, and logout via [fastapi-users](https://fastapi-users.github.io/fastapi-users/) with JWT bearer tokens.
* **Media Upload** — Share images or videos with an optional caption; files are uploaded directly to ImageKit.io.
* **Uniform Feed Display** — Images and videos are resized/padded on the fly using ImageKit URL transformations so the feed stays visually consistent.
* **Caption Overlays** — Captions are rendered as text overlays directly on images using base64-encoded ImageKit transformation strings.
* **Ownership & Permissions** — Users can only delete their own posts; ownership is checked server-side on every request.
* **Async End-to-End** — Fully async backend using SQLAlchemy's async engine with `aiosqlite`, so no request blocks the event loop.
* **Auto-Reloading Dev Server** — Uvicorn's reloader is scoped to the `app/` source directory only, so database writes never trigger a false restart.

## 🛠️ Technologies Used

| Category     | Technology                                                                                                                             | Description                                                     |
| :----------- | :-------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------- |
| **Backend**  | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)                                | High-performance async Python web framework                     |
|              | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-CC2927?style=for-the-badge&logo=sqlalchemy&logoColor=white)                       | Async ORM for database models and queries                       |
|              | ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)                                   | Lightweight async database via `aiosqlite`                      |
|              | ![fastapi-users](https://img.shields.io/badge/fastapi--users-009688?style=for-the-badge&logo=fastapi&logoColor=white)                   | Drop-in JWT authentication, registration, and user management   |
|              | ![PyJWT](https://img.shields.io/badge/PyJWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)                              | JSON Web Token signing and verification                         |
|              | ![Uvicorn](https://img.shields.io/badge/Uvicorn-2A2A2A?style=for-the-badge&logo=gunicorn&logoColor=white)                               | ASGI server with hot-reload for local development                |
|              | ![ImageKit](https://img.shields.io/badge/ImageKit.io-00A3E0?style=for-the-badge&logo=imagekit&logoColor=white)                          | Cloud media storage, delivery, and on-the-fly transformations   |
| **Frontend** | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)                          | Rapid Python UI framework for the web client                    |
|              | ![Requests](https://img.shields.io/badge/Requests-000000?style=for-the-badge&logo=python&logoColor=white)                               | HTTP client for communicating with the FastAPI backend          |

## ⚙️ Getting Started

Follow these steps to set up and run Simple Social on your local machine.

### Prerequisites

* Python 3.12+
* An [ImageKit.io](https://imagekit.io/) account (free tier works fine)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/L-10-rush/PhotoVideoSharing_fastAPI.git
   cd PhotoVideoSharing_fastAPI
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn[standard] sqlalchemy aiosqlite \
               fastapi-users[sqlalchemy] python-dotenv imagekitio \
               streamlit requests python-multipart
   ```

### Environment Variables

Create a `.env` file in the project root with the following variables:

```dotenv
SECRET=a_long_random_secret_string_at_least_32_bytes
IMAGEKIT_PRIVATE_KEY=your_imagekit_private_key
IMAGEKIT_URL=https://ik.imagekit.io/your_imagekit_id
```

* `SECRET` — Signing secret for JWT access tokens, password reset tokens, and email verification tokens. Generate a secure value with:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
* `IMAGEKIT_PRIVATE_KEY` — Your ImageKit.io private API key, used server-side for authenticated uploads.
* `IMAGEKIT_URL` — Your ImageKit URL endpoint, used to build public delivery and transformation URLs.

### 🚀 Usage

1. **Start the Backend** (from the project root):
   ```bash
   python main.py
   ```
   This launches Uvicorn on `http://0.0.0.0:8000` with hot-reload scoped to the `app/` directory.

2. **Start the Frontend** (in a second terminal):
   ```bash
   streamlit run frontend.py
   ```
   This opens the Streamlit client, typically at `http://localhost:8501`.

3. **Sign Up / Log In**:
   * On first use, enter an email and password and click **Sign Up**.
   * Once registered, click **Login** with the same credentials.

4. **Share a Post**:
   * Navigate to **📸 Upload** in the sidebar.
   * Choose an image or video, optionally add a caption, and click **Share**.

5. **Browse the Feed**:
   * Navigate to **🏠 Feed** to see all posts in reverse chronological order.
   * Posts you own show a 🗑️ delete button.

## Backend API

### Base URL
`http://localhost:8000`

### Endpoints

#### POST /auth/register
**Overview**: Registers a new user account.
**Request**:
```json
{
  "email": "jane.doe@example.com",
  "password": "StrongPassword123"
}
```
**Response** (`201 Created`):
```json
{
  "id": "a94ca282-ee11-4d3d-b5c7-810d497c95bd",
  "email": "jane.doe@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```
**Errors**:
- `400 Bad Request`: `"REGISTER_USER_ALREADY_EXISTS"`, weak password errors

#### POST /auth/jwt/login
**Overview**: Authenticates a user and issues a JWT access token. Expects `application/x-www-form-urlencoded` body (`username`, `password`).
**Response** (`200 OK`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
**Errors**:
- `400 Bad Request`: `"LOGIN_BAD_CREDENTIALS"`

#### GET /users/me
**Overview**: Returns the profile of the currently authenticated user. Requires `Authorization: Bearer <token>`.
**Response** (`200 OK`):
```json
{
  "id": "a94ca282-ee11-4d3d-b5c7-810d497c95bd",
  "email": "jane.doe@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```
**Errors**:
- `401 Unauthorized`

#### POST /upload
**Overview**: Uploads a media file to ImageKit.io and creates a new post. Requires authentication. Multipart form data (`file`, `caption`).
**Response** (`200 OK`):
```json
{
  "id": "9749561c-5e91-4e22-8316-7c4f026a2ae1",
  "user_id": "a94ca282-ee11-4d3d-b5c7-810d497c95bd",
  "caption": "Sunset over the hills",
  "url": "https://ik.imagekit.io/your_id/sunset_abc123.jpg",
  "file_type": "image",
  "file_name": "sunset_abc123.jpg",
  "created_at": "2026-07-08T10:02:00.000Z"
}
```
**Errors**:
- `500 Internal Server Error`: ImageKit upload failure or database error

#### GET /feed
**Overview**: Retrieves all posts, most recent first, with owner email attached. Requires authentication.
**Response** (`200 OK`):
```json
{
  "posts": [
    {
      "id": "9749561c-5e91-4e22-8316-7c4f026a2ae1",
      "user_id": "a94ca282-ee11-4d3d-b5c7-810d497c95bd",
      "caption": "Sunset over the hills",
      "url": "https://ik.imagekit.io/your_id/sunset_abc123.jpg",
      "file_type": "image",
      "file_name": "sunset_abc123.jpg",
      "created_at": "2026-07-08T10:02:00.000Z",
      "is_owner": true,
      "email": "jane.doe@example.com"
    }
  ]
}
```

#### DELETE /posts/{post_id}
**Overview**: Deletes a post. Only the post owner may delete it. Requires authentication.
**Response** (`200 OK`):
```json
{
  "success": true,
  "message": "Post deleted successfully"
}
```
**Errors**:
- `403 Forbidden`: `"U dont have permission to delete this post"`
- `404 Not Found`: `"Post not found"`

## 🗂️ Project Structure

```
PhotoVideoSharing_fastAPI/
├── app/
│   ├── app.py        # FastAPI app, routes: /upload, /feed, /posts/{id}
│   ├── db.py          # SQLAlchemy models (User, Post) and async session setup
│   ├── users.py       # fastapi-users JWT auth backend and UserManager
│   ├── images.py      # ImageKit.io client initialization
│   └── schemas.py     # Pydantic request/response schemas
├── frontend.py         # Streamlit client (login, upload, feed pages)
├── main.py             # Uvicorn entrypoint
├── .env                # Environment variables (not committed)
└── test.db             # Local SQLite database (dev only)
```

## 🩹 Known Notes for Contributors

* `Post.id` and `Post.user_id` use fastapi-users' `GUID` type (`fastapi_users_db_sqlalchemy.generics.GUID`) rather than `sqlalchemy.dialects.postgresql.UUID`, so that UUID storage format stays consistent with the `user` table on SQLite.
* `uvicorn`'s `reload_excludes` is configured to ignore `*.db` files, preventing the dev server from restarting on every database write.
* `/feed` eager-loads the post owner with `selectinload(Post.user)` to avoid `MissingGreenlet` errors from lazy-loading relationships inside an `AsyncSession`.

## ✒️ Author Info

* **Name:** Aniket Mondal (K1ngM0nk)
* **GitHub:** [@L-10-rush](https://github.com/L-10-rush)

## 🏅 Badges

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-CC2927?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![ImageKit](https://img.shields.io/badge/ImageKit.io-00A3E0?style=flat&logo=imagekit&logoColor=white)](https://imagekit.io/)
[![Project Status](https://img.shields.io/badge/Status-In%20Development-yellow)](https://github.com/L-10-rush/PhotoVideoSharing_fastAPI)