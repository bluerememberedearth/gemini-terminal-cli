#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --- Permanent Imports & Initial Config ---
import os
import sys
import traceback # For debugging unexpected errors

# API Key will be permanently embedded here after first run.
# DO NOT MANUALLY EDIT THIS LINE UNLESS RESETTING!
API_KEY = "INITIAL_PLACEHOLDER" # This is the VALUE the variable holds initially
MODEL_NAME = "gemini-1.5-flash" # Or your preferred model
# --- End Permanent Imports & Initial Config ---


# --- START SELF-MODIFY/SETUP BLOCK (Will be removed after first run) ---

# Use the core marker text for startswith() check for robustness
_SETUP_BLOCK_START_MARKER_TEXT_ = "# --- START SELF-MODIFY/SETUP BLOCK"
_SETUP_BLOCK_END_MARKER_TEXT_ = "# --- END SELF-MODIFY/SETUP BLOCK"
# Define the exact placeholder line START for replacement within the file content
_API_KEY_PLACEHOLDER_LINE_START_ = 'API_KEY = "INITIAL_PLACEHOLDER"'
# Define the placeholder VALUE for checking the variable's content
_API_KEY_PLACEHOLDER_VALUE_ = "INITIAL_PLACEHOLDER"


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

    # --- ADDED DEBUG PRINT ---
    print(f"DEBUG: Inside setup, got new_key = '{new_key}'")
    # --- END DEBUG PRINT ---

    script_path = os.path.abspath(__file__)
    # Escape potential quotes in the key itself for the string representation
    new_key_escaped = new_key.replace('"', '\\"')
    new_key_line = f'API_KEY = "{new_key_escaped}" # Embedded by setup\n'

    original_api_key_value = API_KEY # Store original value for debugging prints

    try:
        print(f"\nReading current script: {script_path}")
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start_index = -1
        end_index = -1
        placeholder_line_index = -1

        print("Searching for markers and placeholder...")
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if start_index == -1 and stripped_line.startswith(_SETUP_BLOCK_START_MARKER_TEXT_):
                start_index = i
                print(f"Found start marker at line {i+1}")
            elif end_index == -1 and start_index != -1 and \
                 stripped_line.startswith(_SETUP_BLOCK_END_MARKER_TEXT_):
                end_index = i
                print(f"Found end marker at line {i+1}")
            # Use startswith for finding the placeholder line in the file
            elif placeholder_line_index == -1 and \
                 stripped_line.startswith(_API_KEY_PLACEHOLDER_LINE_START_):
                placeholder_line_index = i
                print(f"Found API Key placeholder line at index {i+1}")

        # Validate that markers were found correctly
        if start_index == -1 or end_index == -1:
            print("\nCRITICAL ERROR: Could not find setup block start and/or end markers.", file=sys.stderr)
            print("Expected markers to start with:", file=sys.stderr)
            print(f"Start: '{_SETUP_BLOCK_START_MARKER_TEXT_}'", file=sys.stderr)
            print(f"End:   '{_SETUP_BLOCK_END_MARKER_TEXT_}'", file=sys.stderr)
            print("Check the script file content. Cannot modify script. Aborting setup.", file=sys.stderr)
            print("Using entered key for this session only.", file=sys.stderr)
            print(f"DEBUG: Marker failure, BEFORE global assignment, API_KEY = '{original_api_key_value}'")
            API_KEY = new_key # Use for this session only
            print(f"DEBUG: Marker failure, AFTER global assignment, API_KEY = '{API_KEY}'")
            return False # Indicate setup failed

        if end_index <= start_index:
             print("\nCRITICAL ERROR: End marker found before or at the same line as start marker.", file=sys.stderr)
             print(f"Start Index: {start_index}, End Index: {end_index}", file=sys.stderr)
             print("Cannot modify script. Aborting setup.", file=sys.stderr)
             print("Using entered key for this session only.", file=sys.stderr)
             print(f"DEBUG: Marker order failure, BEFORE global assignment, API_KEY = '{original_api_key_value}'")
             API_KEY = new_key # Use for this session only
             print(f"DEBUG: Marker order failure, AFTER global assignment, API_KEY = '{API_KEY}'")
             return False # Indicate setup failed

        # Construct the new script content
        print("Constructing pruned script content...")
        new_lines = []
        new_lines.extend(lines[:start_index])

        placeholder_line_replaced = False # Flag to track if replacement happened
        if placeholder_line_index != -1:
            if placeholder_line_index < start_index:
                print(f"Replacing placeholder at index {placeholder_line_index} in the *new* list.")
                if placeholder_line_index < len(new_lines):
                     new_lines[placeholder_line_index] = new_key_line
                     placeholder_line_replaced = True
                else:
                     print("\nWARNING: Placeholder index seems out of bounds for replacement. Appending key.", file=sys.stderr)
                     new_lines.append(new_key_line) # Fallback, likely wrong place
            else:
                 print(f"\nWARNING: Placeholder line found at index {placeholder_line_index}, which is *inside or after* the setup block (starts at {start_index}). Key will not be embedded in the pruned script automatically.", file=sys.stderr)
                 # Fallback insertion logic remains the same

        # If placeholder line wasn't found and replaced, try fallback insertion
        if not placeholder_line_replaced:
             # Only warn if we actually expected to replace (i.e. script had placeholder value initially)
             if original_api_key_value == _API_KEY_PLACEHOLDER_VALUE_:
                 print("\nWARNING: Could not find or replace placeholder API_KEY line.", file=sys.stderr)
                 print(f"Expected line starting with: '{_API_KEY_PLACEHOLDER_LINE_START_}' before line {start_index + 1}", file=sys.stderr)
             print("Appending/Inserting new key line as fallback. Review script if issues occur.", file=sys.stderr)
             inserted_fallback = False
             for i, line in enumerate(new_lines): # Search in the already constructed part
                 if line.strip().startswith('# --- End Permanent Imports'):
                     new_lines.insert(i + 1, new_key_line)
                     inserted_fallback = True
                     print("Inserted API key as fallback after imports block.")
                     break
             if not inserted_fallback:
                 print("Could not find fallback insertion point. Appending key line.", file=sys.stderr)
                 new_lines.append(new_key_line) # Absolute fallback

        print(f"Appending lines from index {end_index + 1} onwards.")
        new_lines.extend(lines[end_index + 1:])

        # Overwrite the script with the new content
        print(f"Overwriting script file: {script_path} ({len(new_lines)} lines)")
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("Script successfully pruned and API key embedded.")
            print(f"DEBUG: Successful write, BEFORE global assignment, API_KEY = '{original_api_key_value}'")
            API_KEY = new_key # IMPORTANT: Set for the current run!
            print(f"DEBUG: Successful write, AFTER global assignment, API_KEY = '{API_KEY}'")
            return True # Indicate setup successful
        except (IOError, OSError) as e:
             print(f"\nERROR: Failed to write modified script file '{script_path}': {e}", file=sys.stderr)
             print("Script modification failed. File might be corrupted.", file=sys.stderr)
             print("Using entered key for this session only.", file=sys.stderr)
             print(f"DEBUG: Write failure, BEFORE global assignment, API_KEY = '{original_api_key_value}'")
             API_KEY = new_key # Use for this session only
             print(f"DEBUG: Write failure, AFTER global assignment, API_KEY = '{API_KEY}'")
             return False # Indicate setup failed

    except (IOError, OSError) as e:
        print(f"\nERROR: Failed to read script file '{script_path}': {e}", file=sys.stderr)
        print("Check file permissions. Script modification failed.", file=sys.stderr)
        print("Using entered key for this session only.", file=sys.stderr)
        print(f"DEBUG: Read failure EXCEPTION, BEFORE global assignment, API_KEY = '{original_api_key_value}'")
        API_KEY = new_key # Use for this session only
        print(f"DEBUG: Read failure EXCEPTION, AFTER global assignment, API_KEY = '{API_KEY}'")
        return False # Indicate setup failed
    except Exception as e:
        print(f"\nUNEXPECTED ERROR during script update: {e}", file=sys.stderr)
        traceback.print_exc() # Print full traceback for unexpected errors
        print("Using entered key for this session only.", file=sys.stderr)
        print(f"DEBUG: UNEXPECTED EXCEPTION, BEFORE global assignment, API_KEY = '{original_api_key_value}'")
        API_KEY = new_key # Use for this session only
        print(f"DEBUG: UNEXPECTED EXCEPTION, AFTER global assignment, API_KEY = '{API_KEY}'")
        return False # Indicate setup failed

