import hashlib

from utils import database


async def create_tables(conn):
    async with conn.cursor() as cur:
        await cur.execute(
            """CREATE TABLE IF NOT EXISTS users (
               id BIGINT PRIMARY KEY AUTO_INCREMENT,
               login VARCHAR(255) UNIQUE KEY not null, 
               password VARCHAR(255) NOT NULL
            );""")
        await cur.execute("""
            CREATE TABLE `profiles` (
              `id` bigint NOT NULL AUTO_INCREMENT,
              `user_id` bigint DEFAULT NULL,
              `first_name` varchar(255) NOT NULL,
              `last_name` varchar(255) NOT NULL,
              `date_of_birth` date DEFAULT NULL,
              `sex` enum('male','female','other') DEFAULT NULL,
              `interests` longtext,
              `city` varchar(255) DEFAULT NULL,
              PRIMARY KEY (`id`),
              UNIQUE KEY `user_id` (`user_id`)
            ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        """)

        await cur.execute("""
            create index first_name_idx on profiles(first_name);
        """)
        await cur.execute("""
            create index last_name_idx on profiles(last_name);
        """)

        await cur.execute("""
            CREATE TABLE `messages` (
              `id` bigint NOT NULL AUTO_INCREMENT,
              `from` bigint DEFAULT NULL,
              `to` bigint DEFAULT NULL,
              `datetime` datetime DEFAULT NULL,
              `text` text,
              PRIMARY KEY (`id`),
              KEY `from` (`from`),
              KEY `to` (`to`),
              CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`from`) REFERENCES `profiles` (`id`),
              CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`to`) REFERENCES `profiles` (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci        
        """)

        await cur.execute("""
            CREATE TABLE `followers` (
              `id` bigint NOT NULL AUTO_INCREMENT,
              `profile_id` bigint DEFAULT NULL,
              `follows` bigint DEFAULT NULL,
              PRIMARY KEY (`id`),
              UNIQUE KEY `profile_id` (`profile_id`,`follows`),
              KEY `follows` (`follows`),
              CONSTRAINT `followers_ibfk_1` FOREIGN KEY (`profile_id`) REFERENCES `profiles` (`id`) ON DELETE CASCADE,
              CONSTRAINT `followers_ibfk_2` FOREIGN KEY (`follows`) REFERENCES `profiles` (`id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci        
        """)

        await cur.execute("""
            CREATE TABLE `posts` (
              `id` bigint NOT NULL AUTO_INCREMENT,
              `author_id` bigint DEFAULT NULL,
              `text` varchar(140) DEFAULT NULL,
              `datetime` datetime DEFAULT NULL,
              PRIMARY KEY (`id`),
              KEY `author_id` (`author_id`),
              CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `profiles` (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        """)


async def sample_data(conn):
    async with conn.cursor() as cur:
        await cur.execute(
            f"""INSERT INTO users (login, password) 
                values ('admin', '{hashlib.sha3_256('password'.encode()).hexdigest()}');""")
        await conn.commit()


async def main(app):
    async with database(app):
        async with app['db'].acquire() as conn:
            await create_tables(conn)
            await sample_data(conn)
            conn.close()

