Hotel Booking Backend
This is the backend for a Hotel Booking application, implemented using FastAPI.
It provides RESTful API endpoints for managing users, rooms, bookings, ratings, payments, and images.

✨ Features
Users can:
Register and log in
Manage their bookings
Leave reviews for visited rooms
View other users’ ratings
Admins can:
Manage users, rooms, and bookings
Cancel reservations
Rooms & Bookings support:
Search and filtering by date, capacity, and other parameters
Payments are simulated via Stripe sandbox, including refunds
Images can be uploaded and associated with users or rooms
Security includes:
Password hashing (HS256)
JWT-based authentication
Token-protected endpoints
Secure cookie storage for refresh tokens
Admin-only route protection
🛠️ Tech Stack
Component
Technology
Backend Framework
FastAPI
ORM
SQLAlchemy (async)
Validation
Pydantic
Database
PostgreSQL (via Docker)
Containerization
Docker / Docker Compose
Payments
Stripe (sandbox mode)
ASGI Server
Uvicorn
Migrations
Alembic
📁 Project Structure
123456789101112
app/
├── api/                # Routers
│   ├── booking.py
│   ├── room.py
│   ├── rating.py
│   ├── image.py
│   └── payment.py
├── core/               # Settings & config
├── db/                 # DB models & session
├── schemas/            # Pydantic models

Built using dependency injection and the Unit of Work pattern.

🌐 API Endpoints
📅 Booking
GET /booking/get_bookings_for_one_user – Get bookings for the logged-in user
GET /booking/get_one/{booking_id} – Get a single booking by ID
GET /booking/get_bookings_for_rooms_not_rated_by_user – Get rooms not yet rated by the user
PUT /booking/cancel_booking/{id} – Cancel a booking
POST /booking/refund_booking – Refund a booking
🏨 Room
GET /room – Get all rooms (with optional pagination)
GET /room/search/{start_date}/{end_date}/{capacity} – Search available rooms
GET /room/get_one/{room_id} – Get room details
PUT /room/{room_id} – Update a room (admin only)
DELETE /room/{room_id} – Delete a room (admin only)
GET /room/get_with_filters – Filter rooms by custom parameters
GET /room/get_rooms_booked_not_rated_by_user – Get booked but unrated rooms
⭐ Rating
POST /rating – Create a rating for a room
GET /rating/get_average_rating/room/{room_id} – Get average rating for a room
GET /rating/get_average_ratings – Get average ratings for all rooms
🖼️ Image
POST /image/ – Upload an image for the current user
PUT /image/ – Update user image
GET /image/ – Get image of the logged-in user
🔒 Security
Passwords: hashed with HS256
Authentication: JWT tokens
Refresh tokens: stored in secure HTTP-only cookies
Admin routes: protected by role-based access control
⚙️ Setup
Clone the repo
bash
12
git clone <repo_url>
cd hotel-backend
Create .env file
env
123
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
SECRET_KEY=<your_secret_key>
STRIPE_SECRET_KEY=<stripe_test_secret>
Start database (Docker Compose recommended)
bash
1
docker-compose up -d
Install dependencies
bash
1
Run migrations
bash
1
alembic upgrade head
⚠️ Required before first run to create tables.

Start the server
bash
1
API docs: http://127.0.0.1:8000/docs
💳 Stripe Webhook Integration
The app uses Stripe webhooks to securely confirm payment events.

❗ Redirect URLs are only for UX — not trusted for payment validation.

Webhook Endpoint
1
POST http://localhost:8000/stripe-webhook
Handles:

Signature verification
Payment confirmation (checkout.session.completed, payment_intent.succeeded)
Refund processing (charge.refunded)
Database status updates
Local Development Setup
Install Stripe CLI
Follow instructions: https://stripe.com/docs/stripe-cli
Verify installation
bash
1
stripe --version
Log in
bash
1
stripe login
Start webhook listener
bash
1
stripe listen --forward-to localhost:8000/stripe-webhook
Output example:
1
Your webhook signing secret is whsec_XXXXXXXXXXXXXXXX
Add secret to .env
env
1
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXX
⚠️ Webhooks will be rejected if this is missing or incorrect.

Supported Stripe Events
Event
Purpose
checkout.session.completed
Confirms successful payment
payment_intent.succeeded
Confirms funds captured
charge.refunded
Confirms refund completed
All business logic is triggered only after webhook signature verification.

🌱 Room Data Seeding Script
A script (populate_rooms.py) seeds the database with sample rooms and Base64-encoded images for development/testing only.

Purpose
Quickly populate realistic test data
Avoid manual API calls during dev
Enable immediate UI/booking testing
How It Works
Reads predefined room data (type, price, capacity, etc.)
Loads Base64 image from .txt files (e.g., image1.txt)
Saves via UnitOfWork.room.create()
Skips rooms if image file is missing
Requirements
Images must be Base64 strings in .txt files (no line breaks)
Filenames must exactly match references in script (case-sensitive)
Default image folder:
python
1
folder_path = "C:\\Users\\User\\Desktop\\hotel-rooms"
Execution
bash
1
python populate_rooms.py
⚠️ Never run in production!
