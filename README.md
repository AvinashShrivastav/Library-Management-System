# Library Management System

## Overview
The Library Management System is a multi-user application designed to manage the issuing and returning of e-books. It includes functionalities for both librarians and general users (students).

## Frameworks Used
- **Flask**: For application code
- **Jinja2 templates + Bootstrap**: For HTML generation and styling
- **SQLite**: For data storage

## Core Functionalities
### General User
- **Login/Register**: Users can create an account and log in.
- **View Sections/e-books**: Users can view all existing sections and e-books.
- **Request/Return Books**: Users can request and return e-books.
- **Feedback**: Users can give feedback for e-books.

### Librarian
- **Issue/Revoke e-books**: Librarians can issue or revoke access to e-books for users.
- **Manage Sections/e-books**: Librarians can add, edit, or remove sections and e-books.
- **Monitor Status**: Librarians can monitor the status of each e-book and the user it is issued to.

## Additional Features
- **Search Functionality**: Ability to search for sections and e-books based on various criteria.
- **Download e-books**: Users can download e-books as PDFs for a price.
- **APIs**: CRUD operations on e-books/sections and additional APIs for creating graphs for the librarian dashboard.
- **Validation**: Backend validation for all form inputs before storing/selecting from the database.

## Installation
1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the application using `python app.py`.

## Usage
1. Open the application in your local browser.
2. Register or log in as a user or librarian.
3. Use the dashboard to manage sections and e-books.

## License
This project is licensed under the MIT License.
