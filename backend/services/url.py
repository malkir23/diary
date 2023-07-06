from fastapi import Request


def create_url(request: Request) -> str:
    return f"{request.url.scheme}://{request.url.hostname}"
