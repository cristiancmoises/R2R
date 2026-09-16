"""Chunk-ingestion regressions without a database or embedding provider."""

from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from uuid import UUID

from core.base import IngestionStatus, User, Vector, VectorEntry, VectorType
from core.main.orchestration.simple.ingestion_workflow import (
    simple_ingestion_factory,
)
from core.main.services.ingestion_service import IngestionService

DOCUMENT_ID = UUID("12345678-1234-5678-1234-567812345678")
OWNER_ID = UUID("22345678-1234-5678-1234-567812345678")
COLLECTION_ID = UUID("32345678-1234-5678-1234-567812345678")
CHUNK_ID = UUID("42345678-1234-5678-1234-567812345678")


class OfflineIngestionService(IngestionService):
    """Keep ingress and model conversion real; replace external I/O only."""

    def __init__(self):
        database = SimpleNamespace(
            documents_handler=SimpleNamespace(
                get_documents_overview=AsyncMock(
                    side_effect=lambda **_: {
                        "results": [self.document_info]
                        if self.document_info is not None
                        else []
                    }
                ),
                upsert_documents_overview=AsyncMock(),
                set_workflow_status=AsyncMock(),
            ),
            collections_handler=SimpleNamespace(
                create_collection=AsyncMock(),
                assign_document_to_collection_relational=AsyncMock(),
            ),
            chunks_handler=SimpleNamespace(
                assign_document_chunks_to_collection=AsyncMock(),
            ),
            graphs_handler=SimpleNamespace(create=AsyncMock()),
        )
        super().__init__(
            config=SimpleNamespace(),
            providers=SimpleNamespace(
                database=database,
                ingestion=SimpleNamespace(
                    config=SimpleNamespace(automatic_extraction=False)
                ),
            ),
        )
        self.stored = []
        self.document_info = None

    async def ingest_chunks_ingress(self, **kwargs):
        self.document_info = await super().ingest_chunks_ingress(**kwargs)
        return self.document_info

    async def embed_document(self, extractions):
        for extraction in extractions:
            yield VectorEntry(
                id=extraction["id"],
                document_id=extraction["document_id"],
                owner_id=extraction["owner_id"],
                collection_ids=extraction["collection_ids"],
                vector=Vector(data=[1.0, 0.0], type=VectorType.FIXED),
                text=extraction["data"],
                metadata=extraction["metadata"],
            )

    async def store_embeddings(self, embeddings):
        self.stored.extend(embeddings)
        yield "Stored"


class TestSimpleChunkIngestion(IsolatedAsyncioTestCase):
    async def test_ingests_chunks_with_default_user_collection(self):
        service = OfflineIngestionService()
        user = User(
            id=OWNER_ID,
            email="test@example.com",
            collection_ids=[COLLECTION_ID],
        )

        await simple_ingestion_factory(service)["ingest-chunks"](
            {
                "user": user.model_dump_json(),
                "document_id": str(DOCUMENT_ID),
                "metadata": {"title": "Regression"},
                "chunks": [{"id": str(CHUNK_ID), "text": "Hello chunk"}],
            }
        )

        self.assertEqual(len(service.stored), 1)
        stored = service.stored[0]
        self.assertEqual(stored["id"], CHUNK_ID)
        self.assertEqual(stored["document_id"], DOCUMENT_ID)
        self.assertEqual(stored["owner_id"], OWNER_ID)
        self.assertEqual(stored["collection_ids"], [COLLECTION_ID])
        self.assertEqual(stored["text"], "Hello chunk")
        self.assertEqual(stored["metadata"]["title"], "Regression")
        self.assertEqual(
            service.document_info.ingestion_status, IngestionStatus.SUCCESS
        )
