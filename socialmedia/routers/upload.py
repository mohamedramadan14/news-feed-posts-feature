import logging
import tempfile

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status

from socialmedia.libs.b2 import b2_upload_file

"""
UploadFile : handles file upload in async manner by splitting file into chunks each chunk has size limit of ex: 512KB each chunk is uploaded to local server 1 at a time , process it in background to temp file  and then uploaded to B2 then delete temp file
"""


logger = logging.getLogger(__name__)

router = APIRouter()

CHUNK_SIZE = 1024 * 1024


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload(file: UploadFile):
    try:
        with tempfile.NamedTemporaryFile() as temp_file:
            filename = temp_file.name
            logger.debug(f"Saving uploaded file temporarily to {filename}")
            async with aiofiles.open(filename, "wb") as f:
                chunk = await file.read(CHUNK_SIZE)
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)
            file_url = b2_upload_file(local_file_path=filename, file_name=file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There's an error while uploading file : {str(e)}",
        )
    return {
        "detail": f"File {file.filename} uploaded successfully",
        "file_url": file_url,
    }
