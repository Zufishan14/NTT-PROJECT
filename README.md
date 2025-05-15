# NiceAdmin Django Project

This is a Django project that serves the NiceAdmin template.

## Setup Instructions

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start the development server:
```bash
python manage.py runserver
```

5. Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

## Available Pages

- Home: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/login/
- Register: http://127.0.0.1:8000/register/
- Profile: http://127.0.0.1:8000/profile/
- Tables: http://127.0.0.1:8000/tables/ 