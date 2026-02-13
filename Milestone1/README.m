FitPlan AI - Personalized Fitness Plan Generator (Milestone 1)

Objective:
The objective of Milestone 1 is to build a basic Streamlit web application that collects user fitness details and calculates BMI (Body Mass Index). This milestone focuses on creating the user interface, collecting user input, validating input values, and displaying BMI results with proper category classification.

Features Implemented:

* User-friendly fitness profile form using Streamlit
* Collects user personal details:
  * Name
  * Height (cm)
  * Weight (kg)
* Collects fitness details:
  * Fitness Goal
  * Available Equipment (multiple selection)
  * Fitness Level
* Calculates BMI using the BMI formula
* Displays BMI value and category
* Input validation to avoid empty or invalid values

BMI Formula Used
BMI is calculated using the formula:
BMI = weight (kg) / (height in meters)²

Height is converted from centimeters to meters before calculation:
height (m) = height (cm) / 100

BMI is rounded to two decimal places.

BMI Categories
The BMI categories are classified as:

* Underweight: BMI < 18.5
* Normal: 18.5 ≤ BMI < 25
* Overweight: 25 ≤ BMI < 30
* Obese: BMI ≥ 30

Steps Performed

1. Created a Streamlit application interface.
2. Designed the fitness profile form using Streamlit form elements.
3. Added input fields for name, height, and weight.
4. Added dropdown and checkbox selections for fitness goal and equipment.
5. Added radio selection for fitness level.
6. Implemented BMI calculation logic.
7. Displayed BMI result and category.
8. Added validation for required fields (no empty values and no zero/negative inputs).
9. Deployed the application on Hugging Face Spaces.

Technologies Used

* Python
* Streamlit
* Hugging Face Spaces
* GitHub

Hugging Face Deployment Link

https://huggingface.co/spaces/LakshmiNandaS/Fitness
