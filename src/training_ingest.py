from __future__ import annotations

import io
import ipaddress
import re
import socket
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi


MAX_REMOTE_FILE_BYTES = 12 * 1024 * 1024
MAX_REDIRECTS = 3
_REMOTE_TIMEOUT = (5, 15)


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extrai texto legível de bytes de PDF mantidos apenas em memória."""
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
            "será necessário disponibilizar uma versão com texto pesquisável."
        )
    return result


def _validate_public_url(url: str) -> str:
    value = (url or "").strip()
    parsed = urlparse(value)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname:
        raise ValueError("Informe um link público válido começando com https:// ou http://.")
    if parsed.username or parsed.password:
        raise ValueError("Links com usuário/senha embutidos não são permitidos.")

    host = parsed.hostname.lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError("Links locais ou privados não são permitidos.")

    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("Não foi possível localizar o endereço informado.") from exc

    addresses = {info[4][0] for info in infos}
    if not addresses:
        raise ValueError("O endereço informado não pôde ser validado.")
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise ValueError("O endereço informado não pôde ser validado.") from exc
        if not ip.is_global:
            raise ValueError("Links que apontam para redes privadas, locais ou reservadas não são permitidos.")
    return value


def download_public_document(url: str, max_bytes: int = MAX_REMOTE_FILE_BYTES) -> tuple[str, bytes, str]:
    """Baixa temporariamente uma fonte pública sem gravá-la no Storage.

    Redirecionamentos são seguidos manualmente para que cada destino seja validado
    e não seja possível apontar o servidor para redes privadas (SSRF).
    """
    current = _validate_public_url(url)
    headers = {"User-Agent": "RENOVA-Financas-Training/1.0"}

    for _ in range(MAX_REDIRECTS + 1):
        response = requests.get(
            current,
            headers=headers,
            timeout=_REMOTE_TIMEOUT,
            stream=True,
            allow_redirects=False,
        )

        if response.status_code in {301, 302, 303, 307, 308}:
            location = response.headers.get("Location")
            response.close()
            if not location:
                raise ValueError("O link redirecionou sem informar o novo endereço.")
            current = _validate_public_url(urljoin(current, location))
            continue

        response.raise_for_status()
        declared = response.headers.get("Content-Length")
        if declared:
            try:
                if int(declared) > max_bytes:
                    response.close()
                    raise ValueError("O material excede o limite de 12 MB para leitura temporária.")
            except ValueError:
                if declared.isdigit():
                    raise

        data = bytearray()
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            data.extend(chunk)
            if len(data) > max_bytes:
                response.close()
                raise ValueError("O material excede o limite de 12 MB para leitura temporária.")

        content_type = (response.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
        final_url = current
        response.close()
        return final_url, bytes(data), content_type

    raise ValueError("O link possui redirecionamentos demais.")


def extract_pdf_text_from_url(url: str) -> tuple[str, str]:
    """Lê um PDF por URL pública, processa em memória e não armazena o arquivo bruto."""
    final_url, data, content_type = download_public_document(url)
    parsed = urlparse(final_url)
    is_pdf = content_type in {"application/pdf", "application/x-pdf"} or parsed.path.lower().endswith(".pdf")
    if not is_pdf:
        raise ValueError("O link informado não parece apontar para um arquivo PDF.")
    return final_url, extract_pdf_text(data)


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
