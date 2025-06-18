import os
import asyncio  # Added for async functionality

from app.enums.room_areas import RoomAreas
from app.enums.room_types import RoomType
from app.utils.unitofwork import UnitOfWork  # No changes to imports
from app.schemas.room import RoomBase  # No changes to imports

# Instantiate ABCUnitOfWork instead of assigning the class itself
unit_of_work = UnitOfWork()  # Changed: Create an instance of ABCUnitOfWork


def read_base64_from_file(file_path):
    """Reads a Base64 string from a .txt file."""
    with open(file_path, "r") as f:
        return f.read().strip()  # Strip any extra whitespace or newlines


# Changed the function to be asynchronous and added comments for clarity
async def populate_properties_with_images(folder_path):
    """Populates the Property table with data and Base64 images."""
    # Mock data for properties (unchanged)
    # properties = [
    #     {
    #         "type": "Hotel",
    #         "price": 500,
    #         "address": "123 Beach Road, Miami, FL",
    #         "bedrooms": 10,
    #         "bathrooms": 15,
    #         "area": "Downtown Miami",
    #         "floor": 5,
    #         "parking_spots": 20,
    #         "total_space": "20,000 sq ft",
    #         "contract_status": "Available",
    #         "payment_process": "Online Payment Accepted",
    #         "safety_feature": "24/7 Security System",
    #         "image": "image1.txt",  # File name for the Base64 image
    #     },
    #     {
    #         "type": "Resort",
    #         "price": 1000,
    #         "address": "456 Mountain View, Aspen, CO",
    #         "bedrooms": 5,
    #         "bathrooms": 7,
    #         "area": "Aspen Valley",
    #         "floor": 3,
    #         "parking_spots": 10,
    #         "total_space": "10,000 sq ft",
    #         "contract_status": "Pending",
    #         "payment_process": "Bank Transfer Only",
    #         "safety_feature": "Fire Extinguishers Installed",
    #         "image": "image3.txt",
    #     },
    #     {
    #         "type": "Villa",
    #         "price": 750,
    #         "address": "789 Sunset Blvd, Los Angeles, CA",
    #         "bedrooms": 3,
    #         "bathrooms": 4,
    #         "area": "Hollywood Hills",
    #         "floor": 2,
    #         "parking_spots": 5,
    #         "total_space": "5,000 sq ft",
    #         "contract_status": "Booked",
    #         "payment_process": "Credit Card Accepted",
    #         "safety_feature": "CCTV Surveillance",
    #         "image": "image4.txt",
    #     },
    #     {
    #         "type": "Apartment",
    #         "price": 300,
    #         "address": "101 Park Ave, New York, NY",
    #         "bedrooms": 2,
    #         "bathrooms": 1,
    #         "area": "Midtown Manhattan",
    #         "floor": 10,
    #         "parking_spots": 0,
    #         "total_space": "1,200 sq ft",
    #         "contract_status": "Available",
    #         "payment_process": "PayPal Accepted",
    #         "safety_feature": "Smoke Detectors",
    #         "image": "image5.txt",
    #     },
    #     {
    #         "type": "Cabin",
    #         "price": 200,
    #         "address": "202 Forest Lane, Denver, CO",
    #         "bedrooms": 1,
    #         "bathrooms": 1,
    #         "area": "Rocky Mountains",
    #         "floor": 1,
    #         "parking_spots": 2,
    #         "total_space": "800 sq ft",
    #         "contract_status": "Available",
    #         "payment_process": "Cash Only",
    #         "safety_feature": "First Aid Kit",
    #         "image": "image6.txt",
    #     },
    #     {
    #         "type": "Hotel",
    #         "price": 600,
    #         "address": "303 Ocean Drive, San Diego, CA",
    #         "bedrooms": 12,
    #         "bathrooms": 16,
    #         "area": "La Jolla",
    #         "floor": 8,
    #         "parking_spots": 25,
    #         "total_space": "25,000 sq ft",
    #         "contract_status": "Booked",
    #         "payment_process": "Online Payment Accepted",
    #         "safety_feature": "Emergency Exit Plan",
    #         "image": "image7.txt",
    #     },
    #     {
    #         "type": "Resort",
    #         "price": 1200,
    #         "address": "404 Palm Tree Blvd, Honolulu, HI",
    #         "bedrooms": 8,
    #         "bathrooms": 10,
    #         "area": "Waikiki Beach",
    #         "floor": 4,
    #         "parking_spots": 15,
    #         "total_space": "15,000 sq ft",
    #         "contract_status": "Available",
    #         "payment_process": "Credit Card Accepted",
    #         "safety_feature": "Lifeguards on Duty",
    #         "image": "image8.txt",
    #     },
    #     {
    #         "type": "Villa",
    #         "price": 900,
    #         "address": "505 Hillside Drive, Santa Barbara, CA",
    #         "bedrooms": 4,
    #         "bathrooms": 5,
    #         "area": "Montecito",
    #         "floor": 2,
    #         "parking_spots": 6,
    #         "total_space": "6,000 sq ft",
    #         "contract_status": "Pending",
    #         "payment_process": "Wire Transfer",
    #         "safety_feature": "Gated Community",
    #         "image": "image9.txt",
    #     },
    #     {
    #         "type": "Apartment",
    #         "price": 400,
    #         "address": "606 Riverfront Ave, Chicago, IL",
    #         "bedrooms": 3,
    #         "bathrooms": 2,
    #         "area": "The Loop",
    #         "floor": 15,
    #         "parking_spots": 1,
    #         "total_space": "1,500 sq ft",
    #         "contract_status": "Available",
    #         "payment_process": "Debit Card Accepted",
    #         "safety_feature": "Security Cameras",
    #         "image": "image10.txt",
    #     },
    #     {
    #         "type": "Cabin",
    #         "price": 150,
    #         "address": "707 Lakeview Rd, Seattle, WA",
    #         "bedrooms": 1,
    #         "bathrooms": 1,
    #         "area": "Lake Washington",
    #         "floor": 1,
    #         "parking_spots": 1,
    #         "total_space": "900 sq ft",
    #         "contract_status": "Available",
    #         "payment_process": "Cash Only",
    #         "safety_feature": "Fireplace Safety",
    #         "image": "image11.txt",
    #     },
    # ]
    from enum import Enum  # або твій BaseStrEnum — залежить від реалізації

    # Припускаємо, що RoomType і RoomAreas вже імпортовані
    # from your_module import RoomType, RoomAreas

    rooms = [
        {
            "type": RoomType.SUITE.value,
            "price": 650,
            "beds": 3,
            "bedrooms": 2,
            "bathes": 2,
            "floor": 8,
            "area": RoomAreas.OCEAN_VIEW.value,
            "has_sauna": True,
            "has_jacuzzi": True,
            "description": "This luxurious suite located on the 8th floor of our hotel in San Francisco offers breathtaking ocean views and an elegant atmosphere perfect for discerning travelers. The spacious layout features a king-sized bed, two queen-sized beds, and two beautifully appointed bedrooms with en-suite bathrooms. Guests can relax in the private living area or enjoy a soak in the oversized whirlpool bathtub. The room is equipped with high-speed Wi-Fi, a smart TV, and premium bedding to ensure maximum comfort. A fully functional kitchenette with a mini-refrigerator, microwave, and coffee maker allows guests to prepare light meals without leaving the room. The balcony provides a serene outdoor space where you can enjoy your morning coffee while watching the waves roll in. Our attentive housekeeping staff ensures that the suite remains spotless throughout your stay, and concierge services are available to help plan your local excursions or dining experiences. With its modern design and upscale amenities, this suite is ideal for families, couples, or business travelers seeking a refined retreat in the heart of San Francisco.",
            "total_space": 75.5,
            "image": "image1.txt",
            "capacity": 6
        },
        {
            "type": RoomType.SUITE.value,
            "price": 700,
            "beds": 4,
            "bedrooms": 2,
            "bathes": 2,
            "floor": 12,
            "area": RoomAreas.CITY_VIEW.value,
            "has_sauna": True,
            "has_jacuzzi": False,
            "description": "Perched on the top floor of our San Francisco hotel, this exquisite suite offers panoramic city views stretching from the Financial District to the iconic Golden Gate Bridge. Designed for both luxury and functionality, it features four comfortable beds across two well-appointed bedrooms, making it perfect for families or groups of friends. Each bedroom has an en-suite bathroom fitted with premium toiletries, soft bathrobes, and slippers. The open-plan living and dining area provide ample space for relaxation or entertaining, complemented by large windows that flood the room with natural light. Modern amenities include a state-of-the-art entertainment system, blackout curtains for restful sleep, and a Nespresso machine for freshly brewed coffee. Guests also have access to a private fitness center and a rooftop lounge offering stunning sunset vistas. This top-floor suite combines elegance with convenience, ensuring a memorable stay in one of the most vibrant cities in the world.",
            "total_space": 90.0,
            "image": "image2.txt",
            "capacity": 8
        },
        {
            "type": RoomType.SUITE.value,
            "price": 600,
            "beds": 2,
            "bedrooms": 1,
            "bathes": 1,
            "floor": 5,
            "area": RoomAreas.GARDEN_VIEW.value,
            "has_sauna": False,
            "has_jacuzzi": False,
            "description": "This charming suite overlooks the lush garden courtyard of our San Francisco hotel, providing a peaceful escape from the bustling city streets. The cozy single-bedroom suite is perfect for couples or solo travelers who appreciate nature and tranquility. It includes two plush twin beds that can be combined into a king upon request, and a tastefully decorated bathroom with a rainfall shower and eco-friendly toiletries. Floor-to-ceiling windows allow guests to enjoy the greenery outside while remaining within the comforts of a stylishly furnished interior. The room comes equipped with a work desk, ergonomic chair, and fast internet, making it suitable for remote workers as well. Housekeeping service is provided daily, and room service is available around the clock. Located just minutes from Fisherman’s Wharf and Alcatraz, this suite offers both serenity and accessibility, making it a top choice for visitors exploring the Bay Area.",
            "total_space": 50.2,
            "image": "image3.txt",
            "capacity": 2
        },

        # Deluxe (4)
        {
            "type": RoomType.DELUXE.value,
            "price": 450,
            "beds": 2,
            "bedrooms": 1,
            "bathes": 1,
            "floor": 6,
            "area": RoomAreas.CITY_VIEW.value,
            "has_sauna": False,
            "has_jacuzzi": False,
            "description": "Our Deluxe City View Room is ideally situated on the 6th floor of our San Francisco hotel, offering sweeping vistas of downtown and the surrounding skyline. This single-bedroom room comfortably accommodates two guests with two full-sized beds, making it a great option for couples or traveling companions. The sleek, contemporary design blends comfort with sophistication, featuring a plush seating area, a writing desk, and ambient lighting. The en-suite bathroom is stocked with premium bath products and includes a walk-in shower with adjustable settings. High-speed internet, flat-screen TV, and blackout curtains ensure a relaxing and productive stay. The room also features soundproof windows to minimize noise from the city below. Located near Union Square and major transit hubs, this deluxe room provides easy access to all that San Francisco has to offer, whether you're here for business or pleasure.",
            "total_space": 35.0,
            "image": "image4.txt",
            "capacity": 2
        },
        {
            "type": RoomType.DELUXE.value,
            "price": 500,
            "beds": 3,
            "bedrooms": 2,
            "bathes": 1,
            "floor": 9,
            "area": RoomAreas.PARK_VIEW.value,
            "has_sauna": False,
            "has_jacuzzi": True,
            "description": "This deluxe park-view room is located on the 9th floor of our San Francisco hotel and boasts beautiful views of the central urban park. Featuring two bedrooms and three beds, it's ideal for small families or groups of friends looking for extra space and comfort. One bedroom contains a king-sized bed, while the second bedroom has a twin bed for additional flexibility. The shared bathroom includes a deep soaking tub with a built-in jacuzzi function, perfect for unwinding after a day of exploring the city. The room is thoughtfully designed with modern furnishings, including a compact sitting area, a work desk, and ample storage space. Guests enjoy complimentary bottled water, upgraded bedding, and a selection of teas and coffees. The location offers easy walking access to museums, cafes, and shopping areas, making it a convenient base for tourists and professionals alike.",
            "total_space": 45.0,
            "image": "image5.txt",
            "capacity": 3
        },
        {
            "type": RoomType.DELUXE.value,
            "price": 480,
            "beds": 2,
            "bedrooms": 1,
            "bathes": 1,
            "floor": 4,
            "area": RoomAreas.POOLSIDE_VIEW.value,
            "has_sauna": False,
            "has_jacuzzi": False,
            "description": "Enjoy direct views of the hotel pool from this deluxe room on the 4th floor of our San Francisco property. The room is elegantly furnished with two full-size beds and includes a private bathroom with a rain shower and quality bath amenities. Large windows let in plenty of daylight and offer glimpses of the outdoor pool area, where guests can sunbathe, swim laps, or unwind at the poolside bar. The room includes blackout curtains, a mini fridge, and a safe for storing valuables. Free high-speed internet and cable TV ensure that guests stay connected and entertained throughout their stay. The proximity to the pool makes this room especially popular during summer months, and it's also close to the hotel gym and spa facilities. Whether you're here for leisure or business, this deluxe room offers a refreshing and convenient place to stay.",
            "total_space": 38.5,
            "image": "image6.txt",
            "capacity": 2
        },
        {
            "type": RoomType.DELUXE.value,
            "price": 520,
            "beds": 3,
            "bedrooms": 2,
            "bathes": 1,
            "floor": 10,
            "area": RoomAreas.TERRACE_VIEW.value,
            "has_sauna": False,
            "has_jacuzzi": True,
            "description": "This deluxe terrace-view room on the 10th floor of our San Francisco hotel offers exclusive access to a private terrace with stunning cityscape views. The room features two bedrooms: one with a king-sized bed and another with a single bed, making it suitable for families or small groups. The shared bathroom includes a jacuzzi tub, a rainfall shower, and premium skincare products for a spa-like experience. The terrace is furnished with lounge chairs and a small table, allowing guests to dine al fresco or simply enjoy the fresh air. Inside, the room is equipped with modern conveniences such as a smart TV, high-speed Wi-Fi, a mini-bar, and blackout curtains for uninterrupted sleep. Room service is available until late evening, and valet parking is offered for those arriving by car. This deluxe room is ideal for guests who want to combine luxury with outdoor enjoyment in the heart of San Francisco.",
            "total_space": 42.0,
            "image": "image7.txt",
            "capacity": 3
        },

        # Standard (5)
        {
            "type": RoomType.STANDARD.value,
            "price": 200,
            "beds": 1,
            "bedrooms": 1,
            "bathes": 1,
            "floor": 1,
            "area": RoomAreas.SIDE_VIEW.value,
            "has_sauna": False,
            "has_jacuzzi": False,
            "description": "Our basic standard room on the 1st floor offers a simple yet comfortable stay for solo travelers or budget-conscious guests visiting San Francisco. The single-bed room includes a cozy mattress, a wardrobe, and a compact writing desk, making it suitable for short-term stays or business trips. The private bathroom features a walk-in shower and standard toiletries. While modest in size, the room is clean, quiet, and efficiently laid out to maximize available space. Guests have access to free Wi-Fi, cable TV, and a continental breakfast included in the rate. Although the view is inward-facing, the room is well-lit and maintained to ensure guest satisfaction. Located near public transportation and key attractions, this room provides excellent value for those who prefer spending more time exploring the city than staying indoors.",
            "total_space": 25.0,
            "image": "image8.txt",
            "capacity": 1
        },
        {
            "type": RoomType.STANDARD.value,
            "price": 220,
            "beds": 1,
            "bedrooms": 1,
            "bathes": 1,
            "floor": 2,
            "area": RoomAreas.SIDE_VIEW.value,
            "has_sauna": False,
            "has_jacuzzi": False,
            "description": "This budget-friendly standard room on the 2nd floor overlooks the hotel’s internal courtyard, offering a tranquil setting away from the noise of the street. Designed for solo travelers or those needing a temporary base, the room features a single bed, a small closet, and a compact workspace. The en-suite bathroom includes a basic shower setup and essential toiletries. The room is equipped with a television, a phone, and wireless internet access to keep guests connected. Daily housekeeping ensures cleanliness, and guests can enjoy a complimentary hot beverage station in the lobby each morning. The location is conveniently near bus stops and train stations, making it easy to explore San Francisco without breaking the bank. While not extravagant, this room delivers everything needed for a no-frills, efficient stay.",
            "total_space": 25.0,
            "image": "image9.txt",
            "capacity": 1
        },
        {
            "type": RoomType.STANDARD.value,
            "price": 210,
            "beds": 1,
            "bedrooms": 1,
            "bathes": 1,
            "floor": 3,
            "area": RoomAreas.STREET_VIEW.value,
            "has_sauna": False,
            "has_jacuzzi": False,
            "description": "Located on the 3rd floor, this standard room faces the street and offers a glimpse of San Francisco’s lively urban life. It's a compact but functional space designed for single occupancy, with a full-sized bed, a nightstand, and a small dresser. The private bathroom is equipped with a shower and standard hygiene supplies. Despite its modest price, the room includes essential amenities such as a flat-screen TV, free Wi-Fi, and climate control for added comfort. Sound-insulated windows help reduce traffic noise, allowing for a relatively peaceful night's sleep. Guests also have access to vending machines and laundry facilities on-site. Ideal for backpackers, students, or short-term visitors, this room provides a practical and affordable accommodation option in a prime city location.",
            "total_space": 24.0,
            "image": "image10.txt",
            "capacity": 1
        },
        {
            "type": RoomType.STANDARD.value,
            "price": 230,
            "beds": 2,
            "bedrooms": 1,
            "bathes": 1,
            "floor": 4,
            "area": RoomAreas.SIDE_VIEW.value,
            "has_sauna": False,
            "has_jacuzzi": False,
            "description": "This double occupancy standard room on the 4th floor is perfect for couples or friends traveling together on a budget. The room features two full-sized beds arranged to provide ample personal space for each guest. The single bathroom includes a basic shower and necessary toiletries. Despite its simplicity, the room is clean and well-maintained, with a small work desk and a luggage rack for convenience. Entertainment options include a cable TV and free Wi-Fi, ensuring guests remain entertained and connected. The side-facing window offers a partial view of the hotel grounds and nearby buildings. This room is particularly popular among travelers attending conferences or events in San Francisco who need a place to rest without overspending. It strikes a balance between affordability and comfort, making it a solid choice for shared stays.",
            "total_space": 26.0,
            "image": "image11.txt",
            "capacity": 2
        },
        {
            "type": RoomType.STANDARD.value,
            "price": 190,
            "beds": 1,
            "bedrooms": 1,
            "bathes": 1,
            "floor": 1,
            "area": RoomAreas.SIDE_VIEW.value,
            "has_sauna": False,
            "has_jacuzzi": False,
            "description": "The smallest room in our San Francisco hotel, this single-person standard room is designed for solo travelers who prioritize cost over luxury. It features a single full-sized bed, a wall-mounted lamp, and minimal furniture to conserve space. The en-suite bathroom is compact but sufficient, with a standing shower and basic hygiene items. Amenities include a portable alarm clock, a mirror, and a single electrical outlet for charging devices. The room does not include a TV, but Wi-Fi is available throughout the hotel premises. Despite its size, the room is warm and welcoming, offering a quiet retreat after a long day of sightseeing or meetings. Its low price point and central location make it an excellent option for budget travelers, digital nomads, or those who spend most of their time outdoors exploring the city.",
            "total_space": 22.0,
            "image": "image12.txt",
            "capacity": 1
        }
    ]
    for room_data in rooms:
        image = room_data.pop("image")
        image_path = os.path.join(folder_path, image)

        print(f"Trying to load: {image_path}")

        if os.path.exists(image_path):
            base64_image = read_base64_from_file(image_path)
            print(f"Loaded: {image}")
        else:
            print(f"File NOT found: {image}")
            continue

        room_data["image"] = base64_image
        room_instance = RoomBase(**room_data)

        async with unit_of_work:
            await unit_of_work.room.create(room_instance)


async def main():
    folder_path = "C:\\Users\\User\\Desktop\\hotel-rooms"  #
    await populate_properties_with_images(folder_path)


if __name__ == "__main__":
    asyncio.run(main())
