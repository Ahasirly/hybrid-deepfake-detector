from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    MODEL_SBI_PATH: str = "./ml_models/sbi_finetuned"
    MODEL_DISTILDIRE_PATH: str = "./ml_models/distildire_finetuned"
    
    class Config:
        env_file = ".env"

settings = Settings()
