import os
import cv2  # Import OpenCV for capturing image
import base64
import re
from groq import Groq
from pymongo import MongoClient  # Import MongoDB client
from datetime import datetime  # To log timestamps
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from dateutil import parser

client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI if hosted remotely
db = client["Flipkart"]  # Database name
collection = db["extracted_data"]  # Collection name

# Initialize Groq client
client = Groq(
    api_key=os.getenv('GROQ_API_KEY')
)

upload_folder = "static/upload"

def encode_image(image_path):
    """Convert an image to base64 format."""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8') # This now calls the function to capture an image

# If an image was successfully captured, proceed with processing
def extract_info_from_image(encoded_image):
    """Extract product info from the image using Groq API."""
    prompt_template = """
    Please extract the following details from the image provided and present them in a dictionary format with key-value pairs. Ensure the dictionary contains only the specified fields.
    - **Product Name**
    - **Packaging Material**
    - **Brand Name**
    - **Pack Size**
    - **Expiry Date**
    - **Expiry Date (valid/expired)**
    - **Count Confirmation**
    - **MRP**
    - **Shelf Life Prediction (if applicable)**
    """

    completion = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_template},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            }
        ],
        temperature=0,
        max_tokens=512
    )

    # Extract key-value pairs from response
    info = completion.choices[0].message.content.strip()
    extracted_info = {}
    for line in info.splitlines():
        match = re.match(r"\*\s*\*\*(.*?)\*\*\s*:\s*(.*)", line)
        if match:
            key, value = match.group(1).strip(), match.group(2).strip()
            extracted_info[key] = value

    return extracted_info

# Function for generating the comparison prompt
def generate_comparison_prompt(user_info_str, extracted_info_str):
    prompt = (
        "You are tasked with comparing two sets of product information to determine whether they describe the **same product**. "
        "Focus on the following criteria: product name, brand name, packaging material, expiry date, and other attributes. "
        "Do not consider price as a major factor for this decision, as it may vary due to offers or discounts. "
        "Minor variations in names or formats (e.g., abbreviations or slight differences) are acceptable if they do not change the essence of the product. "
        "Here are the two sets of product data:\n\n"
    )

    # Adding Extracted Product Information
    prompt += "### Extracted Product Information:\n"
    prompt += extracted_info_str + "\n"

    # Adding User Product Information
    prompt += "\n### User Product Information:\n"
    prompt += user_info_str + "\n"

    # Instructions for comparison
    prompt += "\n### Task:\n"
    prompt += (
        "For each field, compare the two values and determine whether they represent the same product information. "
        "Return 'Same' if the field values suggest they refer to the same product, 'Not the Same' if they do not, and 'Close but Needs Clarification' if there is ambiguity. "
        "Provide an explanation for each field comparison. After comparing all fields, provide an overall conclusion on whether the two sets of information represent the same product or not.\n"
    )

    prompt += "### Example Format for Each Field Comparison:\n"
    prompt += "'Field Name: Same/Not the Same/Close but Needs Clarification (Extracted: <extracted_value>, User: <user_value>)'.\n"

    return prompt

# Function for running the comparison using Groq
def compare_product_info(user_info_str, extracted_info_str):
    groq_api_key = os.getenv('GROQ_API_KEY')  
    model_name = "gemma-7b-it" 

    # Initialize the ChatGroq instance
    groq = ChatGroq(groq_api_key=groq_api_key, model_name=model_name)

    # Generate the comparison prompt using the user and extracted information
    prompt = generate_comparison_prompt(user_info_str, extracted_info_str)

    # Send the prompt to the Groq model and receive the response
    response = groq([HumanMessage(content=prompt)])

    # Return the response from the model
    return response.content  # Assuming content has the result we need

# Normalize expiry date to prevent false mismatches
def normalize_expiry_date(expiry_date_str):
    # Use regex to extract the month and year
    match = re.search(r'(\d{1,2})/?(\d{2,4})', expiry_date_str)
    if match:
        month = match.group(1)
        year = match.group(2)

        # Normalize to a common format (MM/YYYY)
        if len(year) == 2:  # If the year is in YY format
            year = '20' + year  # Assume it's 21st century
        return f"{month.zfill(2)}/{year}"
    return expiry_date_str  # Return the original string if no match

