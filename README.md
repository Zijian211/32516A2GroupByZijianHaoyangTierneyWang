# 32516 Assignment 2 Group Project  
# Zijian Electronic Devices EBuy — Advanced E-Commerce Platform

## Project Overview

This project is an advanced full-stack e-commerce platform developed for **32516 Internet Programming Assignment 2**. It extends the original A1 individual project, **Zijian Electronic Devices E-Commerce Platform**, into a more secure, role-based, and administration-oriented web application.

The original A1 project already provided a complete shopping workflow, including product browsing, live search, category filtering, user registration/login, shopping cart management, checkout, order history, MongoDB persistence, and cloud deployment. Assignment 2 builds on this foundation by adding password hashing, JWT-based authentication, protected backend routes, role-based access control, and an admin dashboard for viewing users’ shopping carts and order-related information.

The final system behaves as a single-page application. The React frontend dynamically renders either the normal shopping interface or the admin dashboard depending on the logged-in user’s role. Normal users can browse products, manage carts, and place simulated orders. Admin users can access protected administrative views for monitoring user cart and order information.

---

## Group Members

| Member | Main Role | Key Responsibility |
|---|---|---|
| **Zijian Hua** | Project Lead / Infrastructure & Integration Lead | A1-to-A2 project migration, database separation, integration testing, deployment configuration, database export, README and final documentation |
| **Haoyang** | Security / JWT Authentication Lead | Password hashing, JWT token generation, protected routes, role-based access control, frontend token storage and Authorization header integration |
| **Tierney Wang** | Frontend Admin Feature / UI Lead | Admin dashboard, admin cart and order lookup interface, responsive UI, loading/error/empty states, frontend demo support |

---

## A1 Foundation

The original A1 project implemented a functional FARM-stack e-commerce application. Its main features included:

* Product catalogue for electronic devices
* Real-time product search
* Category filtering
* User registration and login
* Persistent shopping cart
* Add, update, and remove cart items
* Checkout workflow
* Order history
* MongoDB Atlas cloud database
* React single-page frontend
* FastAPI backend CRUD operations
* Vercel frontend deployment
* Render backend deployment
* UptimeRobot monitoring to reduce backend sleeping time

In A1, checkout was intentionally simplified as a simulated e-commerce workflow. Since the website is not a real payment platform, users do not enter payment or shipping information. Once a user clicks checkout, the current cart is converted into a completed order and the cart is cleared.

---

## A2 Extension Summary

Assignment 2 extends the A1 system in three major directions:

### 1. Security Upgrade: Password Hashing and JWT Authentication
The A1 login system has been upgraded with:
* Password hashing using `passlib` and `bcrypt`
* JWT access token generation after successful login
* `Authorization: Bearer <token>` headers for protected API requests
* Protected backend routes using FastAPI dependencies
* Role-based access control for `user` and `admin`
* Secure password change workflow using hashed password verification

This means users no longer rely only on local user IDs. Sensitive cart, order, user, and admin operations require a valid JWT.

### 2. Role-Based User and Admin Separation
The system supports two roles:

| Role | Description |
|---|---|
| `user` | Normal shopping user who can browse products, manage their cart, checkout, and view their own orders |
| `admin` | Administrative user who can access protected admin features and view regular users’ cart/order information |

Normal users are created through public registration and are always assigned the `user` role. Admin accounts are configured in MongoDB by assigning `role: "admin"` to trusted accounts. Public registration does not allow normal users to create admin accounts.

After login, the frontend reads the returned role and conditionally renders:
* Normal shopping interface for regular users
* Admin dashboard for admin users

### 3. Admin Dashboard
The A2 admin interface is a new React frontend feature. It is not a database tool or FastAPI testing page. Instead, it is a real user-facing admin dashboard inside the shopping website.

The admin dashboard allows an admin user to:
* View users
* Select a user
* View that user’s current cart items
* View quantities, prices, subtotals, and cart totals
* View order-related information
* Use a clean dashboard-style interface with loading, empty, and error states

This feature demonstrates how backend-protected admin APIs are integrated into a real React single-page application.

---

## Technical Stack

### Frontend
* React, Vite, JavaScript / JSX, Tailwind CSS
* React state management with custom hooks
* Browser Local Storage for storing user session data and JWT token
* Fetch API for frontend-backend communication

