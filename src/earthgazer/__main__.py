"""
Entrypoint module, in case you use `python -m earthgazer`.
"""


def main():
    from earthgazer.database_manager import DatabaseManager, Base
    Base.metadata.create_all(DatabaseManager().engine)


if __name__ == "__main__":
    main()
