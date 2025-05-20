# Secure Message Vault API

A backend API to store and retrieve encrypted messages. Messages can be time-locked, passphrase-locked, and optionally self-destruct after being read.



## Key Features

- Message encryption & decryption (server-side)
- Set unlock passphrase 
- Set unlock time/date (time-locked messages)
- Option to self-destruct after first view
- API to retrieve and unlock a message securely



## Tech Stack

- Django REST Framework
- Python cryptography for encryption
- Token Authentication
- SQLite





## Authentication

All endpoints are protected with token-based authentication.

**Include in headers:**
```
Authorization: Token YOUR_TOKEN_HERE
```



## API Endpoints

### POST `/api/register/`

**Register a new user.**

**Request:**

```json
{
  "username": "JohnDoe",
  "email": "johndoe@example.com",
  "password": "SecurePassword123"
}
```

**Response:**

```json
{
  "message": "User registered successfully"
}
```


### POST `/api/login/`

**Authenticate a user and return a token. Admin must be verified.**

**Request:**

```json
{
  "email": "user123@gmail.com",
  "password": "UserPassword123"
}
```

**Response:**

```json
{
  "access": "dhaodhadnas",
  "user": {
    "name": "Admin Mike",
    "email": "michael.n.ezeana@gmail.com",
  }
}
```


###  POST `/api/password-reset/`

**Request a password reset link.**

**Request:**

```json
{
  "email": "user@example.com"
}
```

**Response:**

```json
{
  "message": "Password reset link sent"
}
```



###  POST `/api/password-reset-confirm/<uid>/<token>/`

**Confirm password reset using UID and token.**

**Request:**

```json
{
  "new_password": "NewSecurePassword123"
}
```

**Response:**

```json
{
  "message": "Password has been reset"
}
```


###  POST `/messages/`
Create a secure message.

**Request:**
```json
{
  "title": "Backup Codes",
  "content": "Here are your backup codes: 2233, 4467, 8888",
  "passphrase": "vault123",  // optional
  "unlock_after": "2025-05-20 15:10:00",  // optional
  "self_destruct": false
}
```

**Response:**
```json
{
    "title": "first",
    "unlock_after": "2025-05-20 15:10:00",
    "self_destruct": false
}
```



###  GET `/messages/`
List your stored messages.
**Response:**
```json
[
    {
        "id": 1,
        "title": "first",
        "message_url": "http://127.0.0.1:8000/api/messages/1/unlock/",
        "created_at": "2025-05-20 15:01:10"
    }
]
```


###  GET `/messages/{id}/unlock/`
Unlock and read the encrypted message.

**Request (passphrase-protected):**
```json
{
  "passphrase": "vault123"
}
```

**Response (if successful):**
```json
{
  "title": "Backup Codes",
  "content": "Here are your backup codes: 2233, 4467, 8888"
}
```

**If too early:**
```json
{
  "detail": "This message will be unlockable at 2025-04-22 15:00:00"
}
```

**If wrong passphrase:**
```json
{
  "detail": "Incorrect passphrase"
}
```

**If already self-destructed:**
```json
{
  "detail": "This message has already been viewed and destroyed"
}
```



###  DELETE `/messages/{id}/`
Manually delete your message (permanent).



## Core Logic

- **Encryption:** Message content is encrypted before saving using symmetric encryption (Fernet).
- **Decryption:** Happens only after correct time + optional passphrase match.
- **Passphrase:** Stored as a hashed string (e.g., with PBKDF2).
- **Self-destruct:** Once message is read, it's deleted or flagged.


