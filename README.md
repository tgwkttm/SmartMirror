# SmartMirror
Smart Mirror with facial recognition and emotion detection. 

## Project Overview

This project is a Smart Mirror with facial recognition and emotion detection. The application allows users to log in using facial recognition, manage notes, view calendar events, and display detected emotions.

## Deliverables

This README file describes the deliverables of the project, including:

The GitLab repository containing the entire source code (without compiled binaries).

Steps to build the application.

Steps to install and launch the application.

## GitLab Repository

Repository Address:

https://github.com/tgwkttm/SmartMirror

This repository contains the entire source code except for compiled binaries.

## System Requirements

Raspberry Pi 4

Pi Camera

Arduino Uno

DHT11 (temperature and humidity sensor)

MQ135 (air quality sensor)

Python 3.7+

## Install Dependencies

## #Virtual Environment

A virtual environment was created using Python 3.11.2 to manage dependencies efficiently.

## #To create and activate the virtual environment:

python3.11 -m venv smartmirror_env
source smartmirror_env/bin/activate  # On macOS/Linux
smartmirror_env\Scripts\activate  # On Windows

### Update system packages:

sudo apt update && sudo apt upgrade -y

### Install Python and pip (if not installed):

sudo apt install python3 python3-pip -y

### Install OpenCV:

pip install opencv-python

Install TensorFlow Lite Runtime:

pip install tflite-runtime

Install other required libraries:

pip install numpy firebase-admin requests picamera2 imutils face-recognition tk tkcalendar psutil

### Firebase Configuration

Download the firebase_config.json file from Firebase Console.

Place the file in the main project directory.

## How to Build and Run

Clone the GitLab repository:

git clone <repository address>
cd <repository name>

### Run the application:

python3 main.py

## How to Use

Login: Users can log in using email & password or facial recognition.

Calendar: Users can add, view, and delete calendar events.

Emotion Detection: The system detects emotions and displays corresponding messages.

Notes: Users can add and manage personal notes.

Air Quality Monitoring: The application reads air quality data using sensors and sends it to ThingSpeak.

Project Structure

main.py - Starts the application

facial_recognition.py - Handles facial recognition

emotion_detector_app.py - Detects emotions

calendar_app.py - Manages calendar events

notes.py - Manages user notes

firebase_config.py - Configures Firebase

firebase_user_manager.py - Handles user accounts in Firebase

thingspeak.py - Sends air quality data to ThingSpeak

train_model.py - Trains the face recognition model

system_usage_test.py - Tests CPU and RAM usage

test_face_recognition.py - Tests the face recognition system

test_firebase_auth.py - Tests Firebase authentication

welcome_window.py - Displays the welcome screen

new_user_window.py - Handles new user registration

existing_user_window.py - Handles existing user login

user_options_window.py - Provides user dashboard and options

## Common Issues & Solutions

### Camera Not Connecting

Make sure the camera drivers are installed:

sudo apt install libcamera-apps

Restart Raspberry Pi.

### Face Not Recognized

Check if encodings.pickle contains data.

Ensure proper lighting conditions.

### Firebase Not Connecting

Ensure firebase_config.json is correct.

Reinstall dependencies:

pip install firebase-admin

## Conclusion

This project is designed to display personalized information on a Smart Mirror using modern facial recognition and AI technologies.

For questions or contributions, please open an issue on the GitLab repository.