### Backend
* FastAPI, Python, Uvicorn development server
* Motor async MongoDB driver
* Pydantic for request validation
* Passlib + bcrypt for password hashing
* Python-Jose for JWT creation and verification

### Database
* MongoDB Atlas
* Separate A2 database from A1 database
* Collections include: `products`, `users`, `cart`, `orders`

### Deployment
* Frontend: Vercel
* Backend: Render
* Backend monitoring: UptimeRobot

---

## Database Separation Between A1 and A2

To protect the original A1 data, the A2 project uses a separate MongoDB database.

| Project | Database |
|---|---|
| A1 Original Project | `ecommerce_db` |
| A2 Group Extension | `finalecommerce_db` or A2 test database such as `final_ecommerce_db` |

The backend reads the database name from the environment variable:

    MONGODB_DB_NAME=finalecommerce_db

This allows A2 development, JWT testing, admin accounts, cart testing, and order testing to run independently from the original A1 database.

---

## Main Features

### User Features
* Register account
* Login account
* Password complexity validation
* JWT-based login session
* Browse electronic products
* Search products in real time
* Filter products by category
* Add products to cart
* Update cart item quantities
* Remove products from cart
* Checkout cart into an order
* View order history
* Change password
* Delete account

### Admin Features
* Login as admin
* Access admin-only dashboard
* View user cart information
* View user order-related information
* Inspect cart quantities, subtotals, and totals
* Access admin-only APIs protected by JWT and role checking
* All other Users' features inside FastAPI

### Security Features
* Passwords are stored as hashes, not plain text
* JWT token is issued after successful login
* Protected routes require `Authorization: Bearer <token>`
* Normal users can only access their own cart, orders, and account data
* Admin-only APIs require both valid JWT and `role: "admin"`
* Public signup always creates normal users, not admin users
* Sensitive environment variables are stored in `.env`, not committed to GitHub

---

## CRUD Coverage

The system involves CRUD operations across multiple conceptual entities.

| Entity | Create | Read | Update | Delete |
|---|---|---|---|---|
| **User** | Register account | Admin can view users | Change password / update role in controlled admin setup | Delete account |
| **Product** | Seed product catalogue | Browse, search, and filter products | Product data can be managed through seed/export process | Product data can be reset through seed process |
| **Cart / Cart Item** | Add product to cart | View user cart | Update item quantity | Remove item from cart |
| **Order** | Checkout creates order | View order history | Update order item quantity / order status logic | Delete order |

The project therefore satisfies the requirement of involving multiple database-backed entities and full CRUD-style business logic.

---

## Folder Structure

    A2-ECOMMERCE PLATFORM/
    │
    ├── backend/
    │   ├── main.py
    │   │   └── FastAPI application, authentication, JWT, CRUD routes, admin routes
    │   │
    │   ├── seed.py
    │   │   └── Seeds product data into the selected MongoDB database
    │   │
    │   ├── requirements.txt
    │   │   └── Python dependencies
    │   │
    │   ├── .env.example
    │   │   └── Example environment variables for safe setup
    │   │
    │   └── database_export/
    │       ├── products.json
    │       ├── sample_users.json
    │       ├── sample_carts.json
    │       └── sample_orders.json
    │
    ├── frontend/
    │   ├── public/
    │   │   └── Static assets
    │   │
    │   ├── src/
    │   │   ├── assets/
    │   │   │   └── Images and frontend assets
    │   │   │
    │   ├── components/
    │   │   │   ├── ProductCard.jsx
    │   │   │   ├── CartDrawer.jsx
    │   │   │   ├── AuthModal.jsx
    │   │   │   ├── Orders.jsx
    │   │   │   └── AdminCartView.jsx
    │   │   │
    │   ├── hooks/
    │   │   │   ├── useAuth.js
    │   │   │   ├── useCart.js
    │   │   │   └── useOrders.js
    │   │   │
    │   ├── services/
    │   │   │   └── api.js
    │   │   │
    │   ├── App.jsx
    │   ├── main.jsx
    │   ├── App.css
    │   └── index.css
    │
    ├── index.html
    ├── package.json
    └── vite.config.js
    │
    ├── .gitignore
    ├── README.md
    ├── CONTRIBUTIONS.md
    └── TESTING.md

