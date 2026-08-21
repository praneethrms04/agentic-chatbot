"""SQLite-backed checkpointing for LangGraph conversation persistence."""

from pathlib import Path

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.core.config import settings


class CheckpointStore:
    """Owns the aiosqlite connection backing the graph checkpointer."""

    def __init__(self) -> None:
        self._conn: aiosqlite.Connection | None = None
        self.saver: AsyncSqliteSaver | None = None

    async def start(self) -> AsyncSqliteSaver:
        """Open the database, create tables if needed, and return the saver."""
        db_path = Path(settings.CHECKPOINT_DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(str(db_path))
        self.saver = AsyncSqliteSaver(self._conn)
        await self.saver.setup()
        return self.saver

    async def stop(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            await self._conn.close()
        self._conn = None
        self.saver = None


checkpoint_store = CheckpointStore()
