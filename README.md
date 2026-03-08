alembic revision --autogenerate -m "message"
alembic upgrade head
docker-compose up --build -d
uvicorn main:app --reload