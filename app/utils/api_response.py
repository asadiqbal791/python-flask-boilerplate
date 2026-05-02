from flask import jsonify
from http import HTTPStatus


def success(data=None, message: str = "Success", status_code: int = HTTPStatus.OK):
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def created(data=None, message: str = "Created"):
    return success(data, message, HTTPStatus.CREATED)


def no_content():
    return "", HTTPStatus.NO_CONTENT


def paginated(items, total: int, page: int, limit: int):
    return jsonify({
        "success": True,
        "data": {
            "results": items,
            "page": page,
            "limit": limit,
            "totalPages": -(-total // limit),  # ceiling division
            "totalResults": total,
        }
    }), HTTPStatus.OK
