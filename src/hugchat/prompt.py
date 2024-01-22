from .crowdsourced_prompts import PROMPTS
# Pre-defined Prompts for the hugchat command line interface.

def get_roles():
    """Return a list containing just the names of all defined roles."""
    return [role['role'] for role in PROMPTS.values()]

def handle_prompt():
    # Print a menu allowing users to select a role
    print("\nAvailable Roles:\n")
    for index, role in enumerate(get_roles(), start=1):
        print(f"[{index}.{role}]", end=", ")

    # Request the user's selection
    choice = None
    while not isinstance(choice, int) or choice < 0 or choice > len(PROMPTS):
        try:
            choice = int(input("\nPlease make a valid selection: ")) - 1
        except ValueError:
            pass

    # Obtain the selected role and associated details
    chosen_role = get_roles()[choice]
    prompt = next((p for p in PROMPTS.values() if p['role'].lower() == chosen_role.lower()), None)

    if prompt:
        return chosen_role, prompt['prompt']
    else:
        raise Exception(f"No such role found ({chosen_role})")

