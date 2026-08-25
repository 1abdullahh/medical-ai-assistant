# Handles registering a cache with LangChain so repeated identical
# requests are answered instantly instead of calling the API again.
#
# InMemoryCache -> stored in RAM, fastest, cleared when the app restarts.
# SQLiteCache    -> stored in a .db file on disk, survives restarts,
#                   slightly slower than in-memory but reusable across sessions.

try:
    from langchain.globals import set_llm_cache
except ImportError:
    from langchain_core.globals import set_llm_cache

try:
    from langchain_community.cache import InMemoryCache, SQLiteCache
except ImportError:
    from langchain.cache import InMemoryCache, SQLiteCache


def enable_in_memory_cache():
    """Registers an in-memory cache. Fastest, but lost on app restart."""
    set_llm_cache(InMemoryCache())


def enable_sqlite_cache(database_path="mediguide_cache.db"):
    """Registers a SQLite-backed cache. Slightly slower, but persists across restarts."""
    set_llm_cache(SQLiteCache(database_path=database_path))


def disable_cache():
    """Turns caching off - every request hits the API fresh."""
    set_llm_cache(None)