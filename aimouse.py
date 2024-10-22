# Import necessary libraries
import cv2  # OpenCV for image processing
from cvzone.HandTrackingModule import HandDetector  # Hand detection module from CVZone
import mouse  # Mouse control library
import threading  # For handling multiple threads
import numpy as np  # NumPy for numerical operations
import time  # For time-related functions

# Constants for camera settings and frame dimensions
frameR = 100  # Margin for the rectangle frame
cam_w, cam_h = 640, 480  # Camera width and height

# Initialize video capture from the camera
cap = cv2.VideoCapture(0)
cap.set(3, cam_w)  # Set camera width
cap.set(4, cam_h)  # Set camera height

# Initialize the hand detector
detector = HandDetector(detectionCon=0.9, maxHands=1)

# Variables for click delays
l_delay = 0
r_delay = 0
double_delay = 0

# Function to handle left click delay
def l_clk_delay():
    global l_delay
    time.sleep(1)
    l_delay = 0

# Function to handle right click delay
def r_clk_delay():
    global r_delay
    time.sleep(1)
    r_delay = 0

# Function to handle double click delay
def double_clk_delay():
    global double_delay
    time.sleep(2)
    double_delay = 0

# Start threads for handling click delays
l_clk_thread = threading.Thread(target=l_clk_delay)
r_clk_thread = threading.Thread(target=r_clk_delay)
double_clk_thread = threading.Thread(target=double_clk_delay)

# Main loop for processing video feed
while True:
    success, img = cap.read()  # Read a frame from the camera
    if success:
        img = cv2.flip(img, 1)  # Flip the image horizontally
        hands, img = detector.findHands(img, flipType=False)  # Detect hands in the image
        cv2.rectangle(img, (frameR, frameR), (cam_w - frameR, cam_h - frameR), (255, 0, 255), 2)  # Draw a rectangle for the interaction area
        
        if hands:
            lmlist = hands[0]['lmList']  # Get the landmark list for the detected hand
            ind_x, ind_y = lmlist[8][0], lmlist[8][1]  # Index finger coordinates
            mid_x, mid_y = lmlist[12][0], lmlist[12][1]  # Middle finger coordinates
            
            # Draw circles on the detected fingers
            cv2.circle(img, (ind_x, ind_y), 5, (0, 255, 255), 2)
            cv2.circle(img, (mid_x, mid_y), 5, (0, 255, 255), 2)

            fingers = detector.fingersUp(hands[0])  # Get the state of the fingers

            # Mouse movement
            if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 1:  # Index finger up, middle finger down
                conv_x = int(np.interp(ind_x, (frameR, cam_w - frameR), (0, 1536)))  # Convert x-coordinate
                conv_y = int(np.interp(ind_y, (frameR, cam_h - frameR), (0, 864)))  # Convert y-coordinate
                mouse.move(conv_x, conv_y)  # Move the mouse cursor
                print(conv_x, conv_y)  # Print the coordinates

            # Mouse Button Clicks
            if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 1:  # All fingers up
                if abs(ind_x - mid_x) < 25:  # Check if index and middle fingers are close
                    # Left Click
                    if fingers[4] == 0 and l_delay == 0:  # Left click with no delay
                        mouse.click(button="left")
                        l_delay = 1
                        l_clk_thread.start()  # Start the left click delay thread
                    # Right Click
                    if fingers[4] == 1 and r_delay == 0:  # Right click with no delay
                        mouse.click(button="right")
                        r_delay = 1
                        r_clk_thread.start()  # Start the right click delay thread

            # Mouse Scrolling
            if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 0:  # Index and middle fingers up, others down
                if abs(ind_x - mid_x) < 25:
                    mouse.wheel(delta=-1)  # Scroll down
            if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 1:  # Index and middle fingers up, ring finger up
                if abs(ind_x - mid_x) < 25:
                    mouse.wheel(delta=1)  # Scroll up

            # Double Mouse Click
            if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 0 and fingers[4] == 0 and double_delay == 0:  # Only index finger up
                double_delay = 1
                mouse.double_click(button="left")  # Perform a double-click
                double_clk_thread.start()  # Start the double-click delay thread

        # Display the processed image
        cv2.imshow("Camera Feed", img)
        cv2.waitKey(1)  # Wait for a short period to control the frame rate
