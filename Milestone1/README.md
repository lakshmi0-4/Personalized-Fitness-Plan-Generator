FitPlan AI - Personalized Fitness Plan Generator (Milestone 1)

Objective
The objective of this milestone is to develop a basic Streamlit web application that collects user fitness details and calculates BMI (Body Mass Index) with proper category classification.

Input Fields Implemented:

Personal Information

* Name (Required)
* Height in centimeters (Required)
* Weight in kilograms (Required)

Fitness Details

* Fitness Goal (Build Muscle, Weight Loss, Strength Gain, Abs Building, Flexible)
* Available Equipment (Multiple selection allowed using checkboxes)
* Fitness Level (Beginner, Intermediate, Advanced)

---

BMI Formula Used:
BMI is calculated using the formula:

BMI = weight (kg) / (height (m))^2

Height is converted from centimeters to meters using:

height (m) = height (cm) / 100

BMI is rounded to 2 decimal places.


BMI Categories:

* Underweight: BMI < 18.5
* Normal: 18.5 ≤ BMI < 25
* Overweight: 25 ≤ BMI < 30
* Obese: BMI ≥ 30



Steps Performed:

1. Created a Streamlit form for user input.
2. Implemented input validation (no empty name, no zero/negative height and weight).
3. Converted height from cm to meters.
4. Calculated BMI and rounded it to 2 decimals.
5. Classified BMI into standard health categories.
6. Displayed user name, BMI value, BMI category, and fitness details.



Technologies Used:

* Python
* Streamlit
* GitHub
* Hugging Face Spaces


Hugging Face Space Link:
https://huggingface.co/spaces/LakshmiNandaS/Fitness


Screenshots:
Screenshots of the running application are available inside the screenshots/ folder.


