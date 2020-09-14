import json
import logging
from collections import namedtuple

import aio_pika
import aiomysql


async def init_mysql(app):
    conf = app['config']['db']

    conn = await aiomysql.create_pool(
        host=conf['host'], port=conf['port'], user=conf['user'],
        password=conf['password'], db=conf['database'])
    app['db'] = conn


async def close_mysql(app):
    app['db'].close()


async def init_queue(app):
    async def get_connection():
        urn = app['config']['rabbit']['urn']
        return await aio_pika.connect_robust(urn)

    connection_pool = aio_pika.pool.Pool(get_connection, max_size=2, loop=app.loop)

    async def get_channel():
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    channel_pool = aio_pika.pool.Pool(get_channel, max_size=10, loop=app.loop)
    queue_name = "test_queue"

    async def send(msg):
        async with channel_pool.acquire() as channel:
            text = json.dumps(msg, ensure_ascii=False).encode()
            await channel.default_exchange.publish(
                aio_pika.Message(text), queue_name)

    async def receive():
        async with channel_pool.acquire() as channel:
            await channel.set_qos(10)
            queue = await channel.declare_queue(
                queue_name, durable=False, auto_delete=True)
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    yield json.loads(message.body)
                    await message.ack()

    async def close():
        await channel_pool.close()
        await connection_pool.close()

    Sender = namedtuple('Sender', 'send, receive, close')
    app['queue'] = Sender(close=close, send=send, receive=receive)


async def close_queue(app):
    await app['queue'].close()
    logging.info('closing the queue')
