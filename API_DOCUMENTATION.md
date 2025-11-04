# Quran Analysis Backend - API Documentation

## Overview

The Quran Analysis Backend provides comprehensive REST API endpoints for:
- AI-powered Quran recitation analysis with Tajweed guidance
- Complete Quran metadata (surahs, juz, verses)
- User authentication and management
- Progress tracking for reading and memorization
- Bookmark management
- Audio recitation integration

## Base URL

```
http://localhost:8081
```

## Authentication

Most endpoints require one of the following authentication methods:

### API Key (for analysis endpoints)
```
X-API-Key: your-api-key
```

### JWT Bearer Token (for user-specific endpoints)
```
Authorization: Bearer <access_token>
```

## API Endpoints

### 1. Quran Data Endpoints

#### Get All Surahs
```http
GET /api/surahs
```

**Response:**
```json
{
  "ok": true,
  "count": 114,
  "surahs": [
    {
      "id": 1,
      "name": "Al-Fatihah",
      "arabic_name": "الفاتحة",
      "ayah_count": 7,
      "juz": 1,
      "revelation_place": "Makkah"
    }
  ]
}
```

#### Get Specific Surah
```http
GET /api/surahs/{surah_id}
```

**Parameters:**
- `surah_id` (path): Surah number (1-114)

**Response:**
```json
{
  "ok": true,
  "surah": {
    "id": 1,
    "name": "Al-Fatihah",
    "arabic_name": "الفاتحة",
    "ayah_count": 7,
    "juz": 1,
    "revelation_place": "Makkah"
  }
}
```

#### Get All Juz
```http
GET /api/juz
```

**Response:**
```json
{
  "ok": true,
  "count": 30,
  "juz": [
    {
      "id": 1,
      "start_surah": 1,
      "start_ayah": 1,
      "end_surah": 2,
      "end_ayah": 141
    }
  ]
}
```

#### Get Specific Juz
```http
GET /api/juz/{juz_id}
```

**Parameters:**
- `juz_id` (path): Juz number (1-30)

**Response:**
```json
{
  "ok": true,
  "juz": {
    "id": 1,
    "start_surah": 1,
    "start_ayah": 1,
    "end_surah": 2,
    "end_ayah": 141
  },
  "surahs": [...]
}
```

### 2. Reciter & Audio Endpoints

#### Get All Reciters
```http
GET /api/reciters
```

**Response:**
```json
{
  "ok": true,
  "count": 5,
  "reciters": [
    {
      "id": 1,
      "name": "Abdul Basit Abdul Samad",
      "name_ar": "عبد الباسط عبد الصمد",
      "style": "Mujawwad",
      "quality": "high"
    }
  ]
}
```

#### Get Specific Reciter
```http
GET /api/reciters/{reciter_id}
```

**Parameters:**
- `reciter_id` (path): Reciter ID

**Response:**
```json
{
  "ok": true,
  "reciter": {
    "id": 1,
    "name": "Abdul Basit Abdul Samad",
    "name_ar": "عبد الباسط عبد الصمد",
    "style": "Mujawwad",
    "quality": "high"
  }
}
```

#### Get Audio URL
```http
GET /api/audio/{reciter_id}/surah/{surah_id}/ayah/{ayah_number}
```

**Parameters:**
- `reciter_id` (path): Reciter ID
- `surah_id` (path): Surah number (1-114)
- `ayah_number` (path): Ayah number

**Response:**
```json
{
  "ok": true,
  "url": "https://cdn.islamic.network/quran/audio/128/ar.alafasy/1001.mp3",
  "reciter": "Mishary Rashid Alafasy",
  "surah": 1,
  "ayah": 1
}
```

### 3. Authentication Endpoints

#### Register New User
```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "username": "newuser123",
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Login
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "username": "newuser123",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Refresh Token
```http
POST /api/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 4. User Profile Endpoints

#### Get User Profile
```http
GET /api/users/{user_id}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "username": "newuser123",
  "email": "user@example.com",
  "created_at": "2024-11-04T18:00:00",
  "last_login": "2024-11-04T19:00:00",
  "preferences": {
    "font_size": 16,
    "auto_scroll": true,
    "language": "en",
    "theme": "light",
    "reciter_id": 7
  }
}
```

#### Update User Preferences
```http
PUT /api/users/{user_id}/preferences
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "font_size": 18,
  "theme": "dark",
  "language": "ar"
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Preferences updated successfully",
  "preferences": {
    "font_size": 18,
    "auto_scroll": true,
    "language": "ar",
    "theme": "dark",
    "reciter_id": 7
  }
}
```

### 5. Progress Tracking Endpoints

#### Save Progress
```http
POST /api/progress?surah_id=1&verse_number=5&completed=true&memorized=false
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `surah_id`: Surah number (1-114)
- `verse_number`: Verse number
- `completed`: Mark as completed (boolean)
- `memorized`: Mark as memorized (boolean)

**Response:**
```json
{
  "ok": true,
  "message": "Progress saved successfully",
  "surah_id": 1,
  "verse_number": 5
}
```

#### Get User Progress
```http
GET /api/progress/{user_id}?surah_id=1
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `surah_id` (optional): Filter by surah

