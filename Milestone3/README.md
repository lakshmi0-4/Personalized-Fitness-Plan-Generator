# Milestone 3: Login System with OTP Verification 🔐

## 📌 Project Overview
The objective of this milestone was to implement a robust authentication and verification layer for the **FitPlan AI** application. To ensure a professional and secure user experience, the system now features database-backed credentials and mandatory 2-Factor Authentication (2FA) via Email OTP before granting access to the personalized fitness dashboard.

## 🛠️ Key Features Implemented
* **User Signup & Registration**: A dedicated Signup page allows new users to securely register their accounts using an Email ID and Password.
* **Database Management**: Integration of a backend database to securely store, retrieve, and verify user credentials and profile settings.
* **Professional Login Interface**: A sleek, split-screen Login page featuring a high-contrast design with a red-tinted gym background on the left and a clean white form on the right.
* **6-Digit OTP Generation**: Upon successful password verification, the system automatically generates a unique, time-sensitive 6-digit One-Time Password (OTP).
* **Automated Email Integration**: The generated OTP is instantly dispatched to the user's registered email address for identity verification.
* **OTP Verification Gate**: A secondary security page where users must enter the correct code to unlock access to their personalized fitness tools.
* **Restricted Dashboard Access**: The main application dashboard is strictly locked until the user successfully completes the OTP verification process.

## 📁 Repository Structure
The project is organized into a modular structure to handle authentication, multi-page navigation, and AI processing:

### Core Files
* **`app.py`**: The main entry point for the Streamlit application.
* **`auth_token.py`**: Handles security tokens and session management.
* **`model_api.py`**: Contains logic for querying the AI model for workout generation.
* **`prompt_builder.py`**: Logic to construct detailed 8-argument prompts for personalized plans.
* **`requirements.txt`**: List of dependencies required to run the application.
* **`Dockerfile`**: Configuration for containerized deployment.

### Multi-Page Dashboard (`/pages`)
* **`1_Profile.py`**: Handles Section 1 (User Details) and Section 2 (Goals & Equipment).
* **`2_Workout_Plan.py`**: Handles Section 3 (Generated 5-day output).

## 🚀 Live Demo
You can interact with the live version of this application on Hugging Face Spaces:

**Hugging Face Live Link:** 
https://huggingface.co/spaces/LakshmiNandaS/FitPlanAI_PLAN_A

---

## Implementation Screenshots

### 1. Login Interface
<img width="1896" height="865" alt="image" src="https://github.com/user-attachments/assets/e3c805e3-0131-422c-a85a-e54d47b5307c" />


### 2. OTP Verification Screen
<img width="1896" height="866" alt="image" src="https://github.com/user-attachments/assets/4c0aadb2-f28a-4e6e-a568-ed4d5869bc64" />
<img width="1900" height="869" alt="image" src="https://github.com/user-attachments/assets/1b1ecf25-4a60-4b74-b581-a4725e61debd" />
<img width="1476" height="648" alt="image" src="https://github.com/user-attachments/assets/3c7c8d36-2dcc-42b2-a4b9-a92e3b74037b" />


### 3. Successful Account Creation
<img width="1895" height="862" alt="image" src="https://github.com/user-attachments/assets/b87a6f07-74c8-41ac-a991-a3f12a51c7d9" />


### 4. Athlete Profile Setup 
After verification, users provide details (Name, Gender, Age, Weight, Height) and set their fitness goals and available equipment.
<img width="1899" height="861" alt="image" src="https://github.com/user-attachments/assets/f7355475-b8eb-43ea-b31f-b41897074aee" />



### 5. Generated Workout Plan
<img width="1890" height="841" alt="image" src="https://github.com/user-attachments/assets/3b8d2d08-505a-41a2-b386-4c90be084d27" />
<img width="1891" height="864" alt="image" src="https://github.com/user-attachments/assets/9a9f60df-aad4-4836-bbab-cb7a92d8043f" />



---
**FitPlan AI** - *Your Personalized Fitness Journey Starts Here.*