# --- CORRECTED CHECK ---
# Check if setup needs to run by comparing the VARIABLE'S VALUE
print(f"DEBUG: Before setup check, API_KEY = '{API_KEY}'")
if API_KEY == _API_KEY_PLACEHOLDER_VALUE_:
    print("DEBUG: Running setup...")
    setup_success = _perform_first_run_setup()
    print(f"DEBUG: Setup function returned: {setup_success}")
    print(f"DEBUG: Immediately after setup call, API_KEY = '{API_KEY}'") # Crucial check
    if not setup_success:
        # If setup failed critically check the CURRENT VALUE of API_KEY
        if API_KEY == _API_KEY_PLACEHOLDER_VALUE_:
             print("\nExiting due to critical setup failure (API key still placeholder).", file=sys.stderr)
             sys.exit(1)
        else:
             print("\nDEBUG: Setup failed, but API key seems set for this session. Continuing...")
    print("\nFirst run setup complete. Reloading script logic might be needed if run via import.")
    print("Continuing with query for this execution...")
else:
    print("DEBUG: Setup not required.")
# --- END CORRECTED CHECK ---

# --- END SELF-MODIFY/SETUP BLOCK (This marker and the block above are removed) ---

print(f"DEBUG: Before __main__ block, API_KEY = '{API_KEY}'")

