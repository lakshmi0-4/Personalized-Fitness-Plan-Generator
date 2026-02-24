FitPlan AI – Milestone 2

## **Objective**

The objective of Milestone 2 is to integrate a Large Language Model (LLM) into the FitPlan AI application to generate personalized workout plans dynamically based on user fitness inputs collected in Milestone 1.

The application allows users to enter their personal and fitness details and receive an AI-generated 5-day workout plan.

---

## **Model Used**

The application uses the **Mistral-7B-Instruct-v0.2** model from Hugging Face.

The model is accessed using the Hugging Face Inference API through the `huggingface_hub` library.

The model generates structured workout plans based on user fitness inputs.

---

## **Prompt Design Explanation**

A dynamic prompt is created using user inputs collected from the Streamlit interface.

The prompt includes:

* Name
* Age
* BMI Category
* Fitness Goal
* Fitness Level
* Available Equipment

BMI is calculated using the user's height and weight.

The prompt instructs the AI model to generate a structured **5-day workout plan** including exercises with sets and reps.

Example prompt structure:

```
Create a simple 5-day workout plan.

User Info:

Name: Lakshmi
Age: 20
BMI: 23.8 (Normal Weight)
Goal: Strength Gain
Level: Beginner
Equipment: Dumbbells

Day 1:
Exercises with sets and reps

Day 2:
Exercises with sets and reps

Day 3:
Exercises with sets and reps

Day 4:
Exercises with sets and reps

Day 5:
Exercises with sets and reps
```

---

## **Steps Performed**

### **1. Model Loading**

The pre-trained model **Mistral-7B-Instruct-v0.2** was integrated from Hugging Face.

The model is loaded using the Hugging Face Inference API.

Authentication is done using the Hugging Face API token.

---

### **2. Prompt Creation**

User inputs are collected through a Streamlit form interface.

The inputs include:

* Name
* Age
* Gender
* Height
* Weight
* Fitness Goal
* Fitness Level
* Available Equipment

BMI is calculated from height and weight.

A structured prompt is generated using `prompt_builder.py`.

---

### **3. Inference Testing**

The model was tested with multiple user scenarios to ensure proper workout plan generation.

### **Test Scenario 1**

Goal: Weight Loss
Level: Beginner
Equipment: No Equipment

### **Test Scenario 2**

Goal: Strength Gain
Level: Intermediate
Equipment: Dumbbells

### **Test Scenario 3**

Goal: Muscle Building
Level: Advanced
Equipment: Multiple Equipment

The model successfully generated personalized workout plans dynamically.

---

## **Sample Generated Output**

The AI model generates a structured workout plan:

* Day 1 Workout Plan
* Day 2 Workout Plan
* Day 3 Workout Plan
* Day 4 Workout Plan
* Day 5 Workout Plan

Each day includes exercises with sets and repetitions.

---

## **Hugging Face Space Deployment Link**

https://huggingface.co/spaces/LakshmiNandaS/Fitness_2



## **Technologies Used**

* Python
* Streamlit
* Hugging Face API
* Mistral AI Model


