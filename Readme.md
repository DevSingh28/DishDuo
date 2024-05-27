# DishDuo - Recipe Sharing Platform

DishDuo is a modern and intuitive recipe sharing platform built using Flask. It offers a wide range of features to enhance the recipe-sharing experience for users.

## Features

- **User Registration and Authentication:** Users can easily register an account and securely log in to access the platform's features.
- **Recipe Management:** Users can upload, edit, and delete recipes, providing a diverse range of culinary inspirations.
- **Commenting:** Users can comment on recipes to share their cooking experiences, tips, and suggestions.
- **Like Functionality:** Users can like recipes to show appreciation and bookmark them for later reference.
- **Search and Filter:** Users can search for recipes based on keywords, ingredients, or categories, making it easy to discover new dishes.
- **Responsive Design:** The platform is designed to be responsive and mobile-friendly, ensuring a seamless experience across devices.

## Technologies Used

- **Flask:** Python-based web framework for building the application.
- **Bootstrap:** Frontend framework for designing responsive and attractive UI.
- **SQLAlchemy:** ORM for working with databases.
- **Flask-Login:** Provides user session management.
- **Flask-CKEditor:** Integration for rich text editing capabilities.
- **Flask-Gravatar:** Integration for displaying user avatars.
- **SMTP (Simple Mail Transfer Protocol):** Used for sending email notifications.
- **ItsDangerous:** Library for generating and verifying tokens for email verification and password reset.
- **Werkzeug:** Library for password hashing and verification.

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/DevSingh28/DishDuo.git
   cd DishDuo

2. Install Requirements:

   ```bash
   pip install -r requirements.txt

3. Set up environment variables:

    - coffee_key: Secret key for Flask application.
    - myemail: Email address for sending notifications.
    - gm_pass: Password for the email account.
    - DB_URI3: URI for the database (optional, defaults to SQLite).

    
## Contributing
- Contributions are welcome! If you have any suggestions, feature requests, or bug reports, please open an issue or create a pull request.

## License

This project is licensed under the Proprietary License - see the [LICENSE](License.txt) file for details.
