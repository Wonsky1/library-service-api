# Library Service API

Welcome to the Library Management Service API! This API is a Django-based web application designed to modernize and automate the management of book borrowings, payments, and notifications for a library. The system optimizes the work of library administrators and enhances the user experience.

## Getting Started

### Prerequisites

Before you begin, make sure you have the following tools and technologies installed:

- Docker
- Docker-Compose

## Installing / Getting started
> A quick introduction of the setup you need to get run a project.

### Using Git
1. Clone the repo:
```shell
git clone https://github.com/petrykivd/library-service-api
```
2. You can open project in IDE and configure .env file using [.env.sample](.env.sample) file as an example.
<details>
<summary>Parameters for .env file:</summary>

- **STRIPE_SECRET_KEY**: `Your Stripe Secret Key`
- **BOT_TOKEN**: `Your Bot Token`
- **ADMIN_GROUP**: `Your Admin Group in Telegram`
- **TURN_BOT_ON**: `True/False`
- **POSTGRES_DB**: `Your Postgres DB`
- **POSTGRES_USER**: `Your Postgres User`
- **POSTGRES_PASSWORD**: `Your password in DB`
- **POSTGRES_HOST** `Host of your DB`
- **POSTGRES_HOST** `Port of your DB`
</details>

3. Run docker-compose command to build and run containers:
```shell
docker-compose up --build
```
> To access browsable api, use http://localhost:8000/api/
> 
> To get access to the content, visit http://localhost:8000/api/user/token/ to get JWT token.
> 
> Use the following admin user:
> - Email: admin@admin.com
> - Password: 12345

## API Endpoints
<details>
  <summary>Books</summary>

- **List Books**: `GET /api/books/`
- **Create Book**: `POST /api/books/`
- **Retrieve Book**: `GET /api/books/{book_id}/`
- **Update Book**: `PUT /api/books/{book_id}/`
- **Partial Update** `PATCH /api/books/{book_id}/`
- **Delete Book**: `DELETE /api/books/{book_id}/`
- **Upload Astronomy Show Image**: `POST /api/books/{book_id}/upload-image/`
</details>

<details>
  <summary>Borrowings</summary>
  
**List Borrowings**: `GET /api/borrowings/`
- **Create Borrowing**: `POST /api/borrowings/`
- **Retrieve Borrowing**: `GET /api/borrowings/{borrowing_id}/`
- **Update Borrowing**: `PUT /api/borrowings/{borrowing_id}/`
- **Partial Update** `PATCH /api/borrowings/{borrowing_id}/`
- **Delete Borrowing**: `DELETE /api/borrowings/{borrowing_id}/`
</details>

<details>
  <summary>Payments</summary>
  
- **List Payments**: `GET /api/payments/`
- **Retrieve Payment**: `GET /api/payments/{payment_id}/`
- **Create Payment**: `POST /api/payments/`
- **Update Payment**: `PUT /api/payments/{payment_id}/`
- **Partial Update** `PATCH /api/payments/{payment_id}/`
- **Delete Payment**: `DELETE /api/payments/{payment_id}/`
</details>

<details>
  <summary>Show Themes</summary>
  
- **List Show Themes**: `GET /api/planetarium/show-themes/`
- **Create Show Theme**: `POST /api/planetarium/show-themes/`
- **Retrieve Show Theme**: `GET /api/planetarium/show-themes/{show_theme_id}/`
- **Update Show Theme**: `PUT /api/planetarium/show-themes/{show_theme_id}/`
- **Partial Update** `PATCH /api/planetarium/show-themes/{show_theme_id}/`
- **Delete Show Theme**: `DELETE /api/planetarium/show-themes/{show_theme_id}/`
</details>

<details>
  <summary>User</summary>
  
- **Information about current User**: `GET /api/user/me/`
- **Update User**: `PUT /api/user/me/`
- **Partial Update** `PATCH /api/user/me/`
- **Create new User** `POST /api/user/register/`
- **Create access and refresh tokens** `POST /api/user/token/`
- **Refresh access token** `POST /api/user/token/refresh/`
- **Verify tokens**: `POST /api/user/token/verify/`
</details>


## Authentication
- The API uses token-based authentication for user access. Users need to obtain an authentication token by logging in.
- Administrators and authenticated users can access all endpoints, but only administrators can change information about books, borrowings, and related entities. Each authenticated user can access and create their own borrowings.

## Documentation
- The API is documented using the OpenAPI standard.
- Access the API documentation by running the server and navigating to http://localhost:8000/api/doc/swagger/ or http://localhost:8000/api/doc/redoc/.

## DB Structure
![image]()

## Contributing

Feel free to contribute to these enhancements, and let's make our Library Management Service API even better!

## License
This project is licensed under the MIT License.
