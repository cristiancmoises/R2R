import json
import logging
import math
from copy import deepcopy
from datetime import datetime
from typing import Any, AsyncGenerator, Iterable, Optional, TypeVar
from uuid import NAMESPACE_DNS, UUID, uuid4, uuid5

from ..abstractions.search import (
    AggregateSearchResult,
    GraphCommunityResult,
    GraphEntityResult,
    GraphRelationshipResult,
)
from ..abstractions.vector import VectorQuantizationType

logger = logging.getLogger()


def format_search_results_for_llm(results: AggregateSearchResult) -> str:
    formatted_results = []
    source_counter = 1

    if results.chunk_search_results:
        formatted_results.append("Vector Search Results:")
        for result in results.chunk_search_results:
            formatted_results.extend(
                (f"Source [{source_counter}]:", f"{result.text}")
            )
            source_counter += 1

    if results.graph_search_results:
        formatted_results.append("KG Search Results:")
        for kg_result in results.graph_search_results:
            try:
                formatted_results.extend((f"Source [{source_counter}]:",))
            except AttributeError:
                raise ValueError(f"Invalid KG search result: {kg_result}")

            if isinstance(kg_result.content, GraphCommunityResult):
                formatted_results.extend(
                    (
                        f"Community Name: {kg_result.content.name}",
                        f"ID: {kg_result.content.id}",
                        f"Summary: {kg_result.content.summary}",
                        # f"Findings: {kg_result.content.findings}",
                    )
                )
            elif isinstance(
                kg_result.content,
                GraphEntityResult,
            ):
                formatted_results.extend(
                    [
                        f"Entity Name: {kg_result.content.name}",
                        f"ID: {kg_result.content.id}",
                        f"Description: {kg_result.content.description}",
                    ]
                )
            elif isinstance(kg_result.content, GraphRelationshipResult):
                formatted_results.extend(
                    (
                        f"Relationship: {kg_result.content.subject} - {kg_result.content.predicate} - {kg_result.content.object}",
                        f"ID: {kg_result.content.id}",
                        f"Description: {kg_result.content.description}",
                        f"Subject ID: {kg_result.content.subject_id}",
                        f"Object ID: {kg_result.content.object_id}",
                    )
                )

            if kg_result.metadata:
                metadata_copy = kg_result.metadata.copy()
                metadata_copy.pop("associated_query", None)
                if metadata_copy:
                    formatted_results.append("Metadata:")
                    formatted_results.extend(
                        f"- {key}: {value}"
                        for key, value in metadata_copy.items()
                    )

            source_counter += 1
    if results.web_search_results:
        formatted_results.append("Web Search Results:")
        for result in results.web_search_results:
            formatted_results.extend(
                (
                    f"Source [{source_counter}]:",
                    f"Title: {result.title}",
                    f"Link: {result.link}",
                    f"Snippet: {result.snippet}",
                )
            )
            if result.date:
                formatted_results.append(f"Date: {result.date}")
            source_counter += 1

    # 4) NEW: If context_document_results is present:
    if results.context_document_results:
        formatted_results.append("Local Context Documents:")
        for doc_result in results.context_document_results:
            doc_data = doc_result.document
            chunks = doc_result.chunks
            doc_title = doc_data.get("title", "Untitled Document")
            doc_id = doc_data.get("id", "N/A")
            summary = doc_data.get("summary", "")

            formatted_results.append(
                f"Document Title: {doc_title} (ID: {doc_id})"
            )
            if summary:
                formatted_results.append(f"Summary: {summary}")

            # Then each chunk inside:
            formatted_results.extend(
                f"Chunk {i}: {ch}" for i, ch in enumerate(chunks, start=1)
            )

            source_counter += 1

    return "\n".join(formatted_results)


