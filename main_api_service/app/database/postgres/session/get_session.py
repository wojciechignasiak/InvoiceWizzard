from fastapi import Request

async def get_session(request: Request):
        try:
            yield request.app.state.async_postgres_session
            await request.app.state.async_postgres_session.commit()
        except Exception:
            await request.app.state.async_postgres_session.rollback()
        finally:
            await request.app.state.async_postgres_session.remove()