**Response:**
```json
{
  "ok": true,
  "count": 1,
  "progress": [
    {
      "surah_id": 1,
      "completed_verses": [1, 2, 3, 4, 5],
      "memorized_verses": [1, 2],
      "last_read_verse": 5,
      "last_read_time": "2024-11-04T19:00:00"
    }
  ]
}
```

### 6. Bookmark Endpoints

#### Create Bookmark
```http
POST /api/bookmarks?surah_id=2&verse_index=255&note=Ayat al-Kursi
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `surah_id`: Surah number (1-114)
- `verse_index`: Verse number
- `note` (optional): Note for the bookmark

**Response:**
```json
{
  "ok": true,
  "message": "Bookmark created successfully",
  "bookmark": {
    "id": 1,
    "surah_id": 2,
    "verse_index": 255,
    "note": "Ayat al-Kursi",
    "created_at": "2024-11-04T19:00:00"
  }
}
```

#### Get User Bookmarks
```http
GET /api/bookmarks/{user_id}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "ok": true,
  "count": 1,
  "bookmarks": [
    {
      "id": 1,
      "surah_id": 2,
      "verse_index": 255,
      "note": "Ayat al-Kursi",
      "created_at": "2024-11-04T19:00:00"
    }
  ]
}
```

#### Delete Bookmark
```http
DELETE /api/bookmarks/{bookmark_id}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "ok": true,
  "message": "Bookmark deleted successfully"
}
```

### 7. Analysis Endpoints (Existing)

#### Analyze Recitation
```http
POST /analyze
```

**Headers:**
```
X-API-Key: your-api-key
```

**Request (multipart/form-data):**
- `audio`: Audio file (m4a, wav, mp3, aac)
- `expected_arabic`: Expected Arabic text

**Response:**
```json
{
  "ok": true,
  "wer": 0.05,
  "cer": 0.02,
  "transcript": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
  "summary": "Excellent recitation! Keep up the good work!",
  "rule_hints": [],
  "alignment_hints": [],
  "tajweed_analysis": {},
  "score": 95,
  "needs_repeat": false
}
```

#### Get Tajweed Guide
```http
POST /tajweed-guide
```

**Headers:**
```
X-API-Key: your-api-key
```

**Request (form data):**
- `arabic_text`: Arabic text for analysis

**Response:**
```json
{
  "ok": true,
  "text": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
  "rules": [...],
  "difficulty_level": "beginner",
  "estimated_duration": 30
}
```

### 8. Health & Monitoring

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "quran-learning-api",
  "version": "2.0.0",
  "timestamp": "2024-11-04T19:00:00",
  "checks": {
    "whisper": {
      "status": "ok",
      "model": "medium",
      "device": "cpu"
    },
    "gemini": {
      "status": "configured",
      "model": "gemini-1.5-flash"
    },
    "cache": {
      "status": "enabled",
      "items": 0,
      "max_size": 100,
      "ttl": 3600
    },
    "rate_limiter": {
      "status": "enabled",
      "general_limit": "10/minute",
      "analyze_limit": "5/minute"
    }
  }
}
```

## Error Responses

All error responses follow this format:

```json
{
  "ok": false,
  "error": "Error message",
  "detail": "Detailed error information (optional)",
  "timestamp": "2024-11-04T19:00:00"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File size exceeds limit
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

- General endpoints: 10 requests per minute
- Analysis endpoint: 5 requests per minute
- Authenticated endpoints: Per-user rate limiting

## Interactive Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8081/docs`
- ReDoc: `http://localhost:8081/redoc`

## Examples

### Python Example
```python
import requests

# Register a new user
response = requests.post('http://localhost:8081/api/auth/register', json={
    'username': 'john_doe',
    'email': 'john@example.com',
    'password': 'SecurePass123!'
})
tokens = response.json()

# Get all surahs
headers = {'Authorization': f"Bearer {tokens['access_token']}"}
response = requests.get('http://localhost:8081/api/surahs')
surahs = response.json()

print(f"Total surahs: {surahs['count']}")
```

### JavaScript Example
```javascript
// Login
const loginResponse = await fetch('http://localhost:8081/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'SecurePass123!'
  })
});
const { access_token } = await loginResponse.json();

// Get user progress
const progressResponse = await fetch('http://localhost:8081/api/progress/1', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const progress = await progressResponse.json();
console.log('User progress:', progress);
```

## Database Setup

The database is automatically initialized on first run. The SQLite database file `quran.db` will be created in the project root.

### Database Schema

**Users Table:**
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- created_at
- last_login
- preferences (JSON)

**Progress Table:**
- id (Primary Key)
- user_id (Foreign Key → users)
- surah_id
- completed_verses (JSON Array)
- memorized_verses (JSON Array)
- last_read_verse
- last_read_time

**Bookmarks Table:**
- id (Primary Key)
- user_id (Foreign Key → users)
- surah_id
- verse_index
- created_at
- note

## Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=sqlite:///./quran.db

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# API Security
API_KEY=your-api-key
REQUIRE_API_KEY=true

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Whisper Model
WHISPER_MODEL=medium
WHISPER_DEVICE=cpu
```

## Support

For issues and questions, please visit:
https://github.com/OmarBoshnak/quran-analysis-backend
