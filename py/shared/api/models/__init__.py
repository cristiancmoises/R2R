from shared.api.models.auth.responses import (
    TokenResponse,
    WrappedTokenResponse,
)
from shared.api.models.base import (
    GenericBooleanResponse,
    GenericMessageResponse,
    PaginatedR2RResult,
    R2RResults,
    WrappedBooleanResponse,
    WrappedGenericMessageResponse,
)
from shared.api.models.graph.responses import (
    GraphResponse,
    WrappedGraphResponse,
    WrappedGraphsResponse,
)
from shared.api.models.ingestion.responses import (
    IngestionResponse,
    WrappedIngestionResponse,
    WrappedMetadataUpdateResponse,
    WrappedUpdateResponse,
)
from shared.api.models.management.responses import (
    AnalyticsResponse,
    ChunkResponse,
    CollectionResponse,
    ConversationResponse,
    LogResponse,
    PromptResponse,
    ServerStats,
    SettingsResponse,
    WrappedAnalyticsResponse,
    WrappedAPIKeyResponse,
    WrappedAPIKeysResponse,
    WrappedChunkResponse,
    WrappedChunksResponse,
    WrappedCollectionResponse,
    WrappedCollectionsResponse,
    WrappedConversationMessagesResponse,
    WrappedConversationResponse,
    WrappedConversationsResponse,
    WrappedDocumentResponse,
    WrappedDocumentsResponse,
    WrappedLogsResponse,
    WrappedPromptResponse,
    WrappedPromptsResponse,
    WrappedServerStatsResponse,
    WrappedSettingsResponse,
    WrappedUserResponse,
    WrappedUsersResponse,
)
from shared.api.models.retrieval.responses import (
    AgentResponse,
    AggregateSearchResult,
    RAGResponse,
    WrappedAgentResponse,
    WrappedDocumentSearchResponse,
    WrappedRAGResponse,
    WrappedSearchResponse,
    WrappedVectorSearchResponse,
)

__all__ = [
    # Auth Responses
    "GenericMessageResponse",
    "TokenResponse",
    "WrappedTokenResponse",
    "WrappedGenericMessageResponse",
    # Ingestion Responses
    "IngestionResponse",
    "WrappedIngestionResponse",
    "WrappedUpdateResponse",
    "WrappedMetadataUpdateResponse",
    # TODO: Need to review anything above this
    "GraphResponse",
    "WrappedGraphResponse",
    "WrappedGraphsResponse",
    # Management Responses
    "PromptResponse",
    "ServerStats",
    "LogResponse",
    "AnalyticsResponse",
    "SettingsResponse",
    "ChunkResponse",
    "CollectionResponse",
    "ConversationResponse",
    "WrappedServerStatsResponse",
    "WrappedLogsResponse",
    "WrappedAnalyticsResponse",
    "WrappedSettingsResponse",
    # Document Responses
    "WrappedDocumentResponse",
    "WrappedDocumentsResponse",
    # Collection Responses
    "WrappedCollectionResponse",
    "WrappedCollectionsResponse",
    # Prompt Responses
    "WrappedPromptResponse",
    "WrappedPromptsResponse",
    # Chunk Responses
    "WrappedChunkResponse",
    "WrappedChunksResponse",
    # Conversation Responses
    "WrappedConversationMessagesResponse",
    "WrappedConversationResponse",
    "WrappedConversationsResponse",
    # User Responses
    "WrappedUserResponse",
    "WrappedAPIKeyResponse",
    "WrappedAPIKeysResponse",
    "WrappedUsersResponse",
    # Base Responses
    "PaginatedR2RResult",
    "R2RResults",
    "GenericBooleanResponse",
    "GenericMessageResponse",
    "WrappedBooleanResponse",
    "WrappedGenericMessageResponse",
    # TODO: Clean up the following responses
    # Retrieval Responses
    "RAGResponse",
    "WrappedRAGResponse",
    "AgentResponse",
    "AggregateSearchResult",
    "WrappedSearchResponse",
    "WrappedDocumentSearchResponse",
    "WrappedVectorSearchResponse",
    "WrappedAgentResponse",
]
