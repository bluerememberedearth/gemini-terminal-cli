#!/usr/bin/env python3
# ^^^ Add this line for Unix/macOS if using Method 2B or 2C below

import os
import sys
from google import genai
# Optional: Load .env file if you're using one
# from dotenv import load_dotenv
# load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    sys.exit(1) # Exit with an error code

# Check if any arguments (the query) were provided
if len(sys.argv) < 2:
    print("Usage: ask <your question>")
    sys.exit(1)

# Join all arguments after the script name into a single query string
query = " ".join(sys.argv[1:])

# Configure the client
client = genai.Client(api_key=api_key)

# Define the model (adjust if needed)
model_name = "gemini-1.5-flash" # Or "gemini-2.0-flash" if available/preferred

try:
    print(f"Asking Gemini (model: {model_name}): {query}")
    print("---") # Separator

    response = client.models.generate_content(
        model=model_name,
        contents=query,
    )

    # Add basic check for response content
    if response.text:
        print(response.text)
    else:
        # This might happen due to safety filters, etc.
        # You can inspect response.prompt_feedback for details
        print("Received an empty response.")
        # print(f"Prompt Feedback: {response.prompt_feedback}")


except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
