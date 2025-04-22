# Mini Library Management System

## Default Credentials

The following default credentials are used for initial setup:

-   **Admin:**
    -   Username: admin
    -   Email: admin@library.com
    -   Password: admin123

-   **Librarian:**
    -   Username: librarian
    -   Email: librarian@library.com
    -   Password: librarian123

-   **User:**
    -   Username: user
    -   Email: user@library.com
    -   Password: user123

-   **New User:**
    -   Username: charbeltoumieh
    -   Email: charbeltoumieh1@gmail.com
    -   Password: Charbel

**Note:** It is highly recommended to change these default credentials immediately after the initial setup for security reasons.

## Instructions

1.  Install the required packages:

    ```
    pip install -r requirements.txt
    ```

2.  Initialize the database:

    ```
    python init_db.py
    ```

3.  Run the application:

    ```
    python app.py
    ```

## Additional Information

This application uses Flask for the backend and Werkzeug for password hashing. The database is stored in `app/library.db`.

## Roles and Permissions

-   **Admin:**
    -   Can manage users (add, remove).
    -   Has all the permissions of a librarian.

-   **Librarian:**
    -   Can add, edit, and delete books.
    -   Can export book data to a CSV file.

-   **User:**
    -   Can browse the list of books.
    -   Can check out and return books.
    -   Can change their own password.

## Functionalities

-   **Authentication:**
    -   Users can log in using email and password.
    -   Users can change their password.

-   **Book Management:**
    -   Librarians can add new books to the system.
    -   Librarians can edit existing book information.
    -   Librarians can delete books from the system.
    -   Librarians can export book data to a CSV file.

-   **Book Borrowing:**
    -   Users can check out available books.
    -   Users can return borrowed books.

-   **Dashboard:**
    -   Displays the list of all books and the books borrowed by the current user.