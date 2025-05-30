# AKONTABU - Small Business Finance Tracker

AKONTABU is a web application designed to help small traders track their finances efficiently. This repository contains the authentication system with both traditional email/password and Google authentication support.

## Features

- User registration with email and password
- Google authentication integration
- Secure password requirements
- SQLite database for data storage
- Responsive design
- Modern UI with form validation

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- A Firebase project (for Google authentication)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd akontabu
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up Firebase:
   - Create a new project in the [Firebase Console](https://console.firebase.google.com)
   - Download your Firebase Admin SDK service account key
   - Save it as `firebase-credentials.json` in the project root
   - Update the Firebase configuration in `static/js/signup.js` and `static/js/login.js`

5. Initialize the database:
```bash
python app.py
```

## Running the Application

1. Make sure your virtual environment is activated
2. Run the Flask application:
```bash
python app.py
```
3. Open your browser and navigate to `http://localhost:5000`

## Password Requirements

The application enforces the following password requirements:
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character
- Minimum length of 8 characters

## Project Structure

```
akontabu/
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── signup.js
│   │   └── login.js
│   └── images/
├── templates/
│   ├── signup.html
│   └── login.html
├── app.py
├── requirements.txt
└── README.md
```

## Security Considerations

- Passwords are hashed using Werkzeug's security functions
- Firebase authentication tokens are verified server-side
- CSRF protection is enabled
- SQLAlchemy is used for database operations to prevent SQL injection
- Input validation is performed on both client and server side

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 