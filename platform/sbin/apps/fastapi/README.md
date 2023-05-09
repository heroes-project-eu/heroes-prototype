# FastAPI doc

## Vars
```bash
fastapi_server_port="" # Default 80
```

## Start fastapi server
```bash
uvicorn main:app --host 0.0.0.0 --port "${fastapi_server_port}"
```

### Example
```bash
fastapi_server_port=80
uvicorn main:app --host 0.0.0.0 --port "${fastapi_server_port}"
```
