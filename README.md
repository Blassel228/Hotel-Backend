# Hotel Booking Backend

This is the backend for a **Hotel Booking** application, implemented using **FastAPI**. The backend provides API endpoints for managing **users, rooms, bookings, ratings, payments, and images**.

Users can **register, log in, and manage their bookings**.  
Users can **leave reviews** for visited rooms and view other users’ ratings.  
Admins can **manage users, rooms, and bookings**, including canceling reservations.  
Rooms and bookings can be **searched and filtered** by various parameters.  
Payments are simulated with **Stripe sandbox integration**, including refunds.  
Images can be **uploaded and associated** with users or rooms.  

Basic security is implemented: **hashed passwords**, **JWT authentication**, and **token-based endpoint protection**.

---

## Tech Stack

- **FastAPI** – backend framework  
- **SQLAlchemy** – asynchronous ORM  
- **Pydantic** – data validation  
- **PostgreSQL** – database (can be run via Docker)  
- **Docker/Docker Compose** – containerization  
- **Stripe** – payment sandbox  
- **Uvicorn** – ASGI server  
- **Alembic** – database migrations  

---

## Endpoints

### Booking
GET /booking/get_bookings_for_one_user # Get bookings for the logged-in user
GET /booking/get_one/{booking_id} # Get a single booking by ID
GET /booking/get_bookings_for_rooms_not_rated_by_user # Get rooms not yet rated by the user
PUT /booking/cancel_booking/{id} # Cancel a booking
POST /booking/refund_booking # Refund a booking

shell
Копіювати код

### Room
GET /room # Get all rooms (with optional pagination)
GET /room/search/{start_date}/{end_date}/{capacity} # Search rooms by date and capacity
GET /room/get_one/{room_id} # Get details for one room
PUT /room/{room_id} # Update a room
DELETE /room/{room_id} # Delete a room
GET /room/get_with_filters # Get rooms filtered by specific parameters
GET /room/get_rooms_booked_not_rated_by_user # Get rooms booked by the user that are not rated

shell
Копіювати код

### Rating
POST /rating # Create a rating for a room
GET /rating/get_average_rating/room/{room_id} # Get the average rating for a room
GET /rating/get_average_ratings # Get average ratings for all rooms

shell
Копіювати код

### Image
POST /image/ # Upload an image for a user
PUT /image/ # Update a user image
GET /image/ # Get the image of the logged-in user

yaml
Копіювати код

---

## Security

- Passwords are hashed using **HS256**  
- **JWT tokens** secure endpoints  
- Refresh tokens are stored in **secure cookies**  
- **Admin-only endpoints** are protected  

---

## Setup

Clone the repository:
git clone <repo_url>
cd hotel-backend

csharp
Копіювати код

Create a `.env` file with required variables:
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
SECRET_KEY=<your_secret_key>
STRIPE_SECRET_KEY=<stripe_test_secret>

arduino
Копіювати код

Build and run the database (Docker Compose recommended):
docker-compose up -d

yaml
Копіювати код

Install dependencies:
pip install -r requirements.txt

yaml
Копіювати код

---

## Database Migrations (Alembic)

The project uses **Alembic** to manage database schema migrations.  

After configuring the database and environment variables, apply all existing migrations by running:
alembic upgrade head

yaml
Копіювати код
This command must be executed before running the application for the first time to ensure all database tables and schema changes are applied.

---

## Running the Application

Start the FastAPI server using Uvicorn:
uvicorn app.main:app --reload

arduino
Копіювати код

Interactive API docs will be available at:
http://127.0.0.1:8000/docs

yaml
Копіювати код

---

## Stripe Webhook (Local Development & Console Listener)

The application uses **Stripe Webhooks** to securely confirm payment events such as successful payments and refunds.  
Webhook processing is mandatory because redirect URLs alone are not a reliable source of truth for payment status.

### Webhook Endpoint
POST http://localhost:8000/stripe-webhook

markdown
Копіювати код

This endpoint is responsible for:

- Verifying the **Stripe webhook signature**  
- Handling **payment confirmation events**  
- Updating **booking and payment statuses** in the database  
- Processing **refunds** when applicable  

### Running the Stripe Webhook Listener (Console)

For local development, Stripe webhooks are delivered using the **Stripe CLI**, which runs directly in the console.

