from pathlib import Path
from typing import Protocol

from azure.storage.blob import BlobServiceClient


class PersistenceClient(Protocol):
    def persist(self, content: str, object_name: str) -> str:
        """Persiste o conteúdo e retorna sua localização."""


class LocalPersistenceClient:
    def __init__(self, path: str):
        configured_path = Path(path)
        self.path = (
            configured_path
            if configured_path.is_absolute()
            else Path.cwd() / configured_path
        )

    def persist(self, content: str, object_name: str) -> str:
        destination = self.path / object_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        return str(destination.resolve())


class AzureBlobPersistenceClient:
    def __init__(self, connection_string: str, container: str):
        self.connection_string = connection_string
        self.container_name = container

    def persist(self, content: str, object_name: str) -> str:
        service = BlobServiceClient.from_connection_string(self.connection_string)
        container = service.get_container_client(self.container_name)
        blob = container.get_blob_client(object_name.replace("\\", "/"))
        blob.upload_blob(content, overwrite=True)
        return blob.url
