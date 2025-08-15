from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # Athena / AWS
    aws_access_key_id: str | None = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region: str = os.getenv("AWS_REGION", "us-west-2")
    s3_athena_output: str = os.getenv("S3_ATHENA_OUTPUT", "s3://<your-bucket>/athena-results/")

    # Base de datos Athena donde vive etlist
    athena_database: str = os.getenv("ATHENA_DATABASE", "logistica_scr_staging")
    # SSL corporativo: pon "true" para verificar, "false" si rompe por certificados internos
    athena_verify_ssl: bool = os.getenv("ATHENA_VERIFY_SSL", "false").lower() == "true"

    # CORS (para permitir la UI local)
    cors_allowed_origins: str = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8501")

settings = Settings()
