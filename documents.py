import os
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorClient as Client

from pymongo.errors import OperationFailure

from .queryset import Queryset
from .fields import ObjectIdField

from .fields import BaseField


class Document:

    _id = ObjectIdField()

    def __init__(self, *args, **kwargs):
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
            else:
                raise ValueError(f'{self.__class__.__name__} has no attribute {field}')

    @classmethod
    async def connect(cls, *args, **kwargs):
        if not args:
            uri = os.getenv('MONGODB_URI')
            if uri:
                args = (uri, )
        cls.client = Client(*args, **kwargs)
        cls.db = cls.client[os.getenv('DATABASE_NAME', 'db')]

    @classmethod
    def disconnect(cls, *args, **kwargs):
        cls.client.close()

    @classmethod
    async def update_index(cls):
        collection = cls.db[await cls.__table_name__()]
        # Creating indexes
        async for name, field in cls.fields():
            if not name == '_id' and field.index:
                try:
                    await collection.drop_index(name)
                except OperationFailure as e:
                    print(e)
                await collection.create_index(name, unique=field.unique)


    @classmethod
    async def fields(cls):
        '''
        Gets the fields for the document
        '''
        for key, value in cls.__bases__[0].__dict__.items():
            if isinstance(value, BaseField):
                yield key, value
        for key, value in cls.__dict__.items():
            if not key.startswith('__') and not key in ('client', 'db'):
                yield key, value

    @classmethod
    async def from_dict(cls, data):
        fields = {}
        async for key, field in cls.fields():
            if key in data:
                fields[key] = field.validate(data[key])
        return cls(**fields)  # Needs to be reference

    @classmethod
    async def find(cls, *args, **kwargs):
        return Queryset(cls, cls.db[await cls.__table_name__()].find(*args, **kwargs))

    @classmethod
    async def aggregate(cls, pipeline, *args, **kwargs):
        return Queryset(cls, cls.db[await cls.__table_name__()].aggregate(pipeline, *args, **kwargs))

    @classmethod
    async def __table_name__(cls):
        return cls.__name__.lower()

    async def to_dict(self):
        data = {}
        async for field, value in self.fields():
            data[field] = getattr(self, field)
        if not data['_id']:
            data.pop('_id')
        return data

    async def save(self):
        # getattr setattr delattr
        data = await self.to_dict()
        if '_id' in data:
            _id = data['_id']
            data.pop('_id')
            self.db[await self.table_name].replace_one({'_id': ObjectId(_id)}, data)
        else:
            self.db[await self.table_name].insert_one(data)

    async def delete(self):
        pass

    @property
    async def table_name(self):
        return await self.__class__.__table_name__()
