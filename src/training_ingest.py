from __future__ import annotations

import io
import re
from typing import Iterable

from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extrai texto legível de um PDF enviado pelo usuário."""
    if not file_bytes:
        raise ValueError("O PDF está vazio.")

    reader = PdfReader(io.BytesIO(file_bytes))
    parts: list[str] = []
    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        if text:
            parts.append(text)

    result = "\n\n".join(parts).strip()
    if not result:
        raise ValueError(
            "Não encontrei texto extraível neste PDF. Se ele for digitalizado como imagem, "
            "será necessário OCR em uma etapa futura."
        )
    return result


def youtube_video_id(url_or_id: str) -> str:
    value = (url_or_id or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value

    patterns = [
        r"(?:youtube\.com/watch\?v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, value, flags=re.I)
        if match:
            return match.group(1)
    raise ValueError("Informe um link válido do YouTube.")


def extract_youtube_transcript(url_or_id: str) -> tuple[str, str]:
    """Busca a transcrição disponível do vídeo, priorizando português."""
    video_id = youtube_video_id(url_or_id)
    transcript = YouTubeTranscriptApi().fetch(video_id, languages=["pt", "pt-BR", "en"])
    text = "\n".join(str(snippet.text).strip() for snippet in transcript if str(snippet.text).strip())
    if not text.strip():
        raise ValueError("A transcrição deste vídeo está vazia ou indisponível.")
    return video_id, text.strip()


def chunk_training_text(text: str, max_chars: int = 8500) -> list[str]:
    """Divide conteúdo longo em blocos compatíveis com ai_training_items.content."""
    clean = re.sub(r"\r\n?", "\n", text or "").strip()
    if not clean:
        return []
    max_chars = max(1000, min(int(max_chars), 9000))

    paragraphs = [part.strip() for part in re.split(r"\n{2,}", clean) if part.strip()]
    if not paragraphs:
        paragraphs = [clean]

    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            start = 0
            while start < len(paragraph):
                chunks.append(paragraph[start : start + max_chars].strip())
                start += max_chars
            continue

        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            current = paragraph

    if current:
        chunks.append(current.strip())
    return [chunk for chunk in chunks if chunk]


def compact_keywords(values: Iterable[str], limit: int = 12) -> list[str]:
    output: list[str] = []
    seen = set()
    for value in values:
        clean = re.sub(r"\s+", " ", str(value or "")).strip()
        key = clean.casefold()
        if clean and key not in seen:
            seen.add(key)
            output.append(clean[:60])
        if len(output) >= limit:
            break
    return output
