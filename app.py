import datetime

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from api import main, suggest
from enums import TransportType

app = FastAPI()

# Подключение статических файлов из директории "static" в URL-путь "/static"
app.mount("/static", StaticFiles(directory="static", html=True))

# Добавление Middleware для обработки CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Разрешение запросов с любых источников
    allow_credentials=True,  # Разрешение отправки куки и заголовков авторизации
    allow_methods=["*"],  # Разрешение любых HTTP-методов
    allow_headers=["*"],  # Разрешение любых HTTP-заголовков
)

# Обработчик GET-запроса по корневому URL-пути "/"
@app.get("/")
async def root(departure_station: str, arrival_station: str, date: datetime.date, transport_type: TransportType = TransportType.TRAIN):
    return main(departure_station, arrival_station, date, transport_type)  # Вызов функции main с передачей параметров

# Обработчик GET-запроса по URL-пути "/suggest"
@app.get("/suggest")
async def root(sample: str):
    return suggest(sample)  # Вызов функции suggest с передачей параметра
