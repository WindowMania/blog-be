from src.unit_of_work import SqlAlchemyUow


class MockSqlAlchemyUow(SqlAlchemyUow):
    def __init__(self, session_factory):
        super().__init__(session_factory)

    # 흠...
