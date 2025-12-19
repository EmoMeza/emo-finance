"""
Common models and utilities shared across all models
"""
from pydantic_core import core_schema
from typing import Any
from bson import ObjectId


class PyObjectId(str):
    """
    Custom Pydantic type for MongoDB ObjectId (Pydantic v2 compatible)
    """
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler):
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ], serialization=core_schema.plain_serializer_function_ser_schema(
            lambda x: str(x)
        ))

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")