# Simplified final verdict function
def final_verdict(user_info, extracted_info, comparison_result):
    # Normalize expiry dates to avoid mismatches
    extracted_expiry = normalize_expiry_date(extracted_info.get("Expiry Date", ""))
    user_expiry = normalize_expiry_date(user_info.get("Expiry Date", ""))

    # Adjust comparison result for expiry dates if needed
    if extracted_expiry != user_expiry:
        comparison_result = comparison_result.replace(
            "Expiry Date: Not the Same", 
            f"Expiry Date: Same (Extracted: {extracted_expiry}, User: {user_expiry})"
        )

    # Handle minor discrepancies in MRP
    extracted_mrp_str = extracted_info.get("MRP", "0").replace("₹", "").strip()
    user_mrp_str = user_info.get("MRP", "0").replace("₹", "").strip()

    # Convert strings to float safely
    extracted_mrp = float(extracted_mrp_str) if extracted_mrp_str.isnumeric() else 0.0
    user_mrp = float(user_mrp_str) if user_mrp_str.isnumeric() else 0.0
    # Adjust comparison result for MRP if needed
    # Allow tolerance for MRP difference
    if abs(extracted_mrp - user_mrp) < 10:
        comparison_result = comparison_result.replace(
            "MRP: Not the Same", 
            f"MRP: Same  (Extracted: ₹{extracted_mrp}, User: ₹{user_mrp})"
        )

    # Final determination: Check if "Not the Same" appears in the comparison result
    if "Not the Same" in comparison_result:
        return "Disapproved"
    else:
        return "Approved"
##you can provide other user_info_list too 
user_info_list = [
    
    {
        "product_name": "Skin Fruits Active Bright Body Lotion",
        "packaging_material": "Plastic Bottle",
        "brand_name": "Joy",
        "pack_size": "300 mL",
        "expiry_date": "09/23",
        "expiry_status": "Expired",
        "count_confirmation": 1,
        "mrp": 270.00,
        "shelf_life_prediction": "Expired"
    },
    {
    "Product Name": "Yardley London Imperial Jasmine Talcum Powder",
    "Packaging Material": "Plastic",
    "Brand Name": "Yardley London",
    "Pack Size": "100g",
    "Expiry Date": "09/2026",
    "Expiry Date (valid/expired)": "Valid",
    "Count Confirmation": "1",
    "MRP": "₹150",
    "Shelf Life Prediction": "Not applicable",
    "Batch NO": "123456"},
    {
    "Product_Name": "Khadi Natural Sandalwood Soap",
    "Packaging_Material": "Plastic Wrap",
    "Brand_Name": "Khadi Natural",
    "Pack_Size": "125g (4.41 oz)",
    "Expiry_Date": "July 2026",
    "Expiry_Date_Status": "Valid",
    "Count_Confirmation": "Single Unit",
    "MRP": "₹70.00",
    "Shelf_Life_Prediction": "36 months from the manufacturing date"
    },
    {
        "product_name": "Tata Salt Himalayan Rock Salt",
        "packaging_material": "Plastic Pouch",
        "brand_name": "Tata Salt",
        "pack_size": "1 kg",
        "expiry_date": "05/26",
        "expiry_status": "Valid",
        "count_confirmation": 1,
        "mrp": 28.00,
        "shelf_life_prediction": "Valid till May 2026"
    }
]
# Get the list of image files in the upload folder
image_files = os.listdir(upload_folder)

if len(image_files) != len(user_info_list):
    raise ValueError("Mismatch: Number of images and user information entries must be equal.")

# Example usage:
for image_file, user_info in zip(image_files, user_info_list):
    image_path = os.path.join(upload_folder, image_file)
    encoded_image = encode_image(image_path)

    # Extract product info from the image
    extracted_info = extract_info_from_image(encoded_image)

    # Generate comparison result using Groq
    user_info_str = "\n".join([f"{key}: {value}" for key, value in user_info.items()])
    extracted_info_str = "\n".join([f"{key}: {value}" for key, value in extracted_info.items()])

    comparison_result = compare_product_info(user_info_str, extracted_info_str)

    # Call final_verdict with the required arguments
    final_result = final_verdict(user_info, extracted_info, comparison_result)

    # Insert the document into MongoDB
    document = {
        "image_file": image_file,
        "extracted_info": extracted_info,
        "user_info": user_info,
        "final_result": final_result,
        "timestamp": datetime.now()
    }
    collection.insert_one(document)
    print(f"Processed {image_file}: {final_result}")

print("All images processed and results stored in MongoDB.")
