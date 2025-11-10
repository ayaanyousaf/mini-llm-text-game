import ollama
import os
import json
from datetime import datetime

# Open the rules JSOn file
with open('rules.json', 'r') as file:
    rules = json.load(file)

# Define global variables
MODEL = "gemma3:1b" # default lightweight model, recommended to change to 7b/8b model
state = rules['START'].copy()
turns = []
transcript_path = 'samples/transcript.txt'

def save_state(): 
    """
    Saves the current state of the game as a JSON file.
    """
    with open('save.json', 'w') as file:
        json.dump({'state': state, 'turns': turns}, file, indent=2)
    print("Game saved.")

def load_state():
    """
    Loads the last saved game state JSON file.
    """
    global state, turns
    
    with open('save.json', 'r') as file:
        data = json.load(file)
    state, turns = data['state'], data['turns']
    print("Game loaded.")

def add_to_transcript(role, content):
    """
    Adds
    """
    os.makedirs(os.path.dirname(transcript_path), exist_ok=True)

    with open(transcript_path, 'a') as file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"[{timestamp}] {role.upper()}:\n{content}\n\n")

def call_llm(prompt):
    short_rules = {
        "COMMANDS": rules["COMMANDS"],
        "LOCKS": rules.get("LOCKS", {}),
        "QUEST": rules["QUEST"],
        "END_CONDITIONS": rules["END_CONDITIONS"]
    }

    messages = [
        {"role": "system", "content": open('prompts/gm.txt').read()},
        {"role": "user", "content": json.dumps({
            'rules': short_rules,
            'state': state,
            'last_turns': turns[-2:],
            'player_input': prompt
        })}
    ]

    print("\nSending action to LLM...")
    response = ollama.chat(model=MODEL, messages=messages)
    text = response['message']['content']

    # Clean up the model's response for models with smaller parameters (gemma)
    text = text.replace("```json", "")
    text = text.replace("```", "")
    if text.lower().startswith("json"):
        text = text[text.lower().find("{"):]

    text = text.strip().replace(",]", "]").replace(",}", "}")

    try: 
        return json.loads(text)
    except json.JSONDecodeError:
        print("Error decoding LLM JSON response:")
        return {"narration": "Game Master encountered an error.", "state_change": []}
    
def apply_state_changes(changes):
    for change in changes:
        action = change.get('action')
        key = change.get('key')
        value = change.get('value')

        if action == 'set':
            state[key] = value
        elif action == 'delete' and key in state:
            del state[key]

def enforce_rules():
    # HP check
    if state.get("hp", 10) <= 0:
        state.setdefault("flags", {})["hp_zero"] = True

    # Inventory limit
    inventory = state.get("inventory", [])
    limit = rules.get("INVENTORY_LIMIT", 5)
    if len(inventory) > limit:
        state["inventory"] = inventory[:limit]
        print("Inventory full! You can't carry more items.")

def check_end_conditions():
    end = rules.get('END_CONDITIONS', {})
    flags = state.get('flags', {})

    if all(flags.get(flag, False) for flag in end.get('WIN_ALL_FLAGS', [])):
        print("🏆 You successfully completed your quest. The ancient temple trembles as light surrounds you.")
        return True

    if any(flags.get(flag, False) for flag in end.get('LOSE_ANY_FLAGS', [])):
        print("💀 You have fallen. The temple claims another soul.")
        return True

    if state.get("turns", 0) >= end.get("MAX_TURNS", 50):
        print("⏰ Time has run out. The temple collapses around you.")
        return True

    return False

def main():
    global running
    running = True

    while running: 
        user_input = input("\n> ").strip().lower()
        state['turns'] = state.get('turns', 0) + 1

        if not any(user_input.startswith(cmd.split()[0]) for cmd in rules['COMMANDS']):
            print("Invalid command. Type 'help' for a list of commands.")
            continue

        if user_input == 'help':
            print("Available commands:", ", ".join(rules['COMMANDS']))
            continue

        if user_input == 'inventory':
            print("Inventory:", state.get('inventory', []))
            continue

        if user_input == 'save':
            save_state()
            continue

        if user_input == 'load':
            load_state()
            continue   
            
        if user_input == 'quit':
            print("Exiting game.")
            running = False
            break
    
        response = call_llm(user_input)
        narration = response.get("narration", "")
        print("\n" + narration)

        apply_state_changes(response.get("state_change", []))
        enforce_rules()

        if check_end_conditions(): 
            running = False
            break

        turns.append({"player": user_input, "gm": narration})
        add_to_transcript('player', user_input)
        add_to_transcript('gm', json.dumps(response, indent=2))

if __name__ == "__main__":
    main()