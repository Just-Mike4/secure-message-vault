# Secure Message Vault API

## Project Title
**Secure Message Vault API**

## Short Description
The Secure Message Vault API is a robust backend solution for storing and managing highly confidential messages. It provides advanced encryption capabilities, allowing users to securely store sensitive information that can be time-locked, protected by a passphrase, and even configured to self-destruct after a single viewing. Built with Django REST Framework, this API ensures data privacy and controlled access.

## Features Overview

*   **Strong Encryption:** Messages are encrypted server-side using the `cryptography` library, supporting both a system-wide master key and user-defined passphrases for decryption.
*   **Time-Locked Messages:** Set a future date and time before which a message cannot be unlocked, ensuring information is revealed only when intended.
*   **Passphrase Protection:** Enhance security by requiring a specific passphrase to decrypt and access a message.
*   **Self-Destructing Messages:** Messages can be configured to automatically delete themselves from the vault immediately after being viewed for the first time.
*   **User Authentication & Authorization:** Secure user registration, login, and token-based authentication (JWT) manage access to personal message vaults.
*   **Password Management:** Includes functionality for initiating and confirming password resets via email.
*   **RESTful API:** All functionalities are exposed through a clear and consistent RESTful API.

## Installation Instructions

To set up and run the Secure Message Vault API locally, follow these steps:

### Prerequisites
*   Python 3.8+
*   pip (Python package installer)

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd smv-project-directory # Replace with your actual directory name
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
    *   `MASTER_KEY`: A randomly generated base64-encoded URL-safe key for system-level encryption. You can generate one using Python:
        ```python
        from cryptography.fernet import Fernet
        print(Fernet.generate_key().decode())
        ```
    *   **Email Configuration (for password reset):**
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
    *   Payload: `username`, `email`, `password`
    *   Response: Success message or validation errors.

*   **Log In User:**
    *   `POST /api/login/`
    *   Payload: `email`, `password`
    *   Response: JWT `access` token and basic user details.

*   **Request Password Reset:**
    *   `POST /api/password-reset/`
    *   Payload: `email`
    *   Response: Confirmation message indicating a reset link has been sent to the provided email.

*   **Confirm Password Reset:**
    *   `POST /api/password-reset-confirm/<uid>/<token>/`
    *   Payload: `new_password`
    *   Response: Confirmation message that password has been reset.

### Message Management

*   **Create a Secure Message:**
    *   `POST /api/messages/`
    *   Requires authentication.
    *   Payload:
        *   `title`: (string) Title of the message.
        *   `content`: (string) The secret message content.
        *   `passphrase`: (string, optional) A passphrase for decryption. If not provided, a system-generated key will be used, encrypted by the `MASTER_KEY`.
        *   `unlock_after`: (datetime string, required) Format: `YYYY-MM-DD HH:MM:SS`. Message cannot be unlocked before this time. Must be in the future.
        *   `self_destruct`: (boolean) If `true`, the message will be deleted after its first successful unlock.
    *   Response: Details of the created message (title, unlock time, self-destruct status).

*   **List Your Stored Messages:**
    *   `GET /api/messages/`
    *   Requires authentication.
    *   Response: A list of messages associated with the authenticated user, including ID, title, a URL for unlocking, and creation timestamp.

*   **Unlock and Read a Message:**
    *   `POST /api/messages/{id}/unlock/`
    *   Requires authentication.
    *   Payload:
        *   `passphrase`: (string, optional) Required if the message was created with a passphrase.
    *   Response:
        *   On success: `title` and `content` of the decrypted message.
        *   If time-locked and too early: "Available after..." message.
        *   If self-destructed or already viewed (and self-destruct enabled): "Message has been destroyed".
        *   If incorrect passphrase: "Decryption failed - invalid credentials".

## File Structure Summary

The project follows a standard Django project structure, with applications (`messagesvault` and `users`) separating concerns.

```
.
âââ smv/                     # Main Django project configuration
â   âââ settings.py          # Project settings (database, installed apps, DRF config)
â   âââ urls.py              # Main URL router
â   âââ wsgi.py              # WSGI configuration
â   âââ asgi.py              # ASGI configuration
âââ messagesvault/           # Django app for secure message handling
â   âââ models.py            # Defines the MessageVault model
â   âââ views.py             # Handles API logic for message creation, listing, and unlocking
â   âââ serializers.py       # Data serialization and decryption/encryption logic
â   âââ migrations/          # Database migration files
â   âââ apps.py              # App configuration
âââ users/                   # Django app for user authentication and management
â   âââ models.py            # (Could contain custom user model, currently default)
â   âââ views.py             # Handles user registration, login, password reset
â   âââ serializers.py       # Data serialization for user operations
â   âââ migrations/          # Database migration files
â   âââ apps.py              # App configuration
âââ manage.py                # Django's command-line utility
âââ requirements.txt         # Project dependencies
âââ .env.example             # Example environment variables file (for .env)
âââ .gitignore               # Specifies intentionally untracked files to ignore
âââ readme.md                # This README file
```

## Important Notes

*   **Security of `MASTER_KEY`**: The `MASTER_KEY` stored in your `.env` file is critical. In a production environment, ensure this key is securely managed (e.g., via environment variables, secret management services) and never committed to version control. If this key is compromised, all messages encrypted without a user-defined passphrase could be decrypted.
*   **Development vs. Production:** The `DEBUG = True` setting in `smv/settings.py` is suitable for development. For production deployments, this should be set to `False`, and `ALLOWED_HOSTS` should be configured appropriately.
*   **Time Zones:** Ensure your system's timezone and the `TIME_ZONE` setting in `smv/settings.py` are correctly configured, especially for time-locked messages.
*   **CORS Configuration:** `CORS_ALLOW_ALL_ORIGINS = True` is set for development convenience. In production, configure `CORS_ALLOWED_ORIGINS` to a specific list of trusted domains.
*   **Email Sending:** The password reset functionality relies on correctly configured SMTP settings in your `.env` file. Ensure these credentials are valid and that your email provider allows sending emails via SMTP.