---

## Environment Variables

Create a real `.env` file inside the `backend/` folder. **Do not commit the real `.env` file.**
Example:

    MONGODB_URL=your_mongodb_atlas_connection_string
    MONGODB_DB_NAME=finalecommerce_db
    JWT_SECRET=your_jwt_secret_key
    JWT_ALGORITHM=HS256

The repository includes `backend/.env.example` for safe setup instructions.

---

## Backend Setup

Open a terminal in the `backend` folder:

    cd backend

Create and activate a virtual environment:

    py -m venv venv
    .\venv\Scripts\Activate.ps1

Install dependencies:

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

Seed the database:

    python seed.py

Run the FastAPI backend:

    uvicorn main:app --reload

* **Backend local URL:** `http://127.0.0.1:8000`
* **FastAPI Swagger UI:** `http://127.0.0.1:8000/docs`

---

## Frontend Setup

Open another terminal in the `frontend` folder:

    cd frontend

Install frontend dependencies:

    npm install

Run the React development server:

    npm run dev

* **Frontend local URL:** `http://localhost:5173`

---

## Deployment Links

* **Live Website:**  (TODO: Add A2 Vercel frontend link)
* **Backend API:**  (TODO: Add A2 Render backend link)
* **GitHub Repository:** https://github.com/Zijian211/32516A2GroupByZijianHaoyangTierneyWang

---

## API Overview

### Public Routes
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API health check |
| `GET` | `/products` | Fetch all products |
| `POST` | `/auth/signup` | Register new user |
| `POST` | `/auth/login` | Login and receive JWT token |

### User-Protected Routes (Can be used by Admins via user_id)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/cart` | Add item to cart |
| `GET` | `/cart/{user_id}` | View user cart |
| `PUT` | `/cart/{user_id}/{product_id}` | Update cart item quantity |
| `DELETE` | `/cart/{user_id}/{product_id}` | Remove item from cart |
| `POST` | `/orders` | Checkout cart into order |
| `GET` | `/orders/{user_id}` | View user orders |
| `PUT` | `/users/{user_id}/password` | Change password |
| `DELETE` | `/users/{user_id}` | Delete account |

### Admin-Protected Routes (Accessed only by Admins)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/users` | Admin-only user list |
| `GET` | `/admin/carts` | Admin-only user cart overview |

---

## Admin Account Setup

Normal users are created through the public registration form and are assigned the `user` role.
Admin accounts are configured in MongoDB by changing a trusted user document from:

    {
      "role": "user"
    }

to:

    {
      "role": "admin"
    }

After the role is changed, the admin must log out and log in again to receive a new JWT token containing the `admin` role.
*Admin accounts are not created through public registration.*

---

## Testing Checklist

The following workflows were tested:

### Normal User Workflow
- [x] Register new user
- [x] Confirm password is stored as a hash in MongoDB
- [x] Login and receive JWT token
- [x] Confirm frontend stores token
- [x] Confirm protected requests include `Authorization: Bearer <token>`
- [x] Add product to cart
- [x] Update quantity
- [x] Remove product from cart
- [x] Checkout
- [x] View order history
- [x] Change password
- [x] Logout and login again

### Security Workflow
- [x] No token access to protected routes returns unauthorized response
- [x] Normal user cannot access other users’ cart or order data
- [x] Normal user cannot access admin APIs
- [x] Admin token can access admin dashboard data
- [x] Public signup cannot create admin users

### Admin Workflow
- [x] Login as admin
- [x] View admin dashboard
- [x] View user cart information
- [x] View user order-related information
- [x] Confirm admin dashboard is rendered inside the React SPA
- [x] Confirm admin unique route requires JWT and admin role (FastAPI and Authorization)

---

## Workload Allocation

### Zijian Hua
Zijian led the transition from the original A1 e-commerce platform into the A2 group extension. His work focused on infrastructure separation, integration, deployment, testing, database export, and documentation.

