Hotel Booking Backend

This is the backend for a Hotel Booking application, implemented using FastAPIc. The backend provides API endpoints for managing users, rooms, bookings, ratings, payments, and images.

Users can register, log in, and manage their bookings.

Users can leave reviews for visited rooms and view other users’ ratings.

Admins can manage users, rooms, and bookings, including canceling reservations.

Rooms and bookings can be searched and filtered by various parameters.

Payments are simulated with Stripe sandbox integration, including refunds.

Images can be uploaded and associated with users or rooms.

Basic security is implemented: hashed passwords, JWT authentication, and token-based endpoint protection.

Tech Stack

FastAPI – backend framework

SQLAlchemy – asynchronous ORM

Pydantic – data validation

PostgreSQL – database (can be run via Docker)

Docker/Docker Compose – containerization

Stripe – payment sandbox

Uvicorn – ASGI server

Project Structure

The backend is organized following best practices with dependency injection and the Unit of Work pattern.

app/
├─ api/                 # Routers
│  ├─ booking.py
│  ├─ room.py
│  ├─ rating.py
│  ├─ image.py
│  └─ payment.py
├─ core/                # Settings and configuration
├─ db/                  # Database models and session
├─ schemas/             # Pydantic models
├─ services/            # Business logic
└─ main.py              # Application entrypoint

Endpoints
Booking

GET /booking/get_bookings_for_one_user – Get bookings for the logged-in user

GET /booking/get_one/{booking_id} – Get a single booking by ID

GET /booking/get_bookings_for_rooms_not_rated_by_user – Get rooms not yet rated by the user

PUT /booking/cancel_booking/{id} – Cancel a booking

POST /booking/refund_booking – Refund a booking

Room

GET /room – Get all rooms (with optional pagination)

GET /room/search/{start_date}/{end_date}/{capacity} – Search rooms by date and capacity

GET /room/get_one/{room_id} – Get details for one room

PUT /room/{room_id} – Update a room

DELETE /room/{room_id} – Delete a room

GET /room/get_with_filters – Get rooms filtered by specific parameters

GET /room/get_rooms_booked_not_rated_by_user – Get rooms booked by the user that are not rated

Rating

POST /rating – Create a rating for a room

GET /rating/get_average_rating/room/{room_id} – Get the average rating for a room

GET /rating/get_average_ratings – Get average ratings for all rooms

Image

POST /image/ – Upload an image for a user

PUT /image/ – Update a user image

GET /image/ – Get the image of the logged-in user

Security

Passwords are hashed using HS256

JWT tokens secure endpoints

Refresh tokens are stored in secure cookies

Admin-only endpoints are protected

Setup

Clone the repository:

git clone <repo_url>
cd hotel-backend


Create a .env file with required variables:

DATABASE_URL=postgresql://user:password@localhost:5432/db_name
SECRET_KEY=<your_secret_key>
STRIPE_SECRET_KEY=<stripe_test_secret>


Build and run the database (Docker Compose recommended):

docker-compose up -d


Install dependencies:

pip install -r requirements.txt

Running the Application

Start the FastAPI server using Uvicorn:

uvicorn app.main:app --reload


Interactive API docs will be available at:

http://127.0.0.1:8000/docs