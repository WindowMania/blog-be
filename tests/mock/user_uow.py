from src.user.unit_of_work import SqlAlchemyUow


class UnCommitSqlAlchemyUow(SqlAlchemyUow):
    def __init__(self, session_factory):
        super().__init__(session_factory)

    def commit(self):
        """
         커밋을 flush로 위장.
         무조건 rollback 되도록..
        """
        self.session.flush()
