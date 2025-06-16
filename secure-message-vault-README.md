# Secure Message Vault API

## Short Description
The Secure Message Vault API is a robust backend solution for storing and managing highly confidential messages. It provides advanced encryption capabilities, allowing users to securely store sensitive information that can be time-locked, protected by a passphrase, and even configured to self-destruct after a single viewing. Built with Django REST Framework, this API ensures data privacy and controlled access to sensitive content.

## Features Overview

*   **Strong Encryption:** Messages are encrypted server-side using the `cryptography` library. It supports two modes:
    *   **Passphrase-based:** The encryption key is derived directly from a user-provided passphrase, ensuring that only someone with the passphrase can decrypt the content.
    *   **System-key based:** If no passphrase is provided, a unique key is generated for each message, which is then itself encrypted using a global `MASTER_KEY`. This provides an additional layer of security.
*   **Time-Locked Messages:** Users can set a future date and time before which a message cannot be unlocked, ensuring information is revealed only when intended.
*   **Passphrase Protection:** Enhance security by requiring a specific passphrase to decrypt and access a message.
*   **Self-Destructing Messages:** Messages can be configured to automatically delete themselves from the vault immediately after being viewed for the first time, ensuring ephemeral communication.
*   **User Authentication & Authorization:** Secure user registration, login, and token-based authentication (JSON Web Tokens - JWT) manage access to personal message vaults.
*   **Password Management:** Includes robust functionality for initiating and confirming password resets via email.
*   **RESTful API:** All functionalities are exposed through a clear and consistent RESTful API, making integration straightforward.

## Tech Stack

*   **Language:** Python
*   **Framework:** Django
*   **API Framework:** Django REST Framework
*   **Authentication:** `djangorestframework-simplejwt` (JWT)
*   **Encryption:** `cryptography`
*   **Environment Variables:** `python-dotenv`
*   **CORS Management:** `django-cors-headers`

## Installation Instructions

To set up and run the Secure Message Vault API locally, follow these steps:

### Prerequisites
*   Python 3.8+
*   pip (Python package installer)

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd secure-message-vault-api # Replace with your actual project directory name if different
    ```

2.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Install all required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration:**
    Create a `.env` file in the root directory of the project (where `manage.py` is located) and add the following environment variables:
    *   `MASTER_KEY`: A randomly generated base64-encoded URL-safe key for system-level encryption. This key is crucial for decrypting messages not protected by a user-defined passphrase. You can generate one using Python:
        ```python
        from cryptography.fernet import Fernet
        print(Fernet.generate_key().decode())
        ```
    *   **Email Configuration (for password reset functionality):**
        ```ini
        EMAIL_HOST=smtp.your-email-provider.com
        EMAIL_PORT=587 # Or 465 for SSL, adjust EMAIL_USE_TLS/SSL accordingly
        EMAIL_USE_TLS=True # Or EMAIL_USE_SSL=True
        EMAIL_HOST_USER=your_email@example.com
        EMAIL_HOST_PASSWORD=your_email_password
        ```

5.  **Apply Database Migrations:**
    Create the database schema and apply initial migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Create a Superuser (Optional but Recommended):**
    This allows access to the Django Admin panel for database management.
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create your admin user.

7.  **Run the Development Server:**
    Start the Django development server:
    ```bash
    python manage.py runserver
    ```
    The API will now be accessible at `http://127.0.0.1:8000/api/`.

## Usage Examples

The API endpoints are designed to be intuitive for interacting with user accounts and message vaults. All message-related and user-authenticated endpoints require a JWT access token in the `Authorization: Bearer <YOUR_ACCESS_TOKEN>` header.

### User Authentication

*   **Register a New User:**
    *   `POST /api/register/`
    *   **Payload:**
        ```json
        {
          "username": "JohnDoe",
          "email": "johndoe@example.com",
          "password": "SecurePassword123"
        }
        ```
    *   **Response (Success):**
        ```json
        {
          "message": "Registration successful"
        }
        ```

*   **Log In User:**
    *   `POST /api/login/`
    *   **Payload:**
        ```json
        {
          "email": "user@example.com",
          "password": "UserPassword123"
        }
        ```
    *   **Response (Success):**
        ```json
        {
          "access": "eyJhbGciOiJIUzI1Ni...", // Your JWT access token
          "user": {
            "name": "User Name",
            "email": "user@example.com"
          }
        }
        ```