1. **Install Stripe CLI**  
Follow the official installation instructions for your OS:  
[https://stripe.com/docs/stripe-cli](https://stripe.com/docs/stripe-cli)  

Verify installation:
stripe --version

markdown
Копіювати код

2. **Log in to Stripe via CLI**
stripe login

pgsql
Копіювати код
This command opens a browser window to authenticate your Stripe account.

3. **Start the Webhook Listener**
stripe listen --forward-to localhost:8000/stripe-webhook

markdown
Копіювати код
✔ This command:  
- Listens for Stripe events in test mode  
- Forwards them to your local FastAPI backend  
- Outputs a **Webhook Signing Secret**

Example output:
Your webhook signing secret is whsec_XXXXXXXXXXXXXXXX

markdown
Копіювати код

4. **Set the Webhook Secret in .env**
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXX

sql
Копіювати код
⚠️ The application will reject webhook events if this value is missing or incorrect.

### Events Handled by the Application

| Event                        | Purpose                        |
|-------------------------------|--------------------------------|
| checkout.session.completed     | Confirms successful payment    |
| payment_intent.succeeded       | Confirms funds capture         |
| charge.refunded                | Confirms refund completion     |

All business logic (booking confirmation, refunds, status updates) is triggered only after webhook verification.

### Security: Webhook Signature Verification

Every webhook request is validated using:

- **STRIPE_WEBHOOK_SECRET**  
- Stripe’s **Stripe-Signature** header

This guarantees:

- Events are genuinely sent by Stripe  
- Payloads were not tampered with  
- Payments cannot be spoofed by clients  

### Redirect URLs (User Experience Only)

Redirect URLs are used only for UX, not for payment validation:
STRIPE_SUCCESS_URL=http://localhost:8000/payment/success
STRIPE_CANCEL_URL=http://localhost:8000/payment/cancel

vbnet
Копіювати код
⚠️ The backend does not rely on redirect URLs to confirm payment status.

---

## Room Data Seeding Script (Rooms + Images)

For development and testing purposes, the project includes a data seeding script that populates the rooms table with predefined room data and associated images.  

This script is **not part of the production flow**.  
It exists solely to simplify local development, demos, and testing by quickly filling the database with realistic room data.

### Purpose of the Script

The script:

- Inserts predefined room records into the database  
- Associates each room with an image stored as a Base64 string  
- Uses existing enums (**RoomType**, **RoomAreas**) to ensure data consistency  
- Works asynchronously using the **Unit of Work** pattern  

This avoids the need to manually create rooms or upload images through the API during development.

### File Location & Execution

The script can be run manually from the console:
python populate_rooms.py

csharp
Копіювати код
(Exact filename may vary depending on where you place it.)  

It uses `asyncio.run()` and therefore **must not be executed inside an already running event loop**.

### How It Works (Step-by-Step)

A predefined list of rooms is declared in the script. Each room entry contains:

- Room metadata (type, price, capacity, etc.)  
- A reference to an image file name (e.g., `image1.txt`)  

The script:

1. Reads the image file from disk  
2. Loads the Base64-encoded image string  
3. Injects it into the room data  
4. Saves the room using `UnitOfWork.room.create()`  

If an image file is missing, that room is skipped and not inserted.

### Image Storage Format

**Important:** Image files must be Base64-encoded.  

- Room images are **not raw image files** (.jpg, .png, etc.)  
- Each image must be stored as a **.txt file**  
- Containing a **Base64-encoded string** without extra whitespace or line breaks  

Example file content:
iVBORw0KGgoAAAANSUhEUgAA...

mathematica
Копіювати код

### Image Naming Convention (Required)

Image filenames must exactly match the names referenced in the script.

| Room Entry | Image File |
|------------|------------|
| First room | image1.txt |
| Second room | image2.txt |
| Third room | image3.txt |
| ...        | ...        |

If the script contains:
"image": "image4.txt"

arduino
Копіювати код
Then the following file **must exist** in the image folder:
image4.txt

lua
Копіювати код
Otherwise, the script will output:
File NOT found: image4.txt

csharp
Копіювати код
and skip that room.

### Image Folder Location

The folder path is defined explicitly in the script:
folder_path = "C:\Users\User\Desktop\hotel-rooms"

markdown
Копіювати код
You may change this path as needed, but:

- All image `.txt` files must be inside this directory  
- File names must match exactly (case-sensitive on Linux/macOS)  

### Why This Script Exists

This script was added for simplicity:

- To speed up local setup  
- To provide realistic test data  
- To avoid manual API calls for room creation  
- To make UI and booking flows immediately usable  

⚠️ It is **not intended for production use** and should not be run against a live database.

### Assumptions & Constraints

- Images are stored as **Base64 strings** in the database  
- The **RoomBase schema** accepts an `image` field  
- The database schema already exists  
- Enums (**RoomType**, **RoomAreas**) are synchronized with the database  

If any of these change, the script must be updated accordingly.
