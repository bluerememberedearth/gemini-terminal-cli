#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --- Permanent Genome Sequence & Initial Config ---
import os
import sys
import time
import traceback # For debugging unexpected errors
# NOTE: tempfile (RNA template tooling) is only imported during activation

# Functional Gene Sequence (API Key) will be permanently embedded here after activation.
# DO NOT MANUALLY EDIT THIS LINE UNLESS RESETTING GENOME!
GENE_SEQUENCE = "INERT_SEQUENCE_PLACEHOLDER" # This is the VALUE the variable holds initially
#TODO - how to make it so requested model is always the latest available?
GENOME_MODEL_ID = "gemini-2.5-pro-exp-03-25" # Or your preferred model (target protein ID)
# --- End Permanent Genome Sequence & Initial Config ---


# --- START GENOME ACTIVATION SCAFFOLD (Will be spliced out after first run) ---

# Use the core marker text for startswith() check for robustness
_ACTIVATION_SCAFFOLD_START_MARKER_ = "# --- START GENOME ACTIVATION SCAFFOLD"
_ACTIVATION_SCAFFOLD_END_MARKER_ = "# --- END GENOME ACTIVATION SCAFFOLD"
# Define the exact placeholder line START for replacement within the genome file content
_GENE_SEQUENCE_PLACEHOLDER_SITE_ = 'GENE_SEQUENCE = "INERT_SEQUENCE_PLACEHOLDER"'
# Define the placeholder VALUE for checking the variable's content
_INERT_SEQUENCE_PLACEHOLDER_ = "INERT_SEQUENCE_PLACEHOLDER"


