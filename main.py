import asyncio
import uvicorn
from src.core.init_db import create_default_admin

if __name__ == "__main__":
    try:
        asyncio.run(create_default_admin())
    except Exception as e:
        print(f"Ошибка при инициализации БД: {e}")

    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
