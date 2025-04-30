import hashlib
import requests
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP
import logging
from typing import List, Dict, Optional
from config import FEVER_API_URL, FEVER_USERNAME, FEVER_PASSWORD, \
    MCP_SERVER_NAME

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP(MCP_SERVER_NAME)

# Configuration from environment variables
API_KEY = hashlib.md5(f"{FEVER_USERNAME}:{FEVER_PASSWORD}".encode())\
    .hexdigest()


# Fever API client
def fever_api_request(params: dict) -> dict:
    """Make a GET request to the Fever API.

    Args:
        params: Dictionary of query parameters to send with the request.

    Returns:
        JSON response from the Fever API.

    Raises:
        requests.exceptions.HTTPError: If the HTTP request fails.
        ValueError: If the API authentication fails.
    """
    params = {"api_key": API_KEY, **params}
    try:
        response = requests.get(FEVER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        json_response = response.json()
        if json_response.get("auth") == 0:
            raise ValueError("Fever API authentication failed")
        return json_response
    except requests.exceptions.RequestException as e:
        logger.error(f"Fever API request failed: {e}")
        raise


# Helper Functions
def format_item(item: dict) -> dict:
    """Format a Fever API item into a standardized dictionary.

    Args:
        item: Raw item dictionary from the Fever API.

    Returns:
        Formatted item dictionary.
    """
    return {
        "id": item["id"],
        "feed_id": item["feed_id"],
        "title": item["title"],
        "url": item["url"],
        "content": item["html"],
        "created_on": item["created_on_time"],
        "author": item.get("author", ""),
        "enclosure": item.get("enclosure", ""),
        "is_saved": item["is_saved"],
        "is_read": item["is_read"]
    }


def parse_id_string(id_string: str) -> List[int]:
    """Parse a comma-separated string of IDs into a list of integers.

    Args:
        id_string: Comma-separated string of IDs (e.g., "1,2,3").

    Returns:
        List of integer IDs.

    Raises:
        ValueError: If the string contains invalid IDs.
    """
    if not id_string:
        return []
    try:
        return [int(id_) for id_ in id_string.split(",") if id_.strip()]
    except ValueError as e:
        raise ValueError(f"Invalid ID format in string: {id_string}") from e


def fetch_items(
    max_items: int = 10,
    max_id: int = 9999999999,
    since_id: str = "",
    feed_ids: Optional[List[int]] = None,
    group_ids: Optional[List[int]] = None,
    filter_type: Optional[str] = None,
    item_ids: Optional[List[str]] = None
) -> List[Dict]:
    """Fetch items from the Fever API with flexible filtering.

    Args:
        max_items: Maximum number of items to return.
        max_id: Maximum item ID to fetch items before.
        since_id: Fetch items with IDs greater than this value.
        feed_ids: List of feed IDs to filter items.
        group_ids: List of group IDs to filter items.
        filter_type: Type of filter ('unread', 'saved', or None for all items).
        item_ids: Specific item IDs to fetch.

    Returns:
        List of formatted item dictionaries.
    """
    params = {"items": ""}

    # Apply ID filters
    if max_id > 0:
        params["max_id"] = str(max_id)
    if since_id:
        params["since_id"] = since_id
    if item_ids:
        params["with_ids"] = ",".join(item_ids[:50])  # API limits to 50 items
    if feed_ids:
        params["feed_ids"] = ",".join(str(fid) for fid in feed_ids)
    if group_ids:
        params["group_ids"] = ",".join(str(gid) for gid in group_ids)
    if filter_type == "saved":
        params["saved_items"] = ""

    # Optimize for unread items if no specific filters
    if filter_type == "unread" and not (feed_ids or group_ids or since_id or item_ids):
        id_params = {"unread_item_ids": ""}
        response = fever_api_request(id_params)
        unread_ids = response.get("unread_item_ids", "").split(",") if response.get("unread_item_ids") else []
        if unread_ids:
            unread_ids = [id_ for id_ in unread_ids if (not since_id or int(id_) > int(since_id)) and int(id_) <= max_id]
            params["with_ids"] = ",".join(unread_ids[:50])

    response = fever_api_request(params)
    items = response.get("items", [])

    # Apply local filtering
    filtered_items = [
        format_item(item)
        for item in items
        if (filter_type is None or
            (filter_type == "unread" and item["is_read"] == 0) or
            (filter_type == "saved" and item["is_saved"] == 1))
    ]

    return filtered_items[:max_items]


# MCP Tools
@mcp.tool()
def get_unread_items(
    max_items: int = 10,
    max_id: int = 9999999999,
    since_id: str = "",
    feed_ids: Optional[List[int]] = None,
    group_ids: Optional[List[int]] = None
) -> List[Dict]:
    """Fetch unread RSS items from the Fever API.

    Args:
        max_items: Maximum number of unread items to return (local limit, API may return up to 50).
        max_id: Maximum item ID to fetch items before.
        since_id: Fetch items with IDs greater than this value.
        feed_ids: List of feed IDs to filter items (optional).
        group_ids: List of group IDs to filter items (optional).

    Returns:
        List of dictionaries containing unread item details.
    """
    return fetch_items(
        max_items=max_items,
        max_id=max_id,
        since_id=since_id,
        feed_ids=feed_ids,
        group_ids=group_ids,
        filter_type="unread"
    )


@mcp.tool()
def get_saved_items(max_items: int = 10, max_id: int = 9999999999) -> List[Dict]:
    """Fetch saved (favorited) RSS items from the Fever API.

    Args:
        max_items: Maximum number of saved items to return.
        max_id: Maximum item ID to fetch items before.

    Returns:
        List of dictionaries containing saved item details.
    """
    return fetch_items(
        max_items=max_items,
        max_id=max_id,
        filter_type="saved"
    )


@mcp.tool()
def get_items(since_id: str = "") -> List[Dict]:
    """Fetch RSS items from the Fever API since a given item ID.

    Args:
        since_id: Fetch items with IDs greater than this value.

    Returns:
        List of dictionaries containing item details.
    """
    return fetch_items(since_id=since_id)


@mcp.tool()
def get_items_by_feed_ids(feed_ids: str, max_items: int = 10) -> List[Dict]:
    """Fetch RSS items from specific feed IDs.

    Args:
        feed_ids: Comma-separated string of feed IDs (e.g., "1,2,3").
        max_items: Maximum number of items to return.

    Returns:
        List of dictionaries containing item details.

    Raises:
        ValueError: If feed_ids contains invalid IDs.
    """
    feed_id_list = parse_id_string(feed_ids)
    return fetch_items(max_items=max_items, feed_ids=feed_id_list)


@mcp.tool()
def get_items_by_group_ids(group_ids: str, max_items: int = 10) -> List[Dict]:
    """Fetch RSS items from specific group IDs.

    Args:
        group_ids: Comma-separated string of group IDs (e.g., "1,2").
        max_items: Maximum number of items to return.

    Returns:
        List of dictionaries containing item details.

    Raises:
        ValueError: If group_ids contains invalid IDs.
    """
    group_id_list = parse_id_string(group_ids)
    return fetch_items(max_items=max_items, group_ids=group_id_list)


@mcp.tool()
def mark_item(item_id: int, action: str) -> bool:
    """Mark an RSS item with a specific action via the Fever API.

    Args:
        item_id: ID of the item to mark.
        action: Action to perform ('read', 'saved', 'unsaved').

    Returns:
        True if successful.

    Raises:
        ValueError: If authentication fails or action is invalid.
    """
    if action not in {"read", "saved", "unsaved"}:
        raise ValueError(f"Invalid action: {action}")
    params = {"mark": "item", "id": str(item_id), "as": action}
    fever_api_request(params)
    return True


@mcp.tool("data://feeds")
def get_feeds() -> List[Dict]:
    """Fetch all feeds from the Fever API.

    Returns:
        List of dictionaries containing feed details.
    """
    response = fever_api_request({"feeds": ""})
    feeds = response.get("feeds", [])
    return [
        {
            "id": feed["id"],
            "title": feed["title"],
            "url": feed["url"],
            "site_url": feed["site_url"],
            "last_updated": feed["last_updated_on_time"]
        }
        for feed in feeds
    ]


@mcp.tool("data://groups")
def get_groups() -> List[Dict]:
    """Fetch all feed groups from the Fever API.

    Returns:
        List of dictionaries containing group details with associated feed IDs.
    """
    response = fever_api_request({"groups": ""})
    groups = response.get("groups", [])
    feeds_groups = response.get("feeds_groups", [])
    group_feed_map = {
        fg["group_id"]: [int(fid) for fid in fg["feed_ids"].split(",") if fid]
        for fg in feeds_groups
    }

    return [
        {
            "id": group["id"],
            "title": group["title"],
            "feed_ids": group_feed_map.get(group["id"], [])
        }
        for group in groups
    ]


@mcp.resource("config://app-version")
def get_app_version() -> str:
    """Returns the application version."""
    return "v2.1.0"


# Starlette application
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)

if __name__ == "__main__":
    mcp.run()
