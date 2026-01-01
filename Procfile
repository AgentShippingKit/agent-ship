web: gunicorn src.service.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --max-requests 1000 --max-requests-jitter 100