def _perform_genome_activation():
    """Prompts for functional gene sequence (API key), embeds it atomically into the genome (script),
       and removes this activation scaffold."""
    global GENE_SEQUENCE # Needed to set the sequence for the current execution cycle
    # Import RNA template tooling (tempfile) only when needed for activation
    import tempfile

    print("-" * 30)
    print("First execution: Genome activation required (Google AI Gene Sequence).")
    print("Your functional sequence will be embedded, and activation scaffold removed.")
    print("Acquire sequence: https://aistudio.google.com/app/apikey")
    print("-" * 30)

    new_gene_sequence = ""
    while not new_gene_sequence:
        new_gene_sequence = input("Enter your Google AI Gene Sequence (API Key): ").strip()
        if not new_gene_sequence:
            print("Gene sequence cannot be empty.")

    genome_file_path = os.path.abspath(__file__)
    genome_directory = os.path.dirname(genome_file_path) # Needed for RNA template location

    # Use repr() for safer string literal creation including quotes/escapes
    new_gene_line = f'GENE_SEQUENCE = {repr(new_gene_sequence)} # Embedded by activation\n'

    original_gene_sequence_value = GENE_SEQUENCE # Store original value for debugging prints
    rna_template_path = None # Initialize temporary RNA template path variable

    try:
        print(f"\nReading current genome: {genome_file_path}")
        with open(genome_file_path, 'r', encoding='utf-8') as f_genome:
            genome_lines = f_genome.readlines()

        scaffold_start_locus = -1
        scaffold_end_locus = -1
        placeholder_site_locus = -1

        print("Scanning genome for markers and placeholder site...")
        for i, line in enumerate(genome_lines):
            stripped_line = line.strip()
            if scaffold_start_locus == -1 and stripped_line.startswith(_ACTIVATION_SCAFFOLD_START_MARKER_):
                scaffold_start_locus = i
                print(f"Found activation scaffold start marker at locus {i+1}")
            elif scaffold_end_locus == -1 and scaffold_start_locus != -1 and \
                 stripped_line.startswith(_ACTIVATION_SCAFFOLD_END_MARKER_):
                scaffold_end_locus = i
                print(f"Found activation scaffold end marker at locus {i+1}")
            # Use startswith for finding the placeholder line in the genome file
            elif placeholder_site_locus == -1 and \
                 stripped_line.startswith(_GENE_SEQUENCE_PLACEHOLDER_SITE_):
                placeholder_site_locus = i
                print(f"Found Gene Sequence placeholder site at locus {i+1}")

        # Validate that markers were found correctly
        if scaffold_start_locus == -1 or scaffold_end_locus == -1:
            print("\nCRITICAL ERROR: Could not find activation scaffold start and/or end markers.", file=sys.stderr)
            print(f"Expected markers: '{_ACTIVATION_SCAFFOLD_START_MARKER_}' and '{_ACTIVATION_SCAFFOLD_END_MARKER_}'", file=sys.stderr)
            print("Genome modification aborted. Using entered sequence for this session only.", file=sys.stderr)
            GENE_SEQUENCE = new_gene_sequence
            return False

        if scaffold_end_locus <= scaffold_start_locus:
             print("\nCRITICAL ERROR: End marker found before or at the same locus as start marker.", file=sys.stderr)
             print(f"Start Locus: {scaffold_start_locus+1}, End Locus: {scaffold_end_locus+1}", file=sys.stderr)
             print("Genome modification aborted. Using entered sequence for this session only.", file=sys.stderr)
             GENE_SEQUENCE = new_gene_sequence
             return False

        # Construct the new, activated genome content (splicing out the scaffold)
        print("Constructing modified genome sequence...")
        modified_genome_lines = []
        modified_genome_lines.extend(genome_lines[:scaffold_start_locus]) # Keep lines before scaffold

        placeholder_site_replaced = False
        if placeholder_site_locus != -1:
             # Check if the placeholder was *before* the scaffold (where it should be)
             if placeholder_site_locus < scaffold_start_locus:
                 print(f"Replacing placeholder at original locus {placeholder_site_locus+1} in the *new* sequence list.")
                 if placeholder_site_locus < len(modified_genome_lines):
                     # Use the repr()-based line here for the functional sequence
                     modified_genome_lines[placeholder_site_locus] = new_gene_line
                     placeholder_site_replaced = True
                 else:
                    print(f"\nERROR: Placeholder locus {placeholder_site_locus} seems out of bounds for the pre-scaffold section (length {len(modified_genome_lines)}). This should not happen.", file=sys.stderr)

             else:
                 # Placeholder was inside or after the scaffold - it will be removed by splicing.
                 print(f"\nWARNING: Placeholder site found at locus {placeholder_site_locus+1}, which is *inside or after* the activation scaffold (starts at {scaffold_start_locus+1}). Sequence will not be embedded in the spliced genome automatically.", file=sys.stderr)

        # If placeholder wasn't found and replaced in the pre-scaffold section
        if not placeholder_site_replaced:
             # Only warn loudly if the placeholder *value* was still the default
             if original_gene_sequence_value == _INERT_SEQUENCE_PLACEHOLDER_:
                 print("\nWARNING: Could not find or replace placeholder GENE_SEQUENCE line before the scaffold.", file=sys.stderr)
                 print(f"Expected line starting with: '{_GENE_SEQUENCE_PLACEHOLDER_SITE_}' before locus {scaffold_start_locus + 1}", file=sys.stderr)
             # Fallback: Try to insert the new sequence line after the imports block
             print("Attempting to insert new gene sequence line as fallback. Review genome script if issues occur.", file=sys.stderr)
             inserted_fallback = False
             # Find a suitable insertion point (e.g., after the permanent config block)
             fallback_marker_end = '# --- End Permanent Genome Sequence & Initial Config ---'
             for i, line in enumerate(modified_genome_lines):
                 if line.strip().startswith(fallback_marker_end):
                     # Use the repr()-based line here too
                     modified_genome_lines.insert(i + 1, new_gene_line)
                     inserted_fallback = True
                     print(f"Inserted gene sequence as fallback after '{fallback_marker_end}' marker.")
                     break
             if not inserted_fallback:
                 print("Could not find fallback insertion point. Appending gene sequence line to end of pre-scaffold section.", file=sys.stderr)
                 modified_genome_lines.append(new_gene_line) # Absolute fallback

        # Append the part of the genome *after* the scaffold
        print(f"Appending genome sequence from locus {scaffold_end_locus + 2} onwards.")
        modified_genome_lines.extend(genome_lines[scaffold_end_locus + 1:])

        # --- ATOMIC GENOME REPLICATION/REPLACEMENT ---
        # Create a temporary RNA template in the same directory as the genome
        # This makes os.replace more likely to be atomic
        rna_template_fd, rna_template_path = tempfile.mkstemp(suffix=".rna.tmp", dir=genome_directory, text=True)
        print(f"Writing modified genome to RNA template: {rna_template_path} ({len(modified_genome_lines)} lines)")

        try:
            # Write the new genome content to the RNA template
            with os.fdopen(rna_template_fd, 'w', encoding='utf-8') as f_rna:
                f_rna.writelines(modified_genome_lines)
            # Ensure RNA template file is closed and flushed before replacement

            # Atomically replace the original genome script with the RNA template
            print(f"Attempting to atomically replace genome '{genome_file_path}' with template '{rna_template_path}'")
            os.replace(rna_template_path, genome_file_path)
            # If os.replace succeeds, rna_template_path no longer exists (it became genome_file_path)
            rna_template_path = None # Indicate successful replacement (RNA template integrated)

            print("Genome successfully activated: scaffold spliced, gene sequence embedded, file replaced.")
            GENE_SEQUENCE = new_gene_sequence # IMPORTANT: Set sequence for the current execution cycle!
            return True # Indicate activation successful

        except (IOError, OSError) as e:
             print(f"\nERROR: Failed during genome modification (RNA template write/replace): {e}", file=sys.stderr)
             print(f"Original genome '{genome_file_path}' should be untouched.", file=sys.stderr)
             print("Using entered sequence for this session only.", file=sys.stderr)
             GENE_SEQUENCE = new_gene_sequence # Use for this session only
             return False # Indicate activation failed
        finally:
             # Clean up the RNA template file *only* if it still exists (i.e., os.replace failed or was never reached)
             if rna_template_path and os.path.exists(rna_template_path):
                 print(f"Cleaning up temporary RNA template: {rna_template_path}")
                 try:
                     os.remove(rna_template_path)
                 except OSError as cleanup_e:
                     print(f"Warning: Failed to clean up temporary RNA template '{rna_template_path}': {cleanup_e}", file=sys.stderr)
        # --- END ATOMIC GENOME REPLICATION/REPLACEMENT ---

    except (IOError, OSError) as e:
        print(f"\nERROR: Failed to read genome file '{genome_file_path}': {e}", file=sys.stderr)
        print("Check file permissions. Genome activation failed.", file=sys.stderr)
        print("Using entered sequence for this session only.", file=sys.stderr)
        GENE_SEQUENCE = new_gene_sequence # Use for this session only
        return False # Indicate activation failed
    except Exception as e:
        print(f"\nUNEXPECTED ERROR during genome activation: {e}", file=sys.stderr)
        traceback.print_exc() # Print full traceback for unexpected errors
        # Cleanup RNA template if created and an unexpected error occurred before replacement
        if rna_template_path and os.path.exists(rna_template_path):
             print(f"Cleaning up RNA template due to unexpected error: {rna_template_path}")
             try:
                 os.remove(rna_template_path)
             except OSError as cleanup_e:
                 print(f"Warning: Failed to clean up temporary RNA template '{rna_template_path}': {cleanup_e}", file=sys.stderr)
        print("Using entered sequence for this session only.", file=sys.stderr)
        GENE_SEQUENCE = new_gene_sequence # Use for this session only
        return False # Indicate activation failed

