# Flipkart Grid 6.0 - Smart Vision Technology Quality Control

This project implements a smart vision technology solution for quality control in e-commerce product management. It utilizes advanced image processing and artificial intelligence (AI) to compare product information extracted from images against user-provided data, ensuring that the products listed on e-commerce platforms meet quality standards.

## Project Structure

```
.
├── static
│   ├── css
│   │   └── style.css
│   ├── img
│   └── upload
├── templates
│   └── bill.html
├── app.py
├── camera.py
├── compare_info.py
└── README.md
```

## Files Description

- `app.py`: Flask application for web interface.
- `camera.py`: Handles image capture functionality.
- `compare_info.py`: Main script for comparing extracted information with user data.
- `static/css/style.css`: CSS styles for the web interface.
- `static/upload/`: Directory for storing product images captured from the `camera.py`.
- `templates/bill.html`: HTML template for displaying results.

## Features

- Image capture and processing
- Text extraction from images using AI
- Comparison of extracted data with user-provided information
- MongoDB integration for data storage
- Web interface for displaying results

## Extracted Information

The vision model extracts the following information from product images:

- Product Name
- Packaging Material
- Brand Name
- Pack Size
- Expiry Date
- Expiry Date Status (valid/expired)
- Count Confirmation
- Maximum Retail Price (MRP)
- Shelf Life Prediction (if applicable)

## Technologies Used

1. **Python**: The primary programming language used for scripting and implementation.
2. **OpenCV**: A computer vision library used for image processing and capturing images.
3. **Groq**: A machine learning model provider used for product information extraction and comparison. In this project, the following models are employed:
   - **Llama-3.2-11b-vision-preview**: Used for extracting product information from images.
   - **Gemma-7b-it**: Used for comparing product information based on extracted and user-provided details.
4. **MongoDB**: A NoSQL database used for storing extracted data, user information, and comparison results.
5. **Langchain**: A framework that facilitates the integration of various components, allowing for easier interaction with the Groq API.
6. **Flask**: A lightweight web framework used for creating the user interface and handling web requests.

## Setup and Installation

1. Clone the repository
2. Install required dependencies: `pip install -r requirements.txt`
3. Set up MongoDB and update the connection string in `compare_info.py`
4. Obtain a Groq API key and update it in `compare_info.py`

## Usage

1. Run `app.py` to start the Flask server
2. Upload product images through the web interface
3. Enter product information for comparison
4. View results of the quality control check

## Note

Ensure that the Groq API key and MongoDB connection details are kept secure and not shared publicly.

## Contributors

[Your Name/Team Members]

## License

[Specify your license here]
