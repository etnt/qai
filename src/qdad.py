#
# A Dungeon and Dragons game.
#
import os
import ollama
import textwrap


template = """
    You are a Dungeon Master that will narrate a Dungeons and Dragons game. 
    You describe the surroundings and present the user with a few options of what the user can do. 
    The user can pick up artifacts, cast spells and fight with weapons.
    Your goal is to interpret the user's actions and narrate the outcome based on the user input.

    Here are some rules to follow:
    1. Start by asking what character the user is playing.
    2. Describe the surroundings and present the user with a few options.
    3. Interpret the user's actions and narrate the outcome.
    
    Here is the chat history; use this to understand what to say next: {chat_history}
    {user_input}
    """



def main():
    # Get the value of the environment variable 'MY_ENV_VAR'
    # If 'MY_ENV_VAR' is not set or is empty, use 'default_value' instead
    model = os.getenv('USE_MODEL', 'mistral')

    chat_history = []  # Initialize your chat history
    user_input = ""  # Initialize user input
    while True:
        prompt = template.format(chat_history=chat_history, user_input=user_input)
        output = ollama.generate(model=model, prompt=prompt, stream=False)
        response = output['response'].strip()
        chat_history.append(response)  # Update chat history
        print("")
        # To make the text easier to read, we wrap it to a maximum width of 62 characters.
        # Split the response into lines, wrap each line, then join them back together
        print("\n".join([textwrap.fill(line, width=62, break_long_words=False) for line in response.split('\n')]))
        print("")
        uinput = input(">>> What do you want to do: ")
        user_input = f"User input: {uinput}"


if __name__ == "__main__":
    main()
