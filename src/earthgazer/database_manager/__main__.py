if __name__ == "__main__":
    from earthgazer.database_manager import DatabaseManager
    from earthgazer.document_manager import DocumentManager
    from earthgazer.document_manager.models import File
    from sqlalchemy.orm import scoped_session
    from sqlalchemy import select
    from earthgazer.document_manager.definitions import StorageType
    from earthgazer.document_manager.validators import FileCreate

    from earthgazer.document_manager.definitions import TransformationType

    print(TransformationType["1-1"])
    print(TransformationType["one_to_one"])
    print(TransformationType("one_to_many"))
    if False:
        db = DatabaseManager()
        session = scoped_session(db.session_factory)
        dm = DocumentManager(session())
        dm.create_file(FileCreate(name="test something else", storage_type=StorageType.LOCAL, storage_path="/tmp"))
        result = session.execute(select(File).where(File.name.contains("test")))
        for x in result:
            print({attr: getattr(x[0], attr) for attr in x[0].__dict__ if not attr.startswith("_")})
        session.close()
        db.engine.dispose()
