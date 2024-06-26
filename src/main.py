from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="Trading app",
)

@app.get('/')
def hello():
    return "hello world"

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)