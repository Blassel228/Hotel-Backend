import asyncio
from typing import AsyncIterator

from aiobotocore.session import ClientCreatorContext, get_session
from loguru import logger

from app.core import settings
from app.core.exc import StorageFailedFetchFileException, StorageMaxRetryError


class StorageService:
    def __init__(self) -> None:
        self.bucket_name = settings.storage.BUCKET_NAME
        self.session = get_session()

    async def create_client(self) -> ClientCreatorContext:
        """Init session for connection to STORAGE"""
        return self.session.create_client(
            "s3",
            region_name=settings.storage.REGION_NAME,
            endpoint_url=f"https://{settings.storage.ENDPOINT_URL}",
            aws_secret_access_key=settings.storage.SECRET_KEY,
            aws_access_key_id=settings.storage.ACCESS_KEY,
        )

    async def get_file_by_name(self, file_name: str) -> bytes | None:
        """
        Retrieve object by file name which represent path to file in S3.

        Args:
            file_name: object path

        Returns:
            if jsonify object in file, otherwise byte string
        """
        try:
            async with await self.create_client() as s3:
                s3_file = await s3.get_object(Bucket=self.bucket_name, Key=file_name)
                return await s3_file.get("Body").read()
        except Exception as e:
            logger.error(e)

    async def get_size(self, object_name: str) -> int:
        async with await self.create_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_name)

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                raise StorageFailedFetchFileException(error=response["ResponseMetadata"])

            return response["ContentLength"]

    async def stream_file_from_s3(self, object_name: str) -> AsyncIterator[bytes]:
        async with await self.create_client() as client:
            try:
                response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
                async for chunk in response["Body"].iter_chunks():
                    yield chunk
            except StorageFailedFetchFileException:
                raise
            except Exception as e:
                raise StorageFailedFetchFileException(error=e) from e

    async def get_files_with_prefix(self, prefix: str) -> list:
        """
        Retrieve objects by file name prefix.

        Args:
            prefix: part of the name

        Returns:
            list of strings with file paths
        """
        async with await self.create_client() as s3:
            paginator = s3.get_paginator("list_objects_v2")
            async for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                folder_files = [obj["Key"] for obj in page.get("Contents", [])]

        logger.debug(f"Found files. PREFIX:{prefix}. FILES:{folder_files}")
        return folder_files

    async def upload_to_s3(self, data: bytes, object_name: str, is_public: bool = False) -> str:
        """
        Upload bytes data into file with object_name name .

        Args:
            data: bytes content
            object_name: file name to upload
            is_public: object is public or not

        Raises:
            StorageMaxRetryError: if max retries reached

        Returns:
            file path in S3 bucket
        """
        max_retries = settings.storage.UPLOAD_RETRIES
        delay = settings.storage.UPLOAD_DELAY
        for _attempt in range(max_retries):
            try:
                async with await self.create_client() as s3:
                    if is_public:
                        await s3.put_object(Bucket=self.bucket_name, Key=object_name, Body=data, ACL="public-read")
                    else:
                        await s3.put_object(Bucket=self.bucket_name, Key=object_name, Body=data)
                    logger.info(f"File was uploaded. URL: {object_name}")
                    return object_name

            except Exception as e:
                logger.exception(e)
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

        else:
            error = StorageMaxRetryError
            logger.exception(error)
            raise error

    async def delete_files(self, file_links: list[str]) -> None:
        logger.debug(f"Deleting files from storage storage. Files: {file_links}")

        if file_links:
            async with await self.create_client() as s3:
                delete_requests = [{"Key": link} for link in file_links]
                await s3.delete_objects(Bucket=self.bucket_name, Delete={"Objects": delete_requests})
                logger.info(f"Successfully deleted files from storage: {file_links}")
        else:
            logger.info("No files to delete from storage.")


storage_service = StorageService()
