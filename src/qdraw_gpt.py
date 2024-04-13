from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import BaseOutputParser
from dotenv import load_dotenv
import os
from qutils import extract_json_objects, Painter, print_verbose

# Make sure to create an ./python/.env file and put the OpenAI API key in it, like:
#
#    OPENAI_API_KEY='fniwejfiwejfiwjfiwef'
#
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

chat_model = ChatOpenAI(openai_api_key=api_key, model_name="gpt-4")



example_json = """
{
    'action': 'draw',
    'instructions': [
        {'draw_triangle': {'points': [[100, 30], [30, 70], [130, 100]]}},
        {'draw_line': [10,100,100,10]},
        {'set_color': 'blue'},
        {'draw_polygon': {'points': [[110, 40], [40, 90], [140, 120], [200,200]]}},
        {'draw_sinus': {'start': [20,200], 'range': [0, 360, 5, 100]}}
    ]
}
"""

system_template = """
Your goal is to make drawings based on the user input.

You have access to a drawing tool that can perform the following operations:
  - draw_line : This operation draws a line between two points, here represented as two pairs of integers: (X1,Y1) and (X2,Y2)
  - draw_circle : This operation draws a circle with center: (X,Y) ,and a radius of: R
  - draw_triangle : This operation draws a triangle where each corner is defined as a list of points: [(X1,Y1), (X2,Y2), (X3,Y3)]
  - draw_curve : This operation draws a curve between a set of points, where the points are represented as pairs of integers: [(X1,Y1), (X2,Y2), ... , (Xn,Yn)]
  - draw_polygon : This operation draws lines between a set of points, ending at the starting point, where the points are represented as pairs of integers: [(X1,Y1), (X2,Y2), ... , (Xn,Yn)]
  - draw_sinus : This operation draws a sinus curve starting at the point: (X,Y) ,ranging from a Start degree to a Stop degree taking steps of Step degrees ,and where the Y position is scaled by Yscale  
  - set_color : This operation sets the color for the upcoming draw operations.

Here follows your instructions:
1. The drawing tool is operationg within a reversed cartesian coordinate system where the X-axis is pointing to the right and the Y-axis is pointing down and where the origin is at (0,0)
2. The X- and Y-coordinates can only be positive integers.
3. The drawing operations are expressed in JSON format.
4. You should indicate the beginning of the JSON data by a line containing: Action:
5. Do not add any JSON data which are not shown in the example and do not add any JSON comments.
6. Do not produce any textual explanations, only JSON.
7. Indicate the JSON output by beginning the output with a single line containing: Action:
8. At the bottom of this instruction you will find the chat history that you can make use of to improve your output.

Here follows an example of JSON data containing drawing instructions:

Action:
{example_json}

Here follows the chat history:
{chat_history}
"""

user_template = "{question}"

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("human" , user_template)
])


def main():
    p = Painter("AI Drawing Tool")
    chat_history = []  # Initialize the chat history

    while True:
        question = input("Enter a question: ")

        # Format the Prompt
        messages = chat_prompt.format_messages(
            question=question,
            example_json=example_json,
            chat_history='\n'.join(chat_history)
            )

        # Call Chat-GPT
        result = chat_model.invoke(messages)
        response = result.content
        print_verbose(f"<info> response = {response}")

        # Update the Chat History
        chat_history.append(question)
        chat_history.append(response)

        # Check if the response contains 'Action:'
        if 'Action:' in response:
            # Convert it to proper JSON format
            json_text = response.replace("'", '"')

            # Extract JSON objects
            for data in extract_json_objects(json_text):
                print_verbose("<info> Extracted JSON object: ", data)

            # If the JSON object contains an 'action_input' key, and 'query' is in 'action_input',
            # perform a Google search and store the content in the VectorStore, then perform a
            # similarity search.
            if 'action' in data and 'draw' in data['action']:
                instructions = data['instructions']
                for instruction in instructions:
                    p.handle_instruction(instruction)
        else:
            print(response)


if __name__ == "__main__":
    main()
