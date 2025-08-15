from pyathena import connect
from ..config import settings

def get_athena_connection():
    params = dict(
        s3_staging_dir=settings.s3_athena_output,
        region_name=settings.aws_region,
        schema_name=settings.athena_database,
        verify=settings.athena_verify_ssl
    )
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        params.update(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
    return connect(**params)
