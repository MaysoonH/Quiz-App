#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
# test
# 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
from langchain import PromptTemplate 
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseOutputParser
import streamlit as st
import re
# from openai import OpenAI
import os
import openai


################################################# Undo till here

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
# langchain_client = LangchainOpenAI()


# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
#   ]
# )

# print(completion.choices[0].message)
def get_quiz_questions(topic, num_questions):
    prompt = f"Create a multiple-choice quiz with {num_questions} questions about {topic}, with the answers at the end. in the form "
  
    completion = openai.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
      ]
    )
    # initial_response =  
    return completion.choices[0].message
    # processed_response = langchain_client.run(initial_response)
    # return processed_response

# prompt = "create a quiz about the basics of python programming"
# quiz_python =get_response(prompt) 

def create_quiz_prompt_template():
    template = """
        You are an expert quiz maker for any feild. 
        Create a multiple choice quiz with {questions_number} about the following concept/content: {quiz_context}.
        The format of the quiz should be as follows:
        - Questions:
            <Question 1>: 
                <a. Answer 1> 
                <b. Answer 2> 
                <c. Answer 3> 
                <d. Answer 4>
            <Question 2>: 
                <a. Answer 1> 
                <b. Answer 2> 
                <c. Answer 3> 
                <d. Answer 4>
        ....
        - Answers:
            <Answer 1>:<a|b|c|d>
            <Answer 2>:<a|b|c|d>
        ....
        Example: 
        - Questions: 
        - 1. What is the square root of 4?
            a. 2
            b. 4
            c. 3
            d. 1
        - Answers:
        -1. a   

    """
    prompt = PromptTemplate.from_template(template)
    prompt.format(questions_number = 3, quiz_context="Data structures in python")
    return prompt

def create_quiz_chain(prompt_template, llm): 
    return LLMChain(llm=llm, prompt = prompt_template)




def main():

    st.title("Quiz App")
    st.write("This app generates a quiz based on the given context.")

    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = None

    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}

    # User inputs
    quiz_context = st.text_area("Enter the quiz context/concept")
    questions_number = st.number_input("Enter number of questions", min_value=1, max_value=30)

    # Generate quiz button
    if st.button("Generate Quiz"): 
        # Generate a random seed
        openai_questions = get_quiz_questions(quiz_context, questions_number)
        prompt_template = create_quiz_prompt_template()
        llm = ChatOpenAI()
        chain = create_quiz_chain(prompt_template, llm)
        quiz_response = chain.run(questions_number=questions_number, quiz_context=openai_questions)
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

        st.session_state.user_answers_dict = {}

        # Display the quiz questions with clickable answers
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
                if st.session_state.user_answers_dict.get(question_number, "").lower()[0] == correct_answer.lower()[0]:
                    correct_count +=  1 

            # Calculate and display the score
            st.subheader(f"You got {correct_count} out of {len(st.session_state.quiz_data['questions'])} questions correct!")




class AnswersParser:
    def parse_questions_and_answers(self, text: str):
        # Split the text into questions and answers sections
        split_text = text.split("- Answers:")
        questions_text = split_text[0]
        answers_text = split_text[1] if len(split_text) > 1 else ""

        # Process questions
        questions = self.process_questions(questions_text)

        # Extract answers
        answers = re.findall(r"\d+\.\s*([a-d])", answers_text)
        answers_dict = {f"Question {i+1}": answer for i, answer in enumerate(answers)}

        return questions, answers_dict

    def process_questions(self, questions_text):
        # Split by question number
        question_splits = re.split(r'\d+\.', questions_text)
        questions = []

        for q in question_splits[1:]:  # Skip the first split as it's empty
            # Further split into question and choices
            parts = q.split('\n')
            question_statement = parts[0].strip()
            choices = [choice.strip() for choice in parts[1:] if choice.strip()]

            questions.append({
                "question": question_statement,
                "choices": choices
            })

        return questions

    
if __name__ == "__main__":
    main()









