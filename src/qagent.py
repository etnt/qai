# https://huggingface.co/blog/open-source-llms-as-agents
import os
import ollama
import textwrap

question = "Who got the Nobel Prize in Litterature in 2023?"

example_json = """
{
    'action': 'convert_time',
    'action_input': {
        'time': '1:30:00'
    }
}
"""


template = """
Here is a question: {question}
You have access to these tools:
    - convert_time: converts a time given in hours:minutes:seconds into seconds.
    - search: searches the web for the answer to the question

You should first reflect with ‘Thought: {your_thoughts}’, then you either:
    - if you don't know the answer: call a tool with the proper JSON formatting,
    - if you know the answer: print your final answer starting with the prefix ‘Final Answer:’ 

Here is an example of the JSON formatting for calling a tool:

Action:
{example_json}

{observation}
"""



def main():
    # Get the value of the environment variable 'USE_MODEL'
    # If 'USE_MODEL' is not set or is empty, use 'default_value' instead
    model = os.getenv('USE_MODEL', 'mistral')

    chat_history = []  # Initialize your chat history
    observation = ""
    while True:
        prompt = template.format(question=question, your_thoughts="{your_thoughts}", example_json=example_json, observation=observation)
        output = ollama.generate(model=model, prompt=prompt, stream=False)
        response = output['response'].strip()
        print("")
        # To make the text easier to read, we wrap it to a maximum width of 62 characters.
        # Split the response into lines, wrap each line, then join them back together
        print("\n".join([textwrap.fill(line, width=62, break_long_words=False) for line in response.split('\n')]))
        print("")
        uinput = input(">>> Simulate a search answer: ")
        observation = f"Observation: {uinput}"


if __name__ == "__main__":
    main()
