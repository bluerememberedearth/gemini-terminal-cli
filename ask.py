#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --- Permanent Imports & Initial Config ---
import os
import sys
# We import google.genai later, only when needed by the final script,
# but you could move it here if preferred.

# API Key will be permanently embedded here after first run.
# DO NOT MANUALLY EDIT THIS LINE UNLESS RESETTING!
API_KEY = "INITIAL_PLACEHOLDER"
MODEL_NAME = "gemini-1.5-flash" # Or your preferred model
# --- End Permanent Imports & Initial Config ---


# --- START SELF-MODIFY/SETUP BLOCK (Will be removed after first run) ---

_SETUP_BLOCK_START_MARKER_ = "# --- START SELF-MODIFY/SETUP BLOCK"
_SETUP_BLOCK_END_MARKER_ = "# --- END SELF-MODIFY/SETUP BLOCK"

def _perform_first_run_setup():
    """Prompts for API key, embeds it, and removes this setup block."""
    global API_KEY # Needed to set the key for the current run

    print("-" * 30)
    print("First run: Google AI API Key configuration required.")
    print("Your key will be embedded, and setup code removed.")
    print("Get key: https://aistudio.google.com/app/apikey")
    print("-" * 30)

    new_key = ""
    while not new_key:
        new_key = input("Enter your Google AI API Key: ").strip()
        if not new_key:
            print("API key cannot be empty.")

    script_path = os.path.abspath(__file__)
    new_key_line = f'API_KEY = "{new_key}" # Embedded by setup\n'

    try:
        print(f"\nReading current script: {script_path}")
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start_index = -1
        end_index = -1

        for i, line in enumerate(lines):
            if _SETUP_BLOCK_START_MARKER_ in line:
                start_index = i
            elif _SETUP_BLOCK_END_MARKER_ in line:
                end_index = i
                break # Found both markers

        if start_index == -1 or end_index == -1 or end_index <= start_index:
            print("\nCRITICAL ERROR: Could not find setup block markers.", file=sys.stderr)
            print("Expected markers:", file=sys.stderr)
            print(f"Start: '{_SETUP_BLOCK_START_MARKER_}'", file=sys.stderr)
            print(f"End:   '{_SETUP_BLOCK_END_MARKER_}'", file=sys.stderr)
            print("Cannot modify script. Aborting setup.", file=sys.stderr)
            print("Using entered key for this session only.", file=sys.stderr)
            API_KEY = new_key # Use for this session only
            return False # Indicate setup failed

        # Construct the new script content
        print("Constructing pruned script content...")
        new_lines = []
        # Keep lines before the setup block
        new_lines.extend(lines[:start_index])
        # Find where the original placeholder was and replace it
        placeholder_line_found = False
        for i in range(start_index): # Search only in the preserved top part
            if lines[i].strip().startswith('API_KEY = "INITIAL_PLACEHOLDER"'):
                 new_lines[i] = new_key_line # Replace placeholder with actual key
                 placeholder_line_found = True
                 break
        if not placeholder_line_found:
            print("\nWARNING: Could not find placeholder API_KEY line to replace.", file=sys.stderr)
            print("Appending new key line instead. Review script if issues occur.", file=sys.stderr)
            # Try inserting after the imports as a fallback - might need adjustment
            insert_pos = 0
            for i, line in enumerate(new_lines):
                if line.strip().startswith('# --- End Permanent Imports'):
                    insert_pos = i + 1
                    break
            new_lines.insert(insert_pos, new_key_line)


        # Keep lines after the setup block
        new_lines.extend(lines[end_index + 1:])

        # Overwrite the script with the new content
        # WARNING: Not atomic! Interruption can corrupt the file.
        print(f"Overwriting script file: {script_path}")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        print("Script successfully pruned and API key embedded.")
        API_KEY = new_key # IMPORTANT: Set for the current run!
        return True # Indicate setup successful

    except (IOError, OSError) as e:
        print(f"\nERROR: Failed to read/write script file '{script_path}': {e}", file=sys.stderr)
        print("Check file permissions. Script modification failed.", file=sys.stderr)
        print("Using entered key for this session only.", file=sys.stderr)
        API_KEY = new_key # Use for this session only
        return False # Indicate setup failed
    except Exception as e:
        print(f"\nUNEXPECTED ERROR during script update: {e}", file=sys.stderr)
        print("Using entered key for this session only.", file=sys.stderr)
        API_KEY = new_key # Use for this session only
        return False # Indicate setup failed

# Check if setup needs to run (only happens if placeholder is present)
if API_KEY == "INITIAL_PLACEHOLDER":
    if not _perform_first_run_setup():
        # If setup failed critically and couldn't even set the key for this session
        if API_KEY == "INITIAL_PLACEHOLDER":
             print("\nExiting due to critical setup failure.", file=sys.stderr)
             sys.exit(1)
    # Pause briefly after modification before continuing
    print("\nFirst run setup complete. Continuing with query...")
    # Optionally add: input("Press Enter to continue...")

# --- END SELF-MODIFY/SETUP BLOCK (This marker and the block above are removed) ---


# --- Core API Access Logic (Permanent) ---
if __name__ == "__main__":

    # Ensure API key is set (should be by now, either embedded or for this session)
    if not API_KEY or API_KEY == "INITIAL_PLACEHOLDER":
        print("ERROR: API Key is not configured. Please ensure the script setup ran correctly or reset it.", file=sys.stderr)
        sys.exit(1)

    # Check for query argument
    if len(sys.argv) < 2:
        print(f"\nUsage: {os.path.basename(sys.argv[0])} <your question>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    try:
        # Import the library now - it wasn't needed by the setup code itself
        from google import genai

        client = genai.Client(api_key=API_KEY)

        print(f"\nAsking Gemini (model: {MODEL_NAME}): {query}")
        print("---")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=query,
        )

        if hasattr(response, 'text') and response.text:
            print(response.text)
        elif hasattr(response, 'prompt_feedback'):
             print(f"Received no text content. Feedback: {response.prompt_feedback}")
        else:
            print("Received an empty or unexpected response.")

    except ImportError:
         print("\nERROR: The 'google-generativeai' library is not installed.", file=sys.stderr)
         print("Please install it using: pip install google-generativeai", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred during API call: {e}", file=sys.stderr)
        if "API key not valid" in str(e):
             print("The embedded API key might be invalid or revoked.", file=sys.stderr)
             print("You may need to manually edit the script to reset the API_KEY to 'INITIAL_PLACEHOLDER' and run again.", file=sys.stderr)
        sys.exit(1)
