from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import faculty, user, vote, auth

# INIT APP
app = FastAPI()

# ADDING CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# ROUTES
@app.get("/")
def root():
    return {"message": "welcome to IUBAT Faculty Rating System!!"}

app.include_router(faculty.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)