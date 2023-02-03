from __future__ import annotations
import abc
from src.user.repositories import UserRepository
from src.post.repositories import PostRepository, SeriesRepository
from src.file.repositories import FileModelRepository


class AbstractUnitOfWork(abc.ABC):

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    @abc.abstractmethod
    def flush(self):
        raise NotImplementedError


class SqlAlchemyUow(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        self.users = UserRepository(self.session)
        self.posts = PostRepository(self.session)
        self.files = FileModelRepository(self.session)
        self.series = SeriesRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def detach_from_persistence(self):
        self.session.expunge_all()

    def rollback(self):
        self.session.rollback()

    def flush(self):
        self.session.flush()
