from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GenomicAI API"
    app_version: str = "0.1.0"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    rag_persist_dir: str = "./chroma"
    pubmed_demo_path: str = "./app/data/pubmed_demo.json"
    use_sentence_transformers: bool = True
    use_chroma: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
