with open('backend/migrations/env.py', 'r') as f:
    content = f.read()

old_code = """    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )"""

new_code = """    connect_args = {}
    if "asyncpg" in DATABASE_URL:
        connect_args["statement_cache_size"] = 0

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args
    )"""

content = content.replace(old_code, new_code)

with open('backend/migrations/env.py', 'w') as f:
    f.write(content)
