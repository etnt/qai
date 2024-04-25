import os
import ollama
import textwrap
from googlesearch import search
from qutils import extract_json_objects, Painter, print_verbose



example_json = """
{
    'action': 'draw',
    'instructions': [
        {'draw_triangle': {'points': [[100, 30], [30, 70], [130, 100]]}},
        {'draw_circle': {'center': [150, 75], 'radius': 25}},
        {'draw_line': {'points': [[10,100], [100,10]]}},
        {'draw_text': {'position': [50,40], 'text': 'Example text'}},
        {'set_color': 'blue'},
        {'draw_polygon': {'points': [[110, 40], [40, 90], [140, 120], [200,200]]}},
        {'draw_sinus': {'start': [20,200], 'range': [0, 360, 5, 100]}},
        {'clear_all': null}
    ]
}
"""

template = """<|system|>
Your goal is to make drawings based on the user request.

You have access to a drawing tool that can perform the following operations:
  - draw_line : This operation draws a line between two points, here represented as two pairs of integers: (X1,Y1) and (X2,Y2)
  - draw_circle : This operation draws a circle with center: (X,Y) ,and a radius of: R
  - draw_triangle : This operation draws a triangle where each corner is defined as a list of points: [(X1,Y1), (X2,Y2), (X3,Y3)]
  - draw_curve : This operation draws a curve between a set of points, where the points are represented as pairs of integers: [(X1,Y1), (X2,Y2), ... , (Xn,Yn)]
  - draw_polygon : This operation draws lines between a set of points, ending at the starting point, where the points are represented as pairs of integers: [(X1,Y1), (X2,Y2), ... , (Xn,Yn)]
  - draw_sinus : This operation draws a sinus curve starting at the point: (X,Y) ,ranging from a Start degree to a Stop degree taking steps of Step degrees ,and where the Y position is scaled by Yscale  
  - draw_text : This operation will draw a text the Text is centered vertically and horizontally around position (X, Y) , newlines are represented as '\n'
  - set_color : This operation sets the color for the upcoming draw operations where color names must be valid Tkinter color names.
  - clear_all : This operation remove all drawn objects from the drawing canvas.

Here follows your instructions:
1. The drawing tool is operationg within a reversed cartesian coordinate system where the X-axis is pointing to the right and the Y-axis is pointing down and where the origin is at (0,0)
2. The X- and Y-coordinates can only be positive integers.
3. The drawing operations are expressed in JSON format.
4. You should indicate the beginning of the JSON data by a line containing: Action:
5. Do not add any JSON data which are not shown in the example and do not add any JSON comments.
6. Do not produce any textual explanations, only JSON.
7. Indicate the JSON output by beginning the output with a single line containing: Action:
8. At the bottom of this instruction you will find the chat history that you can make use of to improve your output.
9. Any (additional) text response should be output between a line starting with 'START-TEXT:' and a line 'END-TEXT:'

Here follows an example of a text response:

START-TEXT:
This is some example text
spanning two lines.
END-TEXT:

Here follows an example of JSON data containing drawing instructions:

Action:
{example_json}

Here follows the chat history:
{chat_history}
<|end|>
<|user|>
User request: {question}<|end|>
<|assistant|>
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
        print_verbose(f"<info> response = {response}")

        # Check if the response contains 'Action:'
        if 'Action:' in response:
            # Convert it to proper JSON format
            json_text = response.replace("'", '"')

            # Extract JSON objects
            data = None
            for data in extract_json_objects(json_text):
                print_verbose("<info> Extracted JSON object: ", data)

            # If the JSON object contains an 'action_input' key, and 'query' is in 'action_input',
            # perform a Google search and store the content in the VectorStore, then perform a
            # similarity search.
            if data and 'action' in data and 'draw' in data['action']:
                instructions = data['instructions']
                for instruction in instructions:
                    p.handle_instruction(instruction)


if __name__ == "__main__":
    main()
