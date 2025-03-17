# ...existing code...

INSTALLED_APPS = [
    # ...existing code...
    'corsheaders',
    # ...existing code...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # This must be placed at the top, before any middleware that can generate responses
    # ...existing code...
]

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # For development only; restrict in production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',
    'pragma',
    # Change to uppercase 'Expires' to match your fetch request
    'Expires',
]

# ...existing code...