from earthgazer.document_manager.definitions import StorageType, TransformationType
from pydantic import BaseModel


class FileCreate(BaseModel):
    name: str
    storage_type: StorageType
    storage_path: str


class TransformationCreate(BaseModel):
    name: str
    description: str


class TransformationProcessCreate(BaseModel):
    input_file_id: int
    output_file_id: int
    transformation_type: TransformationType
