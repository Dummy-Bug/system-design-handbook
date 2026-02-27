[[02 Design.pdf]]

### 1. POST /api/v1/shortUrl

**Request**
```json
{
  "originalUrl": "https://example.com"
}
```

**Response**
```json
{
  "success": true,
  "message": "Created",
  "data": {
    "id": 123,
    "originalUrl": "https://example.com",
    "shortCode": "abc123"
  }
}
```

# 2. GET /{shortCode}

**Response**
```http
302 Found
Location: https://example.com
```

