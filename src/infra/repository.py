from sqlalchemy.orm import Session


class AbstractRepository:
    def add(self, model):
        raise NotImplementedError()

    def get(self, ref):
        raise NotImplementedError()


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session, model):
        self.session = session
        self.model = model

    def add(self, model):
        self.session.add(model)

    def delete(self, model):
        self.session.delete(model)

    def get(self, ref):
        return self.session.query(self.model) \
            .filter_by(id=ref) \
            .first()
