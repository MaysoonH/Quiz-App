from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import streamlit as st
import re



def create_quiz_prompt_template(questions_number, quiz_context):
    return PromptTemplate(
        input_variables=["questions_number", "quiz_context"],
        template=f"""
        Generate a quiz with {questions_number} multiple-choice questions about {quiz_context}.
        try to follow the following example and keep every question in one line every question needs to be in one line and every answer needs to be in one line too
        the exam will be multiple choice and should look like this example dont use any of these questions:
        Questions:
        1. What is the capital of France?
            a. Madrid
            b. Berlin
            c. Paris
            d. Rome
        2. Who wrote "Romeo and Juliet"?
            a. Charles Dickens
            b. William Shakespeare
            c. Jane Austen
            d. Mark Twain
        3. What is the largest planet in our solar system?
            a. Mars
            b. Venus
            c. Jupiter
            d. Saturn
        and answers should look like this:
        Answers:
        1. c
        2. b
        3. c
        """
    )

def main():
    st.title("Quiz App")
    st.write("This app generates a quiz based on the given context.")

    st.session_state.quiz_data = st.session_state.get("quiz_data", None)
    st.session_state.user_answers = st.session_state.get("user_answers", {})

    # User inputs
    quiz_context = st.text_area("Enter the quiz context/concept", key="quiz_context")
    questions_number = st.number_input("Enter number of questions", min_value=1, max_value=30, key="questions_number")

    # Generate quiz button
    if st.button("Generate Quiz"): 
        # Generate a random seed based on user inputs
        if not st.session_state.quiz_context :
            st.error("Quiz context is required. Please enter a value.")
            st.stop()
        prompt_template = create_quiz_prompt_template(questions_number, quiz_context)
        llm = ChatOpenAI(temperature=0.9)
        chain = LLMChain(llm=llm, prompt=prompt_template)
        quiz_response = chain.run(questions_number=questions_number, quiz_context=quiz_context)

        st.write("Quiz generated!")

        # Parsing the response
        parser = AnswersParser()
        questions, answers_dict = parser.parse_questions_and_answers(quiz_response)

        # Store quiz data in session state
        st.session_state.quiz_data = {
            "questions": questions,
            "answers_dict": answers_dict
        }

        # Reset user answers
        st.session_state.user_answers = {f"Question {i}": None for i in range(1, len(questions) + 1)}

    if st.session_state.quiz_data:
        # Display the quiz questions with clickable answers
        st.session_state.user_answers_dict = {}
        for i, q in enumerate(st.session_state.quiz_data["questions"], start=1):
            question_label = f"Question {i}"
            st.subheader(question_label)
            st.write(q["question"])
            options = q["choices"]

            user_answer = st.radio("Select an answer:", options, key=f"question_{i}")
            st.session_state.user_answers_dict[question_label] = user_answer

        # Submit button to check answers
        if st.button("Submit Answers"):
            correct_count = 0
            for question_number, correct_answer in st.session_state.quiz_data["answers_dict"].items():
                user_answer = st.session_state.user_answers_dict.get(question_number)
                st.write(f" {question_number}:")
                st.write(f"  User Answer: {user_answer}")
                st.write(f"  Correct Answer: {correct_answer}")
                st.write("")
                if user_answer.lower()[0] == correct_answer.lower()[0]:
                    correct_count += 1 

            # Calculate and display the score
            st.subheader(f"You got {correct_count} out of {len(st.session_state.quiz_data['questions'])} questions correct!")

class AnswersParser:
    def parse_questions_and_answers(self, text: str):
        # Split the text into questions and answers sections
        split_text = text.split("Answers:")
        questions_text = split_text[0]
        answers_text = split_text[1] if len(split_text) > 1 else ""

        # Process questions
        questions = self.process_questions(questions_text)

        # Extract answers
        answers = re.findall(r"(\d+\.\s*[a-d])", answers_text)
        answers_dict = {f"Question {i + 1}": answer.split('. ')[1] for i, answer in enumerate(answers)}

        return questions, answers_dict

    def process_questions(self, questions_text):
        # Split by question number
        question_splits = re.split(r'\d+\.', questions_text)
        questions = []

        for q in question_splits[1:]:
            # Further split into question and choices
            parts = q.split('\n', 1)
            question_statement = parts[0].strip()
            choices_text = parts[1].strip() if len(parts) > 1 else ''
            
            # Check if choices_text contains valid choices
            choices = re.findall(r'\s*([a-d]\.\s*\S.*)', choices_text)
            if choices:
                choices = [choice.strip() for choice in choices]
                questions.append({
                    "question": question_statement,
                    "choices": choices
                })

        return questions

if __name__ == "__main__":
    main()
