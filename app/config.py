from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_name: str
    database_username: str
    database_password: str
    
    secret_key: str
    algorithm: str
    access_token_expire_duration: int
    
    admin_username: str
    admin_password: str
    
    class Config:
        env_file = '.env'
        
settings = Settings()