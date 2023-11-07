import logging
from functools import lru_cache

import b2sdk.v2 as b2

from socialmedia.config import config

logger = logging.getLogger(__name__)


@lru_cache()
def b2_api():
    logger.debug("Creating and authorizing B2 API")
    info = b2.InMemoryAccountInfo()
    b2_api = b2.B2Api(info)

    b2_api.authorize_account(
        "production",
        config.B2_KEY_ID,
        config.B2_APPLICATION_KEY,
    )
    return b2_api


@lru_cache()
def b2_get_bucket(api: b2.B2Api):
    return api.get_bucket_by_name(config.B2_BUCKET_NAME)


def b2_upload_file(local_file_path: str, file_name: str):
    api = b2_api()

    logger.debug(f"Uploading file {local_file_path} to B2")

    uploaded_file = b2_get_bucket(api).upload_local_file(
        local_file=local_file_path, file_name=file_name
    )

    download_url = api.get_download_url_for_fileid(uploaded_file.id_)

    logger.debug(
        f"Uploaded file {local_file_path} to B2 successfully and download url is {download_url}"
    )

    return download_url
