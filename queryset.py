import pymongo
from math import ceil


ASCENDING = pymongo.ASCENDING
DESCENDING = pymongo.DESCENDING

PAGE_SIZE = 50


class Queryset:

    def __init__(self, document, cursor):
        self._cursor = cursor
        self._document = document

    async def to_page(self, n):

        self._cursor.rewind()
        self._cursor.skip(n * PAGE_SIZE)

    async def count(self):
        '''
        Counts the number of items
        '''
        i = 0
        async for item in self._cursor:
            i += 1
        self._cursor.rewind()
        return i

    async def first(self):
        '''
        Returns the first element
        '''
        item = await self._cursor.__anext__()
        if not item:
            return None
        self._cursor.rewind()
        return await self._document.from_dict(item)

    async def order_by(self, *args):
        # Takes in list of tuples
        return self._cursor.sort(args)

    async def _number_of_pages(self):
        return ceil(await self.count() / PAGE_SIZE)

    async def all(self):
        '''
        Iterates over all the elements in the query
        '''
        for page in range(await self._number_of_pages()):
            await self.to_page(page)
            async for item in self:
                yield item

    async def __aiter__(self):
        '''
        Iterates over the current page.
        '''
        cursor = self._cursor
        if not 'AsyncIOMotorLatentCommandCursor' == cursor.__class__.__name__:
            cursor = cursor.limit(PAGE_SIZE)
        async for item in cursor:
            yield self._document.from_dict(item)

    async def to_json(self):
        data = []
        async for item in self:
            data.append(await (await item).to_dict())
        return data
