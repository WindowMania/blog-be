# from typing import TypeVar, Generic, Optional
#
# ModelType = TypeVar("ModelType")
# ModelId = TypeVar("ModelId")
#
#
# class SqlAlchemyRepository(Generic[ModelId, ModelType]):
#     @staticmethod
#     def add(session, model: ModelType):
#         session.add(model)
#
#     @staticmethod
#     def get(session, id_: ModelId) -> Optional[ModelType]:
#         print("어??", id_, ModelType)
#         return session \
#             .query(ModelType) \
#             .filter_by(id=id_) \
#             .first()
