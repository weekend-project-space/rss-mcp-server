# RSS MCP 服务器

[English Documentation](README.md)

基于 Fever API 的 RSS 订阅管理 FastMCP 服务器实现。

## 安装

1. 克隆仓库
2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 配置

1. 复制 `.env.example` 到 `.env`：

```bash
cp .env.example .env
```

2. 编辑 `.env` 并设置你的配置值：

- `FEVER_API_URL`：Fever API 端点 URL
- `FEVER_USERNAME`：你的 Fever API 用户名
- `FEVER_PASSWORD`：你的 Fever API 密码
- `MCP_SERVER_NAME`：你的 MCP 服务器实例名称

## 运行服务器

使用以下命令启动服务器：

```bash
python main.py
```

## API 工具

服务器提供以下 MCP 工具：

### 订阅源管理

- `get_feeds()`：获取所有 RSS 订阅源
- `get_groups()`：获取所有订阅源分组

### 文章操作

- `get_unread_items(max_items=10, max_id=9999999999, since_id="", feed_ids=None, group_ids=None)`：获取未读文章
- `get_saved_items(max_items=10, max_id=9999999999)`：获取已收藏文章
- `get_items(since_id="")`：获取指定 ID 之后的文章
- `get_items_by_feed_ids(feed_ids, max_items=10)`：获取指定订阅源的文章
- `get_items_by_group_ids(group_ids, max_items=10)`：获取指定分组的文章
- `mark_item(item_id, action)`：标记文章为已读/收藏/取消收藏

## 依赖项

- starlette>=0.27.0
- requests>=2.31.0
- python-dotenv>=1.0.0
- fastmcp>=0.1.0
- uvicorn>=0.24.0

## 许可证

MIT 许可证
