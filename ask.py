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

# Use the core marker text for startswith() check for robustness
_SETUP_BLOCK_START_MARKER_TEXT_ = "# --- START SELF-MODIFY/SETUP BLOCK"
_SETUP_BLOCK_END_MARKER_TEXT_ = "# --- END SELF-MODIFY/SETUP BLOCK"
# Define the exact placeholder line for replacement
_API_KEY_PLACEHOLDER_LINE_START_ = 'API_KEY = "INITIAL_PLACEHOLDER"'


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
    # Escape potential quotes in the key itself for the string representation
    new_key_escaped = new_key.replace('"', '\\"')
    new_key_line = f'API_KEY = "{new_key_escaped}" # Embedded by setup\n'

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

            # Find Start Marker (only the first occurrence)
            if start_index == -1 and stripped_line.startswith(_SETUP_BLOCK_START_MARKER_TEXT_):
                start_index = i
                print(f"Found start marker at line {i+1}")

            # Find End Marker (only the first occurrence after start marker)
            # This ensures we get the correct block if markers are somehow duplicated
            elif end_index == -1 and start_index != -1 and \
                 stripped_line.startswith(_SETUP_BLOCK_END_MARKER_TEXT_):
                end_index = i
                print(f"Found end marker at line {i+1}")
                # Optimization: we can potentially break here if we don't care about finding
                # the placeholder *after* the end marker (which it shouldn't be).
                # However, searching the whole file first is safer.

            # Find Placeholder Line (only the first occurrence)
            elif placeholder_line_index == -1 and \
                 stripped_line.startswith(_API_KEY_PLACEHOLDER_LINE_START_):
                placeholder_line_index = i
                print(f"Found API Key placeholder at line {i+1}")

        # Validate that markers were found correctly
        if start_index == -1 or end_index == -1:
            print("\nCRITICAL ERROR: Could not find setup block start and/or end markers.", file=sys.stderr)
            print("Expected markers to start with:", file=sys.stderr)
            print(f"Start: '{_SETUP_BLOCK_START_MARKER_TEXT_}'", file=sys.stderr)
            print(f"End:   '{_SETUP_BLOCK_END_MARKER_TEXT_}'", file=sys.stderr)
            print("Check the script file content. Cannot modify script. Aborting setup.", file=sys.stderr)
            print("Using entered key for this session only.", file=sys.stderr)
            API_KEY = new_key # Use for this session only
            return False # Indicate setup failed

        if end_index <= start_index:
             print("\nCRITICAL ERROR: End marker found before or at the same line as start marker.", file=sys.stderr)
             print(f"Start Index: {start_index}, End Index: {end_index}", file=sys.stderr)
             print("Cannot modify script. Aborting setup.", file=sys.stderr)
             print("Using entered key for this session only.", file=sys.stderr)
             API_KEY = new_key # Use for this session only
             return False # Indicate setup failed

        # Construct the new script content
        print("Constructing pruned script content...")
        new_lines = []

        # 1. Keep lines before the setup block
        new_lines.extend(lines[:start_index])

        # 2. Replace the placeholder line IF it was found BEFORE the setup block
        if placeholder_line_index != -1:
            if placeholder_line_index < start_index:
                print(f"Replacing placeholder at index {placeholder_line_index} in the *new* list.")
                # Adjust index because new_lines only contains lines[:start_index]
                if placeholder_line_index < len(new_lines):
                     new_lines[placeholder_line_index] = new_key_line
                else:
                     # This case should ideally not happen if placeholder is before start_index
                     print("\nWARNING: Placeholder index seems out of bounds for replacement. Appending key.", file=sys.stderr)
                     new_lines.append(new_key_line) # Fallback, might be wrong place
            else:
                 print(f"\nWARNING: Placeholder line found at index {placeholder_line_index}, which is *inside or after* the setup block (starts at {start_index}). Key will not be embedded in the pruned script automatically.", file=sys.stderr)
                 # Add the key line after the permanent imports as a fallback
                 # Find insert position again in the final list
                 inserted_fallback = False
                 for i, line in enumerate(new_lines):
                     if line.strip().startswith('# --- End Permanent Imports'):
                         new_lines.insert(i + 1, new_key_line)
                         inserted_fallback = True
                         print("Inserted API key as fallback after imports block.")
                         break
                 if not inserted_fallback:
                     print("Could not find fallback insertion point. Appending key line.", file=sys.stderr)
                     new_lines.append(new_key_line) # Absolute fallback

        elif API_KEY == "INITIAL_PLACEHOLDER": # Only warn if we expected to replace it
             print("\nWARNING: Could not find placeholder API_KEY line to replace.", file=sys.stderr)
             print(f"Expected line starting with: '{_API_KEY_PLACEHOLDER_LINE_START_}'", file=sys.stderr)
             print("Appending new key line after imports as fallback. Review script if issues occur.", file=sys.stderr)
             # Add the key line after the permanent imports as a fallback
             inserted_fallback = False
             for i, line in enumerate(new_lines):
                 if line.strip().startswith('# --- End Permanent Imports'):
                     new_lines.insert(i + 1, new_key_line)
                     inserted_fallback = True
                     print("Inserted API key as fallback after imports block.")
                     break
             if not inserted_fallback:
                 print("Could not find fallback insertion point. Appending key line.", file=sys.stderr)
                 new_lines.append(new_key_line) # Absolute fallback

        # 3. Keep lines after the setup block (includes the end marker line itself)
        #    Correct slicing is lines[end_index + 1:] to EXCLUDE the end marker line
        print(f"Appending lines from index {end_index + 1} onwards.")
        new_lines.extend(lines[end_index + 1:])

        # Overwrite the script with the new content
        # WARNING: Not atomic! Interruption can corrupt the file.
        print(f"Overwriting script file: {script_path} ({len(new_lines)} lines)")
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("Script successfully pruned and API key embedded.")
            API_KEY = new_key # IMPORTANT: Set for the current run!
            return True # Indicate setup successful
        except (IOError, OSError) as e:
             print(f"\nERROR: Failed to write modified script file '{script_path}': {e}", file=sys.stderr)
             # Attempt to restore from original lines if possible? Risky.
             print("Script modification failed. File might be corrupted.", file=sys.stderr)
             print("Using entered key for this session only.", file=sys.stderr)
             API_KEY = new_key # Use for this session only
             return False # Indicate setup failed


    except (IOError, OSError) as e:
        print(f"\nERROR: Failed to read script file '{script_path}': {e}", file=sys.stderr)
        print("Check file permissions. Script modification failed.", file=sys.stderr)
        print("Using entered key for this session only.", file=sys.stderr)
        API_KEY = new_key # Use for this session only
        return False # Indicate setup failed
    except Exception as e:
        print(f"\nUNEXPECTED ERROR during script update: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc() # Print full traceback for unexpected errors
        print("Using entered key for this session only.", file=sys.stderr)
        API_KEY = new_key # Use for this session only
        return False # Indicate setup failed

# Check if setup needs to run (only happens if placeholder is present)
# Make this check slightly more robust in case the line was modified slightly
if 'API_KEY = "INITIAL_PLACEHOLDER"' in API_KEY: # Check substring just in case
    if not _perform_first_run_setup():
        # If setup failed critically and couldn't even set the key for this session
        if 'API_KEY = "INITIAL_PLACEHOLDER"' in API_KEY:
             print("\nExiting due to critical setup failure.", file=sys.stderr)
             sys.exit(1)
    # Pause briefly after modification before continuing
    print("\nFirst run setup complete. Reloading script logic might be needed if run via import.")
    print("Continuing with query for this execution...")
    # If running directly (./script.py), the rest of the script will execute.
    # If imported, the calling code might need to re-import to see changes.

# --- END SELF-MODIFY/SETUP BLOCK (This marker and the block above are removed) ---


# --- Core API Access Logic (Permanent) ---
if __name__ == "__main__":

    # Ensure API key is set (should be by now, either embedded or for this session)
    # Check against placeholder again, just in case setup logic had issues but didn't exit
    if not API_KEY or API_KEY == "INITIAL_PLACEHOLDER" or 'API_KEY = "INITIAL_PLACEHOLDER"' in API_KEY:
        print("ERROR: API Key is not configured.", file=sys.stderr)
        print("Please ensure the script setup ran correctly or reset the API_KEY line manually", file=sys.stderr)
        print("to: API_KEY = \"INITIAL_PLACEHOLDER\"", file=sys.stderr)
        sys.exit(1)

    # Check for query argument
    if len(sys.argv) < 2:
        print(f"\nUsage: {os.path.basename(sys.argv[0])} <your question>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    try:
        # Import the library now - it wasn't needed by the setup code itself
        import google.generativeai as genai # Use alias for clarity

        # Configure the client using the API_KEY variable
        # google.generativeai configure call is simpler if you don't need multiple clients
        genai.configure(api_key=API_KEY)

        print(f"\nAsking Gemini (model: {MODEL_NAME}): {query}")
        print("---")

        # Create the model instance
        model = genai.GenerativeModel(MODEL_NAME)

        # Generate content (simpler API)
        response = model.generate_content(query)

        # Accessing response differs slightly in newer versions
        try:
             print(response.text)
        except ValueError:
             # If the response was blocked, accessing .text raises ValueError
             print("Response was blocked:")
             print(response.prompt_feedback)
        except AttributeError:
              # Handle cases where response might not have .text (e.g., error)
              if hasattr(response, 'prompt_feedback'):
                   print(f"Received no text content. Feedback: {response.prompt_feedback}")
              else:
                   print("Received an empty or unexpected response structure.")
                   print(f"Raw response: {response}")


    except ImportError:
         print("\nERROR: The 'google-generativeai' library is not installed.", file=sys.stderr)
         print("Please install it using: pip install google-generativeai", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred during API call: {e}", file=sys.stderr)
        # Check common API key errors
        err_str = str(e).lower()
        if "api key not valid" in err_str or "permission denied" in err_str or "authenticate" in err_str:
             print("Authentication error: The embedded API key might be invalid, expired, or lack permissions.", file=sys.stderr)
             print("You may need to manually edit the script to reset the API_KEY to 'INITIAL_PLACEHOLDER' and run again.", file=sys.stderr)
        # Add specific check for quota exceeded if needed
        elif "quota" in err_str:
             print("API quota exceeded. Please check your Google AI Studio usage limits.", file=sys.stderr)
        sys.exit(1)