# --- Core API Access Logic (Permanent) ---
if __name__ == "__main__":

    print(f"DEBUG: Inside __main__, checking API_KEY = '{API_KEY}'")
    # --- CORRECTED CHECK ---
    # Ensure API key is set (should be by now, either embedded or for this session)
    # Just check if it's empty or still the placeholder VALUE
    if not API_KEY or API_KEY == "INITIAL_PLACEHOLDER":
        print("ERROR: API Key is not configured.", file=sys.stderr)
        print("Please ensure the script setup ran correctly or reset the API_KEY line manually", file=sys.stderr)
        sys.exit(1)
    # --- END CORRECTED CHECK ---

    # Check for query argument
    if len(sys.argv) < 2:
        print(f"\nUsage: {os.path.basename(sys.argv[0])} <your question>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    try:
        # Import the library now - it wasn't needed by the setup code itself
        import google.generativeai as genai

        # Configure the client using the API_KEY variable
        genai.configure(api_key=API_KEY)

        print(f"\nAsking Gemini (model: {MODEL_NAME}): {query}")
        print("---")

        # Create the model instance
        model = genai.GenerativeModel(MODEL_NAME)

        # Generate content
        response = model.generate_content(query)

        # Accessing response
        try:
             print(response.text)
        except ValueError:
             print("Response was blocked:")
             if hasattr(response, 'prompt_feedback'):
                 print(response.prompt_feedback)
             else:
                 print("(No feedback available)")
        except AttributeError:
              if hasattr(response, 'prompt_feedback'):
                   print(f"Received no text content. Feedback: {response.prompt_feedback}")
              else:
                   print("Received an empty or unexpected response structure.")
                   print(f"Raw response parts: {response.parts if hasattr(response, 'parts') else 'N/A'}")

    except ImportError:
         print("\nERROR: The 'google-generativeai' library is not installed.", file=sys.stderr)
         print("Please install it using: pip install google-generativeai", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred during API call: {e}", file=sys.stderr)
        traceback.print_exc()
        err_str = str(e).lower()
        if "api key not valid" in err_str or "permission denied" in err_str or "authenticate" in err_str:
             print("Authentication error: The embedded API key might be invalid, expired, or lack permissions.", file=sys.stderr)
             print("You may need to manually edit the script to reset the API_KEY to 'INITIAL_PLACEHOLDER' and run again.", file=sys.stderr)
        elif "quota" in err_str:
             print("API quota exceeded. Please check your Google AI Studio usage limits.", file=sys.stderr)
        sys.exit(1)
