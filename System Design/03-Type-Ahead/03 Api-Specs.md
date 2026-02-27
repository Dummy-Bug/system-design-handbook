
## Base Path

```http
/api/v1
```

---

# 1. Fetch Autocomplete Suggestions

Returns ranked suggestions for a given prefix.

---

## Endpoint

```http
GET /typeahead?partialSearchQuery=paris
```

---

## Query Parameters

|Name|Type|Required|Description|
|---|---|---|---|
|partialSearchQuery|string|Yes|User typed prefix|

---

## Example HTTP Request

```http
GET /api/v1/typeahead?partialSearchQuery=paris HTTP/1.1
Host: api.yourdomain.com
Accept: application/json
```

## Success Response

### HTTP Status

```http
200 OK
```

### Response Body

```json
{
  "success": true,
  "message": "Fetched results for prefix: paris",
  "data": [
    "paris weather",
    "paris hotels",
    "paris city cost of living"
  ],
  "error": null
}
```

## Error Response Example

### HTTP Status

```http
400 Bad Request
```

### Response Body

```json
{
  "success": false,
  "message": "Invalid request",
  "data": null,
  "error": {
    "code": "INVALID_PARAMETER",
    "details": "partialSearchQuery is required"
  }
}
```

---

# 2. Increment Search Popularity

Used to update popularity signal after user submits a query.

This endpoint should be asynchronous in production.

---

## Endpoint

```http
PUT /typeahead/increment
```

## Example HTTP Request

```http
PUT /api/v1/typeahead/increment HTTP/1.1
Host: api.yourdomain.com
Content-Type: application/json
```

## Request Body

```json
{
  "query": "paris city cost of living"
}
```

## Field Schema

|Field|Type|Required|Description|
|---|---|---|---|
|query|string|Yes|Full search query|


## Success Response

### HTTP Status

```http
200 OK
```

### Response Body

```json
{
  "success": true,
  "message": "Query frequency incremented successfully",
  "data": null,
  "error": null
}
```

## Error Response Example

### HTTP Status

```http
500 Internal Server Error
```

### Response Body

```json
{
  "success": false,
  "message": "Failed to update query frequency",
  "data": null,
  "error": {
    "code": "WRITE_TIMEOUT",
    "details": "Redis operation timed out"
  }
}
```

