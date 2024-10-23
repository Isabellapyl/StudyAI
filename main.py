import tkinter as tk  # Importing the Tkinter library for GUI
from tkinter import scrolledtext, Canvas, Frame, Scrollbar, messagebox  # Import specific components from Tkinter
import google.generativeai as genai  # Import Google Generative AI library
import re  # Import regular expressions for string processing

# Configure the API key for Google Generative AI
API_KEY = "AIzaSyAROOunbhQRlU56kK0I0g3axmxIgScp-VI"  # Set the API key for Generative AI
genai.configure(api_key=API_KEY)  # Configure the API key for Generative AI

# Function to generate questions using the Gemini API based on user input
def generate_questions(text):  # Define function to generate questions from text
    model = genai.GenerativeModel("gemini-1.5-flash-latest")  # Use the specified generative model
    try:  # Attempt to generate questions
        response = model.generate_content(
            f"Generate 10 clear, distinct questions based on the following text: {text}. Ensure every question ends with a question mark."  # Prompt for generating questions
        )
    except Exception as e:  # Handle exceptions
        messagebox.showerror("API Error", f"Error generating questions: {str(e)}")  # Display error message
        return []  # Return empty list on failure

    questions = response.text.split('\n')  # Split the response text into individual questions

    # Remove unnecessary lines
    if len(questions) > 2:
        questions.pop(0)  # Remove first unnecessary line
        questions.pop(0)  # Remove second unnecessary line
    valid_questions = questions  # Assign valid questions

    # Remove numbering at the beginning of each question (if any)
    # ^ indicates the start of the string.
    # \d+ matches one or more digits.
    # \.? optionally matches a period.
    # \s* matches zero or more whitespace characters.
    valid_questions = [re.sub(r'^\d+\.?\s*', '', q) for q in valid_questions]  # Remove numbering using regex

    return valid_questions  # Return the list of valid questions

# Function to generate feedback based on user's answers
def generate_feedback(question, answer):  # Define function to generate feedback
    model = genai.GenerativeModel("gemini-1.5-flash-latest")  # Use the specified generative model
    prompt = f"Here is the question:\n{question}\nHere is the user's answer:\n{answer}\nPlease provide maximum 3 sentences of feedback on this answer. Highlight any incorrect or incomplete answers and give suggestions for improvement."  # Create prompt for generating feedback

    try:  # Attempt to generate feedback
        response = model.generate_content(prompt)  # Generate feedback based on the prompt
    except Exception as e:  # Handle exceptions
        return "Error generating feedback."  # Return error message on failure

    return response.text  # Return the generated feedback text

# Function to generate questions based on user's study notes
def submit_notes():  # Define function to submit notes
    notes = notes_input.get("1.0", tk.END).strip()  # Get user notes from input area

    if not notes:  # Check if notes are empty
        tk.messagebox.showerror("Error", "Please input your study notes.")  # Show error message if notes are empty
        return  # Do nothing if notes are empty

    # Count the number of words
    word_count = len(notes.split())  # Calculate word count from notes

    # Check if the word count is less than 30
    if word_count < 30:  # If word count is below 30
        tk.messagebox.showerror("Error", "Please input at least 30 words.")  # Show error message
        return  # Do nothing if not enough words

    # Hide the notes input area and the button after generating questions
    notes_input.pack_forget()  # Hide notes input
    notes_label.pack_forget()  # Hide notes label
    submit_notes_button.pack_forget()  # Hide submit button

    # Clear the previous questions, answers, and feedbacks
    for widget in question_frame.winfo_children():  # Iterate over child widgets in question frame
        widget.destroy()  # Destroy each widget

    # Generate questions based on user notes
    questions = generate_questions(notes)  # Call function to generate questions

    # Display questions, answers, and feedback section
    for i, question in enumerate(questions[:10]):  # Limit to 10 questions
        if question.strip():  # Check if question is not empty
            question_label = tk.Label(question_frame, text=f"Question {i + 1}: {question}", wraplength=670, justify=tk.LEFT, bg="lightblue", borderwidth=2, relief="solid")  # Create label for question
            question_label.pack(pady=(10, 5), anchor='w')  # Pack question label into frame

            answer_title = tk.Label(question_frame, text=f"Your Answer for Question {i + 1}:", wraplength=350, justify=tk.LEFT, bg="lightgray", borderwidth=2, relief="solid")  # Create label for answer title
            answer_title.pack(pady=(0, 5), anchor='w')  # Pack answer title label into frame

            answer_box = scrolledtext.ScrolledText(question_frame, height=3, wrap=tk.WORD, borderwidth=2, relief="solid")  # Create text box for answer input
            answer_box.pack(pady=(5, 10), fill=tk.X)  # Pack answer box into frame
            answer_boxes.append((question, answer_box))  # Add question and answer box to list

            feedback_title = tk.Label(question_frame, text=f"Feedback for Question {i + 1}:", wraplength=750, justify=tk.LEFT, bg="lightyellow", borderwidth=2, relief="solid")  # Create label for feedback title
            feedback_title.pack(pady=(0, 5), anchor='w')  # Pack feedback title label into frame

            feedback_box = scrolledtext.ScrolledText(question_frame, height=3, wrap=tk.WORD, state=tk.DISABLED, borderwidth=2, relief="solid")  # Create text box for feedback (disabled)
            feedback_box.pack(pady=(5, 10), fill=tk.X)  # Pack feedback box into frame
            feedback_boxes.append(feedback_box)  # Add feedback box to list

    # Add the black box after Question 10 So the application scrolls easily to view the feedback for question 10
    black_box = Frame(question_frame, height=50, bg="black")  # Create a black box for spacing below question 10
    black_box.pack(fill=tk.X, pady=(10, 10))  # Pack black box into frame

    # Add buttons for submitting answers and clearing inputs
    clear_button.pack(pady=10)  # Pack clear button into frame
    submit_answers_button.pack(pady=20)  # Pack submit answers button into frame
    question_frame.update_idletasks()  # Update task information for the frame
    canvas.config(scrollregion=canvas.bbox("all"))  # Configure canvas scroll region