# --- ACTIVATION CHECK ---
# Check if activation needs to run by comparing the GENE_SEQUENCE'S VALUE (is it inert?)
if GENE_SEQUENCE == _INERT_SEQUENCE_PLACEHOLDER_:
    activation_successful = _perform_genome_activation()
    if not activation_successful:
        if GENE_SEQUENCE == "INERT_SEQUENCE_PLACEHOLDER":
             print("\nExiting due to critical activation failure (Gene sequence still inert placeholder).", file=sys.stderr)
             sys.exit(1)
    print("\nGenome activation process complete. Reloading script logic might be needed if run via import.")
    print("Continuing with expression trigger for this execution cycle...")
# --- END ACTIVATION CHECK ---

# --- END GENOME ACTIVATION SCAFFOLD (This marker and the block above are removed) ---


# --- Core Gene Expression Logic (Permanent) ---
# (This section remains unchanged in function)
if __name__ == "__main__":

    # --- POST-ACTIVATION CHECK ---
    # Ensure functional gene sequence is set (should be by now, either embedded or for this session)
    # Just check if it's empty or still the inert placeholder VALUE
    if not GENE_SEQUENCE or GENE_SEQUENCE == "INERT_SEQUENCE_PLACEHOLDER":
        print("ERROR: Functional Gene Sequence (API Key) is not configured.", file=sys.stderr)
        print("Please ensure genome activation ran correctly or reset the GENE_SEQUENCE line manually to the placeholder.", file=sys.stderr)
        sys.exit(1)
    # --- END POST-ACTIVATION CHECK ---

    # Check for expression trigger (query argument)
    if len(sys.argv) < 2:
        print(f"\nUsage: {os.path.basename(sys.argv[0])} <expression_trigger_query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:]) # The external stimulus

    try:
        # Import the expression machinery library now - wasn't needed for activation
        from google.api_core import exceptions
        from google import genai

        # Configure the expression client using the embedded GENE_SEQUENCE
        genai.configure(api_key=GENE_SEQUENCE)

        print(f"\nTriggering expression via Gemini (model: {GENOME_MODEL_ID}): {query}")
        print("---")

        # Create the expression model instance
        expression_model = genai.GenerativeModel(GENOME_MODEL_ID)

        first_segment_received = False
        start_time = time.time()
        accumulated_segments = ""
        
        # Generate the expression result (protein/response)
        expression_stream = expression_model.generate_content(
            query,
            stream=True, 
            request_options={'timeout': 60}
        )

        for segment in expression_stream:
            if not first_segment_received:
                first_segment_time = time.time()
                print(f"First segment received in {first_segment_time - start_time:.2f} seconds.")
                print("Receiving stream: ", end="", flush=True)
            first_segment_received = True

            try:
                print(segment.text, end="", flush=True)
                accumulated_segments += segment.text
            except ValueError:
                print("[Blocked segment or No fragment]", end="", flush=True)
            except Exception as e:
                print(f"\n[Error processing segment: {e}]", end="", flush=True)

        print("\n--- Stream Finished ---")
        stream_finished_without_error = True
        end_time = time.time()
        print(f"Stream finished in {end_time - start_time:.2f} seconds.")
        
        try:
            final_prompt_feedback = expression_stream.prompt_feedback
        except Exception:
            print("Could not retrieve final prompt feedback from the stream.")
    
    except Exception as e:
        print(f"\nAn error occurred during gene expression (API call): {e}", file=sys.stderr)
        traceback.print_exc()
        err_str = str(e).lower()
        # Check for errors related to the embedded gene sequence
        if "api key not valid" in err_str or "permission denied" in err_str or "authenticate" in err_str:
             print("Authentication error: The embedded Gene Sequence might be invalid, expired, or lack permissions.", file=sys.stderr)
             print("You may need to manually edit the genome script to reset the GENE_SEQUENCE to 'INERT_SEQUENCE_PLACEHOLDER' and run activation again.", file=sys.stderr)
        elif "quota" in err_str:
             print("Expression quota exceeded. Please check your Google AI Studio usage limits.", file=sys.stderr)
        sys.exit(1)
