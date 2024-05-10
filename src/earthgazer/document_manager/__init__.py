from earthgazer.document_manager.models import File, Transformation, TransformationProcess
from earthgazer.document_manager.validators import FileCreate, TransformationCreate, TransformationProcessCreate
from sqlalchemy.orm import Session


class DocumentManager:
    def __init__(self, session: Session):
        self.session: Session = session

    def create_file(self, file: FileCreate):
        db_file = File(name=file.name, storage_type=file.storage_type.value, storage_path=file.storage_path)
        self.session.add(db_file)
        self.session.commit()
        self.session.refresh(db_file)
        return db_file

    def create_transformation(self, transformation: TransformationCreate):
        db_transformation = Transformation(name=transformation.name, description=transformation.description)
        self.session.add(db_transformation)
        self.session.commit()
        self.session.refresh(db_transformation)
        return db_transformation

    def create_transformation_process(self, process: TransformationProcessCreate):
        db_process = TransformationProcess(input_file_id=process.input_file_id, output_file_id=process.output_file_id, transformation_type=process.transformation_type)
        self.session.add(db_process)
        self.session.commit()
        self.session.refresh(db_process)
        return db_process