*   **Request Password Reset:**
    *   `POST /api/password-reset/`
    *   **Payload:**
        ```json
        {
          "email": "user@example.com"
        }
        ```
    *   **Response (Success):**
        ```json
        {
          "message": "Password reset link sent"
        }
        ```
    *   *(Note: A password reset link will be sent to the user's email, containing `uid` and `token` parameters for the confirmation endpoint.)*

*   **Confirm Password Reset:**
    *   `POST /api/password-reset-confirm/<uid>/<token>/`
    *   **Payload:**
        ```json
        {
          "new_password": "NewSecurePassword123"
        }
        ```
    *   **Response (Success):**
        ```json
        {
          "message": "Password has been reset"
        }
        ```

### Message Management

*   **Create a Secure Message:**
    *   `POST /api/messages/`
    *   **Requires:** Authentication (`Authorization: Bearer <YOUR_ACCESS_TOKEN>`)
    *   **Payload:**
        ```json
        {
          "title": "Secret Project Notes",
          "content": "Meeting details for Project X: Phase 1 starts next week.",
          "passphrase": "mySuperSecretPassphrase",  // Optional: Omit for system-key encryption
          "unlock_after": "2025-12-31 09:00:00",    // Required: Must be a future date/time
          "self_destruct": true                   // Optional: Default is false
        }
        ```
    *   **Response (Success):**
        ```json
        {
            "title": "Secret Project Notes",
            "unlock_after": "2025-12-31 09:00:00",
            "self_destruct": true
        }
        ```

*   **List Your Stored Messages:**
    *   `GET /api/messages/`
    *   **Requires:** Authentication (`Authorization: Bearer <YOUR_ACCESS_TOKEN>`)
    *   **Response (Success):**
        ```json
        [
            {
                "id": 1,
                "title": "Confidential Info",
                "message_url": "http://127.0.0.1:8000/api/messages/1/unlock/",
                "created_at": "2025-05-20 15:01:10"
            },
            {
                "id": 2,
                "title": "My Backup Codes",
                "message_url": "http://127.0.0.1:8000/api/messages/2/unlock/",
                "created_at": "2025-05-21 10:30:00"
            }
        ]
        ```

*   **Unlock and Read a Message:**
    *   `POST /api/messages/{id}/unlock/`
    *   **Requires:** Authentication (`Authorization: Bearer <YOUR_ACCESS_TOKEN>`)
    *   **Payload:**
        ```json
        {
          "passphrase": "mySuperSecretPassphrase" // Required if message was created with a passphrase
        }
        ```
    *   **Response (Success):**
        ```json
        {
          "title": "Secret Project Notes",
          "content": "Meeting details for Project X: Phase 1 starts next week."
        }
        ```
    *   **Response (If time-locked and too early):**
        ```json
        {
          "detail": "Available after 2025-12-31 09:00:00"
        }
        ```
    *   **Response (If self-destructed or already viewed and self-destruct enabled):**
        ```json
        {
          "detail": "Message has been destroyed"
        }
        ```
    *   **Response (If incorrect passphrase):**
        ```json
        {
          "detail": "Decryption failed - invalid credentials"
        }
        ```

## File Structure Summary

The project follows a standard Django project structure, with dedicated applications (`messagesvault` and `users`) to separate concerns and promote modularity.

```
.
â”œâ”€â”€ smv/                     # Main Django project configuration
â”‚   â”œâ”€â”€ settings.py          # Project settings (database, installed apps, DRF config)
â”‚   â”œâ”€â”€ urls.py              # Main URL router, includes app-specific URLs
â”‚   â”œâ”€â”€ wsgi.py              # WSGI configuration for web server deployment
â”‚   â””â”€â”€ asgi.py              # ASGI configuration for async web server deployment
â”œâ”€â”€ messagesvault/           # Django app for secure message handling
â”‚   â”œâ”€â”€ models.py            # Defines the MessageVault database model
â”‚   â”œâ”€â”€ views.py             # Handles API logic for message creation, listing, and unlocking
â”‚   â”œâ”€â”€ serializers.py       # Data serialization and core encryption/decryption logic
â”‚   â”œâ”€â”€ migrations/          # Database migration files for MessageVault
â”‚   â””â”€â”€ apps.py              # App configuration for messagesvault
â”œâ”€â”€ users/                   # Django app for user authentication and management
â”‚   â”œâ”€â”€ models.py            # (Uses Django's default User model)
â”‚   â”œâ”€â”€ views.py             # Handles user registration, login, and password reset API endpoints
â”‚   â”œâ”€â”€ serializers.py       # Data serialization for user operations, including token generation
â”‚   â”œâ”€â”€ migrations/          # Database migration files for users
â”‚   â””â”€â”€ apps.py              # App configuration for users
â”œâ”€â”€ manage.py                # Django's command-line utility for administrative tasks
â”œâ”€â”€ requirements.txt         # Lists all project dependencies
â”œâ”€â”€ .env.example             # An example file for environment variables (copy to .env)
â”œâ”€â”€ .gitignore               # Specifies files and directories to be ignored by Git
â””â”€â”€ README.md                # This documentation file
```

## Important Notes

*   **Security of `MASTER_KEY`**: The `MASTER_KEY` stored in your `.env` file is critical. In a production environment, ensure this key is securely managed (e.g., via environment variables, secret management services) and never committed to version control. If this key is compromised, all messages encrypted without a user-defined passphrase could be decrypted.
*   **Development vs. Production:** The `DEBUG = True` setting in `smv/settings.py` is suitable for development. For production deployments, this should be set to `False`, and `ALLOWED_HOSTS` should be configured appropriately to specify the domains that can serve your Django project.
*   **Time Zones:** The `TIME_ZONE` setting in `smv/settings.py` is currently set to `"Africa/lagos"`. Ensure your system's timezone and this setting are correctly configured, especially for accurate behavior of time-locked messages.
*   **CORS Configuration:** `CORS_ALLOW_ALL_ORIGINS = True` is currently set for development convenience. In a production environment, this should be restricted. Configure `CORS_ALLOWED_ORIGINS` to a specific list of trusted client domains that are allowed to make requests to your API.
*   **Email Sending:** The password reset functionality relies on correctly configured SMTP settings in your `.env` file. Ensure these credentials are valid and that your email provider allows sending emails via SMTP for the password reset emails to function correctly. The password reset link generated is for a local development URL (`http://127.0.0.1:8000/...`). For production, this base URL should be configured to your public API domain.