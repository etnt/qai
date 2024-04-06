#
# A Dungeon and Dragons game.
#
import ollama

# Initialize the game state
game_state = [
    {"role": "system", "content": "You are a Dungeon Master. Narrate a Dungeons and Dragons game. You describe the surroundings and present the user with a few options of what the user can do. The user can pick up artifacts, cast spells and fight with weapons."},
    {"role": "user", "content": "I want to start a new game. I am a level 1 wizard. I have just stopped in front of a wast forrest."},
]

# Main game loop
while True:
    # Use the ollama.chat function to generate the Dungeon Master's response
    output = ollama.chat(model="mistral", messages=game_state)

    # Print the Dungeon Master's response
    print(output['message']['content'])

    # Add the Dungeon Master's response to the game state
    game_state.append({"role": "system", "content": output['message']['content']})

    # Get the player's action
    action = input("What do you want to do? ")

    # Add the action to the game state
    game_state.append({"role": "user", "content": action})


