from .documents import Document

import logging


def connect(app, *args, **kwargs):

    @app.listener('before_server_start')
    async def open_connection(app, loop):
        await Document.connect(*args, io_loop=loop, **kwargs)

        documents_in_scope = Document.__subclasses__()

        # Update the indexes
        for document in documents_in_scope:
            await document.update_index()


    @app.listener('before_server_stop')
    async def close_connection(app, loop):
        await Document.disconnect()
