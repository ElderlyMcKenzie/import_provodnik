import uvicorn

from app import app

if __name__ == "__main__":
     # Запуск веб-приложения с помощью uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)