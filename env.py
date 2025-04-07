import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv('Your LANGCHAIN_API_KEY')
if api_key is None:
    raise ValueError("LANGCHAIN_API_KEY is not set! Check your environment variables.")

os.environ['LANGCHAIN_API_KEY'] = api_key  # Now it's safe to assign
