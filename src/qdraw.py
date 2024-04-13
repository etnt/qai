import os
import ollama
import textwrap
from googlesearch import search
from qutils import extract_json_objects, Painter, print_verbose



example_json = """
{
    'action': 'draw',
    'instructions': [
        {'draw_line': [10,10,100,100]},
        {'draw_line': [10,100,100,10]},
        {'draw_circle': {'center': [150, 75], 'radius': 25}}
    ]
}
"""

template = """
Here is the user input: {question}

Your goal is to make drawings based on the user input.

You have access to a drawing tool that can perform the following operations:
  - draw_line : the operation draws a line between two points, here represented as two pairs of integers: (X1,Y1) and (X2,Y2)
  - draw_circle : the operation draws a circle with center: (X,Y) ,and a radius of: R

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

def main():
    # Get the value of the environment variable 'USE_MODEL'
    # If 'USE_MODEL' is not set or is empty, use 'default_value' instead
    model = os.getenv('USE_MODEL', 'mistral')

    p = Painter("AI Drawing Tool")
    
    chat_history = []  # Initialize your chat history
    observation = ""
    while True:
        question = input("Enter a question: ")
        chat_history.append(question)

        prompt = template.format(question=question, example_json=example_json, chat_history=chat_history)
        output = ollama.generate(model=model, prompt=prompt, stream=False)
        response = output['response'].strip()
        chat_history.append(response)
        #print_verbose(f"<info> response = {response}")

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


if __name__ == "__main__":
    main()