# Function to submit answers and receive feedback
def submit_answers():  # Define function to submit answers
    for i, (question, answer_box) in enumerate(answer_boxes):  # Iterate over questions and answer boxes
        answer = answer_box.get("1.0", tk.END).strip()  # Get user input from text box

        if not answer:  # Check if answer is empty
            continue  # Skip empty answers

        feedback = generate_feedback(question, answer)  # Call function to generate feedback

        feedback_boxes[i].config(state=tk.NORMAL)  # Enable feedback box for editing
        feedback_boxes[i].delete("1.0", tk.END)  # Clear existing text in feedback box
        feedback_boxes[i].insert(tk.END, feedback)  # Insert new feedback into feedback box
        feedback_boxes[i].config(state=tk.DISABLED)  # Disable feedback box after updating

# Function to clear all notes, questions, and answers
def clear_all():  # Define function to clear all inputs
    notes_input.delete("1.0", tk.END)  # Clear the notes input box
    for widget in question_frame.winfo_children():  # Iterate over child widgets in question frame
        widget.destroy()  # Destroy each widget
    answer_boxes.clear()  # Clear the answer boxes list
    feedback_boxes.clear()  # Clear the feedback boxes list
    canvas.config(scrollregion=canvas.bbox("all"))  # Configure canvas scroll region
    notes_label.pack(pady=(10, 0), anchor='w')  # Pack notes label into frame
    notes_input.pack(pady=(5, 10), fill=tk.X)  # Pack notes input box into frame
    submit_notes_button.pack(pady=10)  # Pack submit button into frame
    submit_answers_button.pack_forget()  # Hide submit answers button
    clear_button.pack_forget()  # Hide clear button

# Set up the main window
root = tk.Tk()  # Create main window
root.title("AI Study Helper")  # Set title of the main window
root.geometry("800x900")  # Set the geometry of the main window

canvas = Canvas(root)  # Create canvas for scrolling content
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # Pack canvas into the main window

scrollbar = Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)  # Create vertical scrollbar
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Pack scrollbar into the main window

canvas.configure(yscrollcommand=scrollbar.set)  # Configure canvas to work with scrollbar
question_frame = Frame(canvas)  # Create a frame to hold all questions, answers, and feedback
canvas.create_window((0, 0), window=question_frame, anchor="nw")  # Add frame to canvas

def on_frame_configure(event):  # Define function to configure frame
    canvas.configure(scrollregion=canvas.bbox("all"))  # Update canvas scroll region

question_frame.bind("<Configure>", on_frame_configure)  # Bind configure event to frame

# UI elements for user input
notes_label = tk.Label(root, text="Enter your study notes below (at least 30 words):", bg="lightgreen", borderwidth=2, relief="solid")  # Create label for notes input
notes_label.pack(pady=(10, 0), anchor='w')  # Pack notes label into main window

notes_input = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD, borderwidth=2, relief="solid")  # Create text box for notes input
notes_input.pack(pady=(5, 10), fill=tk.X)  # Pack notes input box into main window

submit_notes_button = tk.Button(root, text="Generate Questions", command=submit_notes, bg="lightblue", borderwidth=2, relief="raised")  # Create button to submit notes
submit_notes_button.pack(pady=10)  # Pack submit button into main window

answer_boxes = []  # Initialize list to store answer boxes
feedback_boxes = []  # Initialize list to store feedback boxes

submit_answers_button = tk.Button(root, text="Submit Answers", command=submit_answers, bg="lightblue", borderwidth=2, relief="raised")  # Create button to submit answers
clear_button = tk.Button(root, text="Clear All", command=clear_all, bg="red", fg="white", borderwidth=2, relief="raised")  # Create button to clear all inputs

def on_mouse_wheel(event):  # Define function for mouse wheel scrolling
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")  # Scroll canvas on mouse wheel

canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Bind mouse wheel event to canvas

root.mainloop()  # Run the main window loop
