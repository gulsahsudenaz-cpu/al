web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT

worker: cd backend && rq worker --url $REDIS_URL

