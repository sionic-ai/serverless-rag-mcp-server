from pathlib import Path
from typing import List
import os
import mimetypes
import asyncio
import base64


class FileSystemManager:
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path).resolve()
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True)

    def _validate_path(self, path: str | Path) -> Path:
        """주어진 경로가 base_path 내에 있는지 확인"""
        full_path = (self.base_path / path).resolve()
        if not str(full_path).startswith(str(self.base_path)):
            raise ValueError("Invalid path: Access denied")
        return full_path

    async def read_file(self, path: str) -> tuple[str, str]:
        """파일 읽기 (텍스트 파일 기준)"""
        full_path = self._validate_path(path)
        if not full_path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        mime_type, _ = mimetypes.guess_type(str(full_path))
        # 텍스트 파일(UTF-8) 가정
        content = await asyncio.to_thread(full_path.read_text)
        return content, mime_type or "text/plain"

    async def list_directory(self, path: str = "") -> List[dict]:
        """디렉토리 내용 나열"""
        full_path = self._validate_path(path)
        if not full_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")

        items = []
        for item in full_path.iterdir():
            rel_path = str(item.relative_to(self.base_path))
            items.append(
                {
                    "name": item.name,
                    "path": rel_path,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                }
            )
        return items

    async def search_files(self, pattern: str) -> List[dict]:
        """파일 검색"""
        results = []
        async for path in self._walk_async(self.base_path):
            if pattern.lower() in path.name.lower():
                rel_path = str(path.relative_to(self.base_path))
                results.append(
                    {
                        "name": path.name,
                        "path": rel_path,
                        "type": "directory" if path.is_dir() else "file",
                    }
                )
        return results

    async def _walk_async(self, path: Path):
        """비동기 파일 시스템 탐색"""
        dirs = []
        files = []
        async for entry in asyncio.to_thread(os.scandir, str(path)):
            if entry.is_dir():
                dirs.append(entry)
            else:
                files.append(entry)

        for entry in files:
            yield Path(entry.path)

        for entry in dirs:
            async for x in self._walk_async(Path(entry.path)):
                yield x

    # ------------------------------------------------------------------------
    # 새로 추가: 파일 업로드 로직 (Base64 컨텐츠 받기)
    # ------------------------------------------------------------------------
    async def upload_file(self, path: str, b64_content: str) -> None:
        """
        fileContent(Base64) 를 디코딩해서 로컬 파일로 저장.
        path: 저장될 파일 경로 (base_path 하위)
        b64_content: base64로 인코딩된 바이너리(또는 텍스트) 내용
        """
        full_path = self._validate_path(path)

        # 디렉토리가 아닌, 상위 디렉토리가 존재하는지 확인
        parent_dir = full_path.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)

        # Base64 디코딩
        raw_data = base64.b64decode(b64_content)

        # 바이너리 쓰기
        # (만약 텍스트 파일만 취급한다면 `write_text`로 바꿔도 됨)
        await asyncio.to_thread(full_path.write_bytes, raw_data)