def format_search_results_for_stream(results: AggregateSearchResult) -> str:
    CHUNK_SEARCH_STREAM_MARKER = "chunk_search"
    GRAPH_SEARCH_STREAM_MARKER = "graph_search"
    WEB_SEARCH_STREAM_MARKER = "web_search"
    CONTEXT_STREAM_MARKER = "content"

    context = ""

    if results.chunk_search_results:
        context += f"<{CHUNK_SEARCH_STREAM_MARKER}>"
        vector_results_list = [
            r.as_dict() for r in results.chunk_search_results
        ]
        context += json.dumps(vector_results_list, default=str)
        context += f"</{CHUNK_SEARCH_STREAM_MARKER}>"

    if results.graph_search_results:
        context += f"<{GRAPH_SEARCH_STREAM_MARKER}>"
        kg_results_list = [r.dict() for r in results.graph_search_results]
        context += json.dumps(kg_results_list, default=str)
        context += f"</{GRAPH_SEARCH_STREAM_MARKER}>"

    if results.web_search_results:
        context += f"<{WEB_SEARCH_STREAM_MARKER}>"
        web_results_list = [r.to_dict() for r in results.web_search_results]
        context += json.dumps(web_results_list, default=str)
        context += f"</{WEB_SEARCH_STREAM_MARKER}>"

    # NEW: local context
    if results.context_document_results:
        context += f"<{CONTEXT_STREAM_MARKER}>"
        # Just store them as raw dict JSON, or build a more structured form
        content_list = [
            cdr.to_dict() for cdr in results.context_document_results
        ]
        context += json.dumps(content_list, default=str)
        context += f"</{CONTEXT_STREAM_MARKER}>"

    return context


def _generate_id_from_label(label) -> UUID:
    return uuid5(NAMESPACE_DNS, label)


def generate_id(label: Optional[str] = None) -> UUID:
    """
    Generates a unique run id
    """
    return _generate_id_from_label(label if label != None else str(uuid4()))


def generate_document_id(filename: str, user_id: UUID) -> UUID:
    """
    Generates a unique document id from a given filename and user id
    """
    safe_filename = filename.replace("/", "_")
    return _generate_id_from_label(f"{safe_filename}-{str(user_id)}")


def generate_extraction_id(
    document_id: UUID, iteration: int = 0, version: str = "0"
) -> UUID:
    """
    Generates a unique extraction id from a given document id and iteration
    """
    return _generate_id_from_label(f"{str(document_id)}-{iteration}-{version}")


def generate_default_user_collection_id(user_id: UUID) -> UUID:
    """
    Generates a unique collection id from a given user id
    """
    return _generate_id_from_label(str(user_id))


def generate_user_id(email: str) -> UUID:
    """
    Generates a unique user id from a given email
    """
    return _generate_id_from_label(email)


def generate_default_prompt_id(prompt_name: str) -> UUID:
    """
    Generates a unique prompt id
    """
    return _generate_id_from_label(prompt_name)


def generate_entity_document_id() -> UUID:
    """
    Generates a unique document id inserting entities into a graph
    """
    generation_time = datetime.now().isoformat()
    return _generate_id_from_label(f"entity-{generation_time}")


async def to_async_generator(
    iterable: Iterable[Any],
) -> AsyncGenerator[Any, None]:
    for item in iterable:
        yield item


def increment_version(version: str) -> str:
    prefix = version[:-1]
    suffix = int(version[-1])
    return f"{prefix}{suffix + 1}"


def decrement_version(version: str) -> str:
    prefix = version[:-1]
    suffix = int(version[-1])
    return f"{prefix}{max(0, suffix - 1)}"


def validate_uuid(uuid_str: str) -> UUID:
    return UUID(uuid_str)


def update_settings_from_dict(server_settings, settings_dict: dict):
    """
    Updates a settings object with values from a dictionary.
    """
    settings = deepcopy(server_settings)
    for key, value in settings_dict.items():
        if value is not None:
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(getattr(settings, key), dict):
                        getattr(settings, key)[k] = v
                    else:
                        setattr(getattr(settings, key), k, v)
            else:
                setattr(settings, key, value)

    return settings


def _decorate_vector_type(
    input_str: str,
    quantization_type: VectorQuantizationType = VectorQuantizationType.FP32,
) -> str:
    return f"{quantization_type.db_type}{input_str}"


def _get_vector_column_str(
    dimension: int | float, quantization_type: VectorQuantizationType
) -> str:
    """
    Returns a string representation of a vector column type.

    Explicitly handles the case where the dimension is not a valid number
    meant to support embedding models that do not allow for specifying
    the dimension.
    """
    if math.isnan(dimension) or dimension <= 0:
        vector_dim = ""  # Allows for Postgres to handle any dimension
    else:
        vector_dim = f"({dimension})"
    return _decorate_vector_type(vector_dim, quantization_type)


KeyType = TypeVar("KeyType")


def deep_update(
    mapping: dict[KeyType, Any], *updating_mappings: dict[KeyType, Any]
) -> dict[KeyType, Any]:
    """
    Taken from Pydantic v1:
    https://github.com/pydantic/pydantic/blob/fd2991fe6a73819b48c906e3c3274e8e47d0f761/pydantic/utils.py#L200
    """
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if (
                k in updated_mapping
                and isinstance(updated_mapping[k], dict)
                and isinstance(v, dict)
            ):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping
