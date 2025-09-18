import hashlib
import os
import pathlib
from typing import Tuple
import requests
import datetime

from loguru import logger

CACHE_DIR = pathlib.Path(".cache/")

def _safe_name(url: str) -> str:
    """Create a filesystem-safe name from the URL."""
    h = hashlib.sha1(url.encode()).hexdigest()
    ext = os.path.splitext(url.split("?")[0])[1]
    return h + ext

def _is_cached(url: str, cache_ttl_sec) -> Tuple[pathlib.Path, bool]:
    f = pathlib.Path(CACHE_DIR).joinpath(_safe_name(url))

    creation_time = datetime.datetime.fromtimestamp(os.path.getctime(f))
    now = datetime.datetime.now()
    age = (now - creation_time).total_seconds()

    cache_hit = f.exists() and age < cache_ttl_sec
    if cache_hit:
        ttl = int(cache_ttl_sec-age)
        logger.debug(f"Cache hit for {url} with {f} (ttl: {ttl}s)")
    return f, cache_hit

def _download_and_cache(url: str, destination: pathlib.Path):
    CACHE_DIR.mkdir(exist_ok=True)

    r = requests.get(url, timeout=20)
    r.raise_for_status()
    destination.write_bytes(r.content)
    logger.debug(f"Downloaded {url} to {destination}")

def get(url: str, cache_ttl_sec=0) -> pathlib.Path:
    """Download and cache the file located at url.
    It discards cache entries older than cache_ttl_sec"""

    destination, cache_hit = _is_cached(url, cache_ttl_sec)
    if not cache_hit:
        _download_and_cache(url, destination)

    return destination
