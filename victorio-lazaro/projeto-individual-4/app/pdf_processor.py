import io
import logging
import os
from typing import List

import httpx
import fitz  # PyMuPDF
from openai import AsyncOpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200


class BalancoOperacional(BaseModel):
    total_lancamentos: float | None
    total_vendas: float | None


async def download_pdf(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def semantic_chunking(text: str) -> List[str]:
    paragraphs = text.split("\n\n")
    chunks: List[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        if len(current_chunk) + len(paragraph) + 1 <= CHUNK_SIZE:
            current_chunk += ("\n" + paragraph) if current_chunk else paragraph
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def filter_relevant_chunks(chunks: List[str]) -> List[str]:
    keywords = [
        "lançamento", "lancamento", "lançamentos", "lancamentos",
        "venda", "vendas", "unidade", "unidades",
        "operacional", "prévia", "previa",
        "total", "consolidado",
    ]
    relevant = []
    for chunk in chunks:
        lower = chunk.lower()
        if any(kw in lower for kw in keywords):
            relevant.append(chunk)
    return relevant if relevant else chunks[:5]


async def extract_balanco_from_pdf(url: str) -> BalancoOperacional:
    pdf_bytes = await download_pdf(url)
    text = extract_text_from_pdf(pdf_bytes)
    chunks = semantic_chunking(text)
    relevant_chunks = filter_relevant_chunks(chunks)

    content = "\n---\n".join(relevant_chunks)

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um assistente que extrai dados operacionais de prévias operacionais "
                    "de construtoras brasileiras. Extraia APENAS dados explicitamente presentes no texto. "
                    "NÃO invente valores. Se a informação não estiver presente, retorne null.\n\n"
                    "Retorne um JSON com exatamente dois campos:\n"
                    '- "total_lancamentos": número total de lançamentos (em unidades ou R$ milhões), ou null\n'
                    '- "total_vendas": número total de vendas (em unidades ou R$ milhões), ou null\n\n'
                    "Retorne APENAS o JSON, sem explicações."
                ),
            },
            {
                "role": "user",
                "content": f"Extraia os dados de lançamentos e vendas do seguinte documento:\n\n{content}",
            },
        ],
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content
    balanco = BalancoOperacional.model_validate_json(raw_json)
    return balanco
