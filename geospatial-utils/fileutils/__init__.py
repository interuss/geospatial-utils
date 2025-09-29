import datetime
import hashlib
import os
import pathlib
from wsgiref.handlers import format_date_time

import requests
from loguru import logger

CACHE_DIR = pathlib.Path(".cache/")
"""Location used to cache downloaded files"""

FILE_RETRIEVAL_TIMEOUT_S = 20
"""Connection and read timeout when retrieving files"""


def _safe_name(url: str) -> str:
    """Create a filesystem-safe name from the URL."""
    h = hashlib.sha1(url.encode()).hexdigest()
    ext = os.path.splitext(url.split("?")[0])[1]
    return h + ext


def get(url: str, cache_ttl_sec: int | None = None) -> pathlib.Path:
    """Download and cache the file located at url.
    It ignores cache entries older than cache_ttl_sec"""

    f = pathlib.Path(CACHE_DIR).joinpath(_safe_name(url))

    if f.exists():
        creation_time = datetime.datetime.fromtimestamp(
            os.path.getctime(f), tz=datetime.UTC
        )

        # Check for local cache hit
        if cache_ttl_sec is not None:
            now = datetime.datetime.now(tz=datetime.UTC)
            age = (now - creation_time).total_seconds()
            if age < cache_ttl_sec:
                ttl = int(cache_ttl_sec - age)
                logger.debug(f"Cache hit for {url} with {f} (ttl: {ttl}s)")
                return f

        # Tell server when our copy was retrieved
        http_date = format_date_time(creation_time.timestamp())
        headers = {"If-Modified-Since": http_date}
    else:
        headers = {}

    r = requests.get(url, headers=headers, timeout=FILE_RETRIEVAL_TIMEOUT_S)
    r.raise_for_status()

    if r.status_code == 200:
        CACHE_DIR.mkdir(exist_ok=True, parents=True)
        f.write_bytes(r.content)
        logger.debug(f"Downloaded {url} to {f}")
    elif r.status_code == 304:
        pass  # Our copy is up to date with the server
    else:
        raise RuntimeError(f"Server status of {r.status_code} is not supported")
    return f
