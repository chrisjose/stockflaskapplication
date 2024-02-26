web: gunicorn applications.web.app:app
data_analyzer: uvicorn applications.data_analyzer.app:app --host 0.0.0.0 --port 8081
data_collector: uvicorn applications.data_collector.app:app --host 0.0.0.0 --port 8082
