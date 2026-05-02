from flask import request
from app.config.config import BaseConfig


def get_pagination_params():
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(
            max(1, int(request.args.get("limit", BaseConfig.DEFAULT_PAGE_SIZE))),
            BaseConfig.MAX_PAGE_SIZE,
        )
    except (ValueError, TypeError):
        page, limit = 1, BaseConfig.DEFAULT_PAGE_SIZE
    return page, limit


def paginate_query(query, page: int, limit: int):
    """Paginate a SQLAlchemy query. Returns (items, total)."""
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return items, total
