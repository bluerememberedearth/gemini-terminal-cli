#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --- Permanent Imports & Initial Config ---
import os
import sys
import traceback # For debugging unexpected errors
# NOTE: tempfile is only imported within the setup function below now

# API Key will be permanently embedded here after first run.
# DO NOT MANUALLY EDIT THIS LINE UNLESS RESETTING!
API_KEY = "INITIAL_PLACEHOLDER" # This is the VALUE the variable holds initially
MODEL_NAME = "gemini-2.5-pro-exp-03-25" # Or your preferred model
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
    """Prompts for API key, embeds it atomically, and removes this setup block."""
    global API_KEY # Needed to set the key for the current run
    # Import tempfile only when needed for setup
    import tempfile

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
    script_dir = os.path.dirname(script_path) # Needed for temp file location

    # Use repr() for safer string literal creation including quotes/escapes
    new_key_line = f'API_KEY = {repr(new_key)} # Embedded by setup\n'

    original_api_key_value = API_KEY # Store original value for debugging prints
    temp_path = None # Initialize temporary path variable

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
            # ... (rest of marker error handling as before) ...
            print("Using entered key for this session only.", file=sys.stderr)
            API_KEY = new_key
            return False

        if end_index <= start_index:
             print("\nCRITICAL ERROR: End marker found before or at the same line as start marker.", file=sys.stderr)
             # ... (rest of marker order error handling as before) ...
             print("Using entered key for this session only.", file=sys.stderr)
             API_KEY = new_key
             return False

        # Construct the new script content
        print("Constructing pruned script content...")
        new_lines = []
        new_lines.extend(lines[:start_index])

        placeholder_line_replaced = False
        if placeholder_line_index != -1:
            if placeholder_line_index < start_index:
                print(f"Replacing placeholder at index {placeholder_line_index} in the *new* list.")
                if placeholder_line_index < len(new_lines):
                     # Use the repr()-based line here
                     new_lines[placeholder_line_index] = new_key_line
                     placeholder_line_replaced = True
                # ... (rest of placeholder handling as before) ...
            else:
                 print(f"\nWARNING: Placeholder line found at index {placeholder_line_index}, which is *inside or after* the setup block (starts at {start_index}). Key will not be embedded in the pruned script automatically.", file=sys.stderr)

        if not placeholder_line_replaced:
             if original_api_key_value == _API_KEY_PLACEHOLDER_VALUE_:
                 print("\nWARNING: Could not find or replace placeholder API_KEY line.", file=sys.stderr)
                 print(f"Expected line starting with: '{_API_KEY_PLACEHOLDER_LINE_START_}' before line {start_index + 1}", file=sys.stderr)
             print("Appending/Inserting new key line as fallback. Review script if issues occur.", file=sys.stderr)
             inserted_fallback = False
             for i, line in enumerate(new_lines):
                 if line.strip().startswith('# --- End Permanent Imports'):
                     # Use the repr()-based line here too
                     new_lines.insert(i + 1, new_key_line)
                     inserted_fallback = True
                     print("Inserted API key as fallback after imports block.")
                     break
             if not inserted_fallback:
                 print("Could not find fallback insertion point. Appending key line.", file=sys.stderr)
                 new_lines.append(new_key_line) # Absolute fallback

        print(f"Appending lines from index {end_index + 1} onwards.")
        new_lines.extend(lines[end_index + 1:])

        # --- ATOMIC WRITE IMPLEMENTATION ---
        # Create a temporary file in the same directory as the script
        # This makes os.replace more likely to be atomic
        temp_fd, temp_path = tempfile.mkstemp(suffix=".tmp", dir=script_dir, text=True)
        print(f"Writing modified content to temporary file: {temp_path} ({len(new_lines)} lines)")

        try:
            # Write the new content to the temporary file
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f_temp:
                f_temp.writelines(new_lines)
            # Ensure temporary file is closed and flushed before replacement

            # Atomically replace the original script with the temporary file
            print(f"Attempting to atomically replace '{script_path}' with '{temp_path}'")
            os.replace(temp_path, script_path)
            # If os.replace succeeds, temp_path no longer exists (it became script_path)
            temp_path = None # Indicate successful replacement (temp file gone)

            print("Script successfully pruned, API key embedded, and file replaced.")
            API_KEY = new_key # IMPORTANT: Set for the current run!
            return True # Indicate setup successful

        except (IOError, OSError) as e:
             print(f"\nERROR: Failed during script modification (write/replace): {e}", file=sys.stderr)
             print(f"Original script '{script_path}' should be untouched.", file=sys.stderr)
             print("Using entered key for this session only.", file=sys.stderr)
             API_KEY = new_key # Use for this session only
             return False # Indicate setup failed
        finally:
             # Clean up the temporary file *only* if it still exists (i.e., os.replace failed or was never reached)
             if temp_path and os.path.exists(temp_path):
                 print(f"Cleaning up temporary file: {temp_path}")
                 try:
                     os.remove(temp_path)
                 except OSError as cleanup_e:
                     print(f"Warning: Failed to clean up temporary file '{temp_path}': {cleanup_e}", file=sys.stderr)
        # --- END ATOMIC WRITE IMPLEMENTATION ---

    except (IOError, OSError) as e:
        print(f"\nERROR: Failed to read script file '{script_path}': {e}", file=sys.stderr)
        print("Check file permissions. Script modification failed.", file=sys.stderr)
        print("Using entered key for this session only.", file=sys.stderr)
        API_KEY = new_key # Use for this session only
        return False # Indicate setup failed
    except Exception as e:
        print(f"\nUNEXPECTED ERROR during script update: {e}", file=sys.stderr)
        traceback.print_exc() # Print full traceback for unexpected errors
        # Cleanup temp file if created and an unexpected error occurred before replacement
        if temp_path and os.path.exists(temp_path):
             print(f"Cleaning up temporary file due to unexpected error: {temp_path}")
             try:
                 os.remove(temp_path)
             except OSError as cleanup_e:
                 print(f"Warning: Failed to clean up temporary file '{temp_path}': {cleanup_e}", file=sys.stderr)
        print("Using entered key for this session only.", file=sys.stderr)
        API_KEY = new_key # Use for this session only
        return False # Indicate setup failed

# --- CORRECTED CHECK ---
# (The rest of the script remains the same as your previous version)
# Check if setup needs to run by comparing the VARIABLE'S VALUE
if API_KEY == _API_KEY_PLACEHOLDER_VALUE_:
    setup_success = _perform_first_run_setup()
    if not setup_success:
        # If setup failed critically check the CURRENT VALUE of API_KEY
        if API_KEY == _API_KEY_PLACEHOLDER_VALUE_:
             print("\nExiting due to critical setup failure (API key still placeholder).", file=sys.stderr)
             sys.exit(1)
    print("\nFirst run setup complete. Reloading script logic might be needed if run via import.")
    print("Continuing with query for this execution...")
else:
# --- END CORRECTED CHECK ---

# --- END SELF-MODIFY/SETUP BLOCK (This marker and the block above are removed) ---


# --- Core API Access Logic (Permanent) ---
# (This section remains unchanged)
if __name__ == "__main__":

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
