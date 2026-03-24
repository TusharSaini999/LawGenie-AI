from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import CollectionInvalid, OperationFailure

from config.settings import settings


client = MongoClient(settings.mongodb_uri)
db = client[settings.mongodb_db_name]

documents_collection = db[settings.mongo_documents_collection]
sessions_collection = db[settings.mongo_sessions_collection]
messages_collection = db[settings.mongo_messages_collection]
training_state_collection = db[settings.mongo_training_state_collection]

_BOOTSTRAP_DONE = False


DOCUMENTS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["source", "source_name", "chunk_index", "text", "embedding"],
        "properties": {
            "source": {"bsonType": "string"},
            "source_name": {"bsonType": "string"},
            "chunk_index": {"bsonType": "int"},
            "text": {"bsonType": "string"},
            "embedding": {"bsonType": "array"},
            "metadata": {"bsonType": ["object", "null"]},
            "created_at": {"bsonType": ["date", "null"]},
            "updated_at": {"bsonType": ["date", "null"]},
        },
    }
}

SESSIONS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["token", "created_at", "updated_at", "expires_at"],
        "properties": {
            "token": {"bsonType": "string"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
            "expires_at": {"bsonType": "date"},
        },
    }
}

MESSAGES_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["token", "role", "message", "timestamp"],
        "properties": {
            "token": {"bsonType": "string"},
            "role": {"bsonType": "string"},
            "message": {"bsonType": "string"},
            "timestamp": {"bsonType": "date"},
        },
    }
}

TRAINING_STATE_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["source_name", "fingerprint", "status", "updated_at"],
        "properties": {
            "source_name": {"bsonType": "string"},
            "source": {"bsonType": "string"},
            "fingerprint": {"bsonType": "string"},
            "status": {"bsonType": "string"},
            "total_chunks": {"bsonType": ["int", "null"]},
            "processed_chunks": {"bsonType": ["int", "null"]},
            "started_at": {"bsonType": ["date", "null"]},
            "completed_at": {"bsonType": ["date", "null"]},
            "updated_at": {"bsonType": "date"},
            "last_error": {"bsonType": ["string", "null"]},
        },
    }
}


def _create_or_update_collection(name: str, validator: dict) -> None:
    try:
        db.create_collection(name, validator=validator)
        return
    except CollectionInvalid:
        pass

    try:
        db.command("collMod", name, validator=validator)
    except OperationFailure:
        # Some hosted Mongo plans can block collMod for low-privilege users.
        # Keep service running and rely on application-level validation.
        pass


def init_mongo_collections() -> None:
    _create_or_update_collection(settings.mongo_documents_collection, DOCUMENTS_VALIDATOR)
    _create_or_update_collection(settings.mongo_sessions_collection, SESSIONS_VALIDATOR)
    _create_or_update_collection(settings.mongo_messages_collection, MESSAGES_VALIDATOR)
    _create_or_update_collection(settings.mongo_training_state_collection, TRAINING_STATE_VALIDATOR)


def init_mongo_indexes() -> None:
    try:
        documents_collection.drop_index("uniq_source_chunk_index")
    except Exception:
        pass

    documents_collection.create_index(
        [("source_name", ASCENDING), ("chunk_index", ASCENDING)],
        unique=True,
        name="uniq_source_name_chunk_index",
    )
    documents_collection.create_index(
        [("source_name", ASCENDING)],
        name="idx_documents_source_name",
    )

    sessions_collection.create_index("token", unique=True, name="uniq_token")
    sessions_collection.create_index("expires_at", expireAfterSeconds=0, name="ttl_expires_at")
    sessions_collection.create_index("updated_at", name="idx_sessions_updated_at")

    messages_collection.create_index(
        [("token", ASCENDING), ("timestamp", DESCENDING)],
        name="idx_messages_token_timestamp",
    )

    training_state_collection.create_index("source_name", unique=True, name="uniq_training_source_name")
    training_state_collection.create_index("status", name="idx_training_status")
    training_state_collection.create_index("updated_at", name="idx_training_updated_at")


def init_atlas_vector_index() -> None:
    if not settings.mongo_use_atlas_vector_search:
        return

    try:
        db.command(
            {
                "createSearchIndexes": settings.mongo_documents_collection,
                "indexes": [
                    {
                        "type": "vectorSearch",
                        "name": settings.mongo_vector_index_name,
                        "definition": {
                            "fields": [
                                {
                                    "type": "vector",
                                    "path": "embedding",
                                    "numDimensions": settings.mongo_embedding_dimensions,
                                    "similarity": "cosine",
                                }
                            ]
                        },
                    }
                ],
            }
        )
    except Exception:
        # Atlas search index creation is not available on all Mongo deployments.
        pass


def init_atlas_search_index() -> None:
    if not settings.mongo_use_atlas_vector_search:
        return

    try:
        db.command(
            {
                "createSearchIndexes": settings.mongo_documents_collection,
                "indexes": [
                    {
                        "type": "search",
                        "name": settings.mongo_search_index_name,
                        "definition": {
                            "mappings": {
                                "dynamic": True,
                            }
                        },
                    }
                ],
            }
        )
    except Exception:
        # Ignore if index already exists or command unsupported for the deployment.
        pass


def bootstrap_mongo() -> None:
    global _BOOTSTRAP_DONE
    if _BOOTSTRAP_DONE:
        return

    init_mongo_collections()
    init_mongo_indexes()
    init_atlas_vector_index()
    init_atlas_search_index()
    _BOOTSTRAP_DONE = True


bootstrap_mongo()