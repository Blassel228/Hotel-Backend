# import os
# import asyncio  # Added for async functionality
#
# from app.utils.unitofwork import UnitOfWork  # No changes to imports
# from app.schemas.property import PropertyBase  # No changes to imports
#
# # Instantiate ABCUnitOfWork instead of assigning the class itself
# unit_of_work = UnitOfWork()  # Changed: Create an instance of ABCUnitOfWork
#
#
# def read_base64_from_file(file_path):
#     """Reads a Base64 string from a .txt file."""
#     with open(file_path, "r") as f:
#         return f.read().strip()  # Strip any extra whitespace or newlines
#
#
# # Changed the function to be asynchronous and added comments for clarity
# async def populate_properties_with_images(folder_path):
#     """Populates the Property table with data and Base64 images."""
#     # Mock data for properties (unchanged)
#     properties = [
#         {
#             "type": "Hotel",
#             "price": 500,
#             "address": "123 Beach Road, Miami, FL",
#             "bedrooms": 10,
#             "bathrooms": 15,
#             "area": "Downtown Miami",
#             "floor": 5,
#             "parking_spots": 20,
#             "total_space": "20,000 sq ft",
#             "contract_status": "Available",
#             "payment_process": "Online Payment Accepted",
#             "safety_feature": "24/7 Security System",
#             "image": "image1.txt",  # File name for the Base64 image
#         },
#         {
#             "type": "Resort",
#             "price": 1000,
#             "address": "456 Mountain View, Aspen, CO",
#             "bedrooms": 5,
#             "bathrooms": 7,
#             "area": "Aspen Valley",
#             "floor": 3,
#             "parking_spots": 10,
#             "total_space": "10,000 sq ft",
#             "contract_status": "Pending",
#             "payment_process": "Bank Transfer Only",
#             "safety_feature": "Fire Extinguishers Installed",
#             "image": "image3.txt",
#         },
#         {
#             "type": "Villa",
#             "price": 750,
#             "address": "789 Sunset Blvd, Los Angeles, CA",
#             "bedrooms": 3,
#             "bathrooms": 4,
#             "area": "Hollywood Hills",
#             "floor": 2,
#             "parking_spots": 5,
#             "total_space": "5,000 sq ft",
#             "contract_status": "Booked",
#             "payment_process": "Credit Card Accepted",
#             "safety_feature": "CCTV Surveillance",
#             "image": "image4.txt",
#         },
#         {
#             "type": "Apartment",
#             "price": 300,
#             "address": "101 Park Ave, New York, NY",
#             "bedrooms": 2,
#             "bathrooms": 1,
#             "area": "Midtown Manhattan",
#             "floor": 10,
#             "parking_spots": 0,
#             "total_space": "1,200 sq ft",
#             "contract_status": "Available",
#             "payment_process": "PayPal Accepted",
#             "safety_feature": "Smoke Detectors",
#             "image": "image5.txt",
#         },
#         {
#             "type": "Cabin",
#             "price": 200,
#             "address": "202 Forest Lane, Denver, CO",
#             "bedrooms": 1,
#             "bathrooms": 1,
#             "area": "Rocky Mountains",
#             "floor": 1,
#             "parking_spots": 2,
#             "total_space": "800 sq ft",
#             "contract_status": "Available",
#             "payment_process": "Cash Only",
#             "safety_feature": "First Aid Kit",
#             "image": "image6.txt",
#         },
#         {
#             "type": "Hotel",
#             "price": 600,
#             "address": "303 Ocean Drive, San Diego, CA",
#             "bedrooms": 12,
#             "bathrooms": 16,
#             "area": "La Jolla",
#             "floor": 8,
#             "parking_spots": 25,
#             "total_space": "25,000 sq ft",
#             "contract_status": "Booked",
#             "payment_process": "Online Payment Accepted",
#             "safety_feature": "Emergency Exit Plan",
#             "image": "image7.txt",
#         },
#         {
#             "type": "Resort",
#             "price": 1200,
#             "address": "404 Palm Tree Blvd, Honolulu, HI",
#             "bedrooms": 8,
#             "bathrooms": 10,
#             "area": "Waikiki Beach",
#             "floor": 4,
#             "parking_spots": 15,
#             "total_space": "15,000 sq ft",
#             "contract_status": "Available",
#             "payment_process": "Credit Card Accepted",
#             "safety_feature": "Lifeguards on Duty",
#             "image": "image8.txt",
#         },
#         {
#             "type": "Villa",
#             "price": 900,
#             "address": "505 Hillside Drive, Santa Barbara, CA",
#             "bedrooms": 4,
#             "bathrooms": 5,
#             "area": "Montecito",
#             "floor": 2,
#             "parking_spots": 6,
#             "total_space": "6,000 sq ft",
#             "contract_status": "Pending",
#             "payment_process": "Wire Transfer",
#             "safety_feature": "Gated Community",
#             "image": "image9.txt",
#         },
#         {
#             "type": "Apartment",
#             "price": 400,
#             "address": "606 Riverfront Ave, Chicago, IL",
#             "bedrooms": 3,
#             "bathrooms": 2,
#             "area": "The Loop",
#             "floor": 15,
#             "parking_spots": 1,
#             "total_space": "1,500 sq ft",
#             "contract_status": "Available",
#             "payment_process": "Debit Card Accepted",
#             "safety_feature": "Security Cameras",
#             "image": "image10.txt",
#         },
#         {
#             "type": "Cabin",
#             "price": 150,
#             "address": "707 Lakeview Rd, Seattle, WA",
#             "bedrooms": 1,
#             "bathrooms": 1,
#             "area": "Lake Washington",
#             "floor": 1,
#             "parking_spots": 1,
#             "total_space": "900 sq ft",
#             "contract_status": "Available",
#             "payment_process": "Cash Only",
#             "safety_feature": "Fireplace Safety",
#             "image": "image11.txt",
#         },
#     ]
#
#     for prop_data in properties:
#         image = prop_data.pop("image")  # Extract the image file name
#         image_path = os.path.join(folder_path, image)  # Build the full file path
#
#         if os.path.exists(image_path):
#             base64_image = read_base64_from_file(image_path)  # Read Base64 string
#         else:
#             print(f"File not found: {image_path}")
#             base64_image = None
#         prop_data["image"] = base64_image
#         property_instance = PropertyBase(**prop_data)
#
#         # Ensure the unit of work is used asynchronously
#         async with unit_of_work:
#             await unit_of_work.property.create(property_instance)
#
#
# # Added an async wrapper function to run the script
# async def main():
#     folder_path = "C:\\Users\\User\\Desktop\\iamges1"  #
#     await populate_properties_with_images(folder_path)
#
#
# if __name__ == "__main__":
#     # Run the async main function using asyncio
#     asyncio.run(main())
