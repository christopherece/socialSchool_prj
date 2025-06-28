# School Social Media Platform

A Django-based social media platform designed specifically for schools, allowing students, teachers, and administrators to connect and share content in a secure environment.

## Features

- User authentication with roles (Student, Teacher, Admin)
- Post creation with text, images, videos, and files
- Instagram-like feed layout
- Media handling with Lightbox support
- Like and comment functionality
- Moderation tools for administrators

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/
