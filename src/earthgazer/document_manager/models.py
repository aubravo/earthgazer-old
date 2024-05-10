from earthgazer.database_manager import Base

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from earthgazer.document_manager.definitions import TransformationType


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    storage_type = Column(String, index=True)
    storage_path = Column(String)
    transformations = relationship("Transformation", secondary='file_transformation_association', back_populates="files")
    transformation_processes = relationship("TransformationProcess", foreign_keys="[TransformationProcess.input_file_id]", back_populates="input_file")


class Transformation(Base):
    __tablename__ = 'transformations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    files = relationship("File", secondary='file_transformation_association', back_populates="transformations")


class TransformationProcess(Base):
    __tablename__ = 'transformation_processes'

    id = Column(Integer, primary_key=True, index=True)
    input_file_id = Column(Integer, ForeignKey('files.id'))
    output_file_id = Column(Integer, ForeignKey('files.id'))
    transformation_type = Column(Enum(TransformationType))

    input_file = relationship("File", foreign_keys=[input_file_id], back_populates="transformation_processes")
    output_file = relationship("File", foreign_keys=[output_file_id])


file_transformation_association_table = Table(
    'file_transformation_association', Base.metadata,
    Column('file_id', Integer, ForeignKey('files.id')),
    Column('transformation_id', Integer, ForeignKey('transformations.id'))
)
