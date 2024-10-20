import cv2
import time
import os

# Ensure the 'static/upload' folder exists
save_folder = "static/upload"
os.makedirs(save_folder, exist_ok=True)

# Initialize the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Define rectangle dimensions (you can adjust as needed)
rect_x, rect_y = 200, 100   # Top-left corner of the rectangle
rect_w, rect_h = 240, 320   # Width and height of the rectangle

# Track time for capturing images every 5 seconds
last_capture_time = time.time()

print("Press 'Ctrl + C' to exit the script.")

try:
    while True:
        # Read the frame from the webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Draw the static rectangle on the frame
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), (0, 255, 0), 2)

        # Get the current time
        current_time = time.time()

        # Check if 5 seconds have passed since the last capture
        if current_time - last_capture_time >= 5:
            # Crop the region inside the rectangle
            cropped_img = frame[rect_y:rect_y + rect_h, rect_x:rect_x + rect_w]

            # Generate a unique filename with the timestamp
            filename = f"{int(current_time)}.jpg"
            filepath = os.path.join(save_folder, filename)

            # Save the image
            cv2.imwrite(filepath, cropped_img)
            print(f"Image saved: {filepath}")

            # Update the last capture time
            last_capture_time = current_time

        # Optional: Small delay to reduce CPU usage
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nScript terminated by user.")

finally:
    # Release the webcam resource
    cap.release()
    print("Webcam released.")
