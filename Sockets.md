## Available Events

### 1. Initialize User Session
**Event:** `init_user`

Initialize user session with business information to start generating posts.

**Request Data:**
```javascript
{
  "business_id": "123",
  "access_token": "your_jwt_token"
}
```



**Success Response:** `ack` event
```javascript
{
  "msg": "User info received"
}
```

**Error Response:** `error` event
```javascript
{
  "msg": "Init failed: [error_details]"
}
```

**Notes:**
- Must be called before any other operations
- Stores user business information in session
- Required for authentication with backend services

---

### 2. Generate Post
**Event:** `generate_request`

Generate a new social media post based on specified preferences.

**Request Data:**
```javascript
{
  "message": "write me a post about social media",
  "approximate_words": 100,
  "hashtags": true,
  "emojis": true,
  "required_words": ["innovation", "technology"],
  "forbidden_words": ["boring", "outdated"]
}
```

**Parameters:**
- `message` (string, **required**): The content prompt for post generation
- `approximate_words` (number): Target word count for the post
- `hashtags` (boolean): Whether to include hashtags
- `emojis` (boolean): Whether to include emojis
- `required_words` (array of strings): Words that must appear in the post
- `forbidden_words` (array of strings): Words to avoid in the post



**Response Flow:**
1. `bot_typing` event with "....." - indicates processing
2. `bot_message` event with generated post JSON

**Success Response:** `bot_message` event
```javascript
{
  "title": "Generated Post Title",
  "description": "Generated post content..."
}
```

**Error Response:** `error` event
```javascript
{
  "msg": "No message received" // if message field is empty
}
// or
{
  "msg": "Generate failed: [error_details]"
}
```

---

### 3. Toggle Hashtags
**Event:** `toggle_hashtags`

Add or remove hashtags from the last generated post.

**Request Data:**
```javascript
{} // Empty object
```


**Response Flow:**
1. `bot_typing` event with "....." - indicates processing
2. `bot_message` event with updated post

**Success Response:** `bot_message` event
```javascript
{
  "title": "Same Title",
  "description": "Updated content with/without hashtags..."
}
```

**Error Response:** `error` event
```javascript
{
  "msg": "No post generated yet"
}
```

**Notes:**
- Requires a post to be generated first using `generate_request`
- Toggles the current hashtag state (adds if missing, removes if present)

---

### 4. Toggle Emojis
**Event:** `toggle_emojis`

Add or remove emojis from the last generated post.

**Request Data:**
```javascript
{} // Empty object
```


**Response Flow:**
1. `bot_typing` event with "....." - indicates processing
2. `bot_message` event with updated post

**Success Response:** `bot_message` event
```javascript
{
  "title": "Same Title",
  "description": "Updated content with/without emojis..."
}
```

**Error Response:** `error` event
```javascript
{
  "msg": "No post generated yet"
}
```

**Notes:**
- Requires a post to be generated first using `generate_request`
- Toggles the current emoji state (adds if missing, removes if present)

---

### 5. Publish Post
**Event:** `publish_post`

Send the generated post to backend for publishing to social media platforms.

**Request Data:**
```javascript
{
  "access_token": "your_jwt_token"
}
```


**Success Response:** `ack` event
```javascript
{
  "msg": "Post sent to backend for publishing"
}
```

**Error Response:** `error` event
```javascript
{
  "msg": "No post to publish" // if no post was generated
}
// or
{
  "msg": "Publish failed: [error_details]"
}
```

**Notes:**
- Requires a post to be generated first
- Sends post along with all generation preferences to backend
- Does not directly publish - sends to backend for processing


## Required Sequence

1. **Always start with:** `init_user`
2. **Then generate:** `generate_request`
3. **Optionally modify:** `toggle_hashtags`, `toggle_emojis`
4. **Finally publish:** `publish_post`

Each step must complete successfully before proceeding to the next.
