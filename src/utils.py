from fastapi import HTTPException

def debug_mode(fn):
    def wrapped():
        try:
            return fn()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return wrapped