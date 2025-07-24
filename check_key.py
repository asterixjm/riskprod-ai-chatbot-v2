import os
import dotenv

# Load the .env file just like your main app does
dotenv.load_dotenv()

# Get the key from the environment
api_key = os.getenv("ANTHROPIC_API_KEY")

if api_key:
    print("API key found!")
    # We print the key between > and < to make any whitespace visible
    print(f"Key is: >{api_key}<")
    print(f"Key length is: {len(api_key)}")
else:
    print("API key was NOT found in the environment.")
