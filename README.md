# RSS MCP Server

[中文文档](README_zh.md)

A FastMCP server implementation for RSS feed management using the Fever API.

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

2. Edit `.env` and set your configuration values:

- `FEVER_API_URL`: URL of your Fever API endpoint
- `FEVER_USERNAME`: Your Fever API username
- `FEVER_PASSWORD`: Your Fever API password
- `MCP_SERVER_NAME`: Name for your MCP server instance

3. Configure Cursor Integration:

Create or edit your Cursor MCP configuration file at `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "RssMcpServer": {
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}
```

This configuration will allow Cursor to connect to your RSS MCP server running locally on port 8000.

## Running the Server

Start the server using:

```bash
python main.py
```

## API Tools

The server provides the following MCP tools:

### Feed Management

- `get_feeds()`: Retrieve all RSS feeds
- `get_groups()`: Retrieve all feed groups

### Item Operations

- `get_unread_items(max_items=10, max_id=9999999999, since_id="", feed_ids=None, group_ids=None)`: Get unread items
- `get_saved_items(max_items=10, max_id=9999999999)`: Get saved/favorited items
- `get_items(since_id="")`: Get items since a specific ID
- `get_items_by_feed_ids(feed_ids, max_items=10)`: Get items from specific feeds
- `get_items_by_group_ids(group_ids, max_items=10)`: Get items from specific groups
- `mark_item(item_id, action)`: Mark items as read/saved/unsaved

## Dependencies

- starlette>=0.27.0
- requests>=2.31.0
- python-dotenv>=1.0.0
- fastmcp>=0.1.0
- uvicorn>=0.24.0

## License

MIT License