**Specific contributions:**
* Created and maintained the A2 group repository based on the original A1 FARM-stack e-commerce project.
* Separated the A2 project from the original A1 project so that A2 development would not affect the existing A1 website, deployment, or MongoDB data.
* Refactored backend database configuration to support environment-based database selection using `MONGODB_DB_NAME`.
* Configured the A2 backend to use a separate MongoDB database from the A1 `ecommerce_db`.
* Updated or supported `seed.py` so product seed data can be inserted into the selected A2 database.
* Prepared `.env.example` and database export files for safe setup and submission.
* Integrated and tested Haoyang’s JWT authentication and protected route implementation within the original A1 e-commerce workflow.
* Coordinated Tierney’s admin dashboard frontend with the backend admin API.
* Conducted end-to-end testing across registration, login, cart, checkout, order history, admin cart view, and account management workflows.
* Prepared final README, contribution documentation, deployment setup, and testing checklist.

**Files / areas:**
`backend/main.py`, `backend/seed.py`, `backend/.env.example`, `backend/database_export/`, `README.md`, `CONTRIBUTIONS.md`, `TESTING.md`, deployment configuration

### Haoyang
Haoyang was responsible for the JWT authentication and security upgrade of the system.

**Specific contributions:**
* Implemented password hashing using `passlib` and `bcrypt`.
* Updated user signup so passwords are stored as secure hashes.
* Updated login to verify hashed passwords and issue JWT tokens.
* Added JWT token payload with user ID and role.
* Implemented `get_current_user()` to validate bearer tokens.
* Implemented `require_admin()` for admin-only backend access.
* Protected cart, order, user, and admin routes using FastAPI dependencies.
* Fixed password change logic so old passwords are verified against hashes and new passwords are stored as hashes.
* Updated frontend authentication logic to store JWT tokens.
* Updated API service functions to send `Authorization: Bearer <token>` headers.

**Files / areas:**
`backend/main.py`, `backend/requirements.txt`, `frontend/src/hooks/useAuth.js`, `frontend/src/services/api.js`

### Tierney Wang
Tierney was responsible for the admin-facing frontend feature and user interface improvement.

**Specific contributions:**
* Created the admin dashboard interface for role-based admin users.
* Implemented `AdminCartView.jsx`.
* Designed the admin cart and order lookup interface.
* Added admin-only navigation behaviour.
* Displayed user cart items, quantities, prices, subtotals, and total values.
* Added empty, loading, and error states for admin views.
* Improved frontend layout and responsiveness for the admin dashboard.
* Supported final frontend testing and demo preparation.

**Files / areas:**
`frontend/src/components/AdminCartView.jsx`, `frontend/src/App.jsx`, `frontend/src/App.css`, `frontend/src/index.css`, `frontend/src/services/api.js`

---

## Challenges and Solutions

**1. Separating A1 and A2 Infrastructure**
Since the A2 project extends the original A1 project, a key challenge was ensuring that A2 development did not affect the original A1 deployment or database. This was solved by using a new A2 GitHub repository, a separate backend/frontend deployment pipeline, and an environment-based MongoDB database selection using `MONGODB_DB_NAME`.

**2. JWT Integration Across Frontend and Backend**
JWT authentication required coordinated changes across backend and frontend. The backend needed to hash passwords, issue tokens, and protect routes. The frontend needed to store the token and attach it to API requests. This was solved by updating `useAuth.js` and centralising authenticated request headers inside `api.js`.

**3. Role-Based Interface Rendering**
The system needed to show different interfaces to normal users and admins. This was solved by storing the logged-in user’s role and conditionally rendering either the shopping interface or the admin dashboard.

**4. Admin Dashboard as a Real Website Feature**
FastAPI Swagger UI and MongoDB Compass are developer tools, not user-facing website features. Therefore, the admin dashboard was implemented in React as part of the single-page application. This allows admins to use the website itself to view user cart and order information.

---

## Notes on Simulated Checkout

This project is a simulated e-commerce platform for academic purposes. It does not process real payments or collect real shipping information. When a user clicks checkout, the current cart is converted into a completed order and the cart is cleared. This design keeps the focus on full-stack CRUD logic, user state, JWT authentication, and role-based business functionality.

---

## Final Project Status

The project demonstrates:
* A full-stack e-commerce website
* React SPA behaviour
* MongoDB-backed CRUD operations
* JWT-based authentication
* Password hashing
* Role-based access control
* Admin dashboard
* Separate A1 and A2 database configuration
* Cloud deployment workflow
* Clear group workload allocation
