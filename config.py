import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fever API Configuration
FEVER_API_URL = os.getenv('FEVER_API_URL', 'https://api.webfollow.cc/plugins/fever/')
FEVER_USERNAME = os.getenv('FEVER_USERNAME', 'guest')
FEVER_PASSWORD = os.getenv('FEVER_PASSWORD', '123456')

# MCP Server Configuration
MCP_SERVER_NAME = os.getenv('MCP_SERVER_NAME', 'rss-mcp-server')