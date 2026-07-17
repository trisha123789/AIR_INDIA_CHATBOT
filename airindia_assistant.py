import os
import tempfile
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

try:
    from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
    from langchain_core.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:  # pragma: no cover - fallback for deployment environments
    DirectoryLoader = None
    PyPDFLoader = None
    PromptTemplate = None
    ChatGoogleGenerativeAI = None

load_dotenv()

DEFAULT_GEMINI_API_KEY = "AQ.Ab8RN6I5MPk1tD_h_MPUV4CqPrcO3prL67zXFuScO_3wSwju7w"
DEFAULT_PDF_DIR = Path(__file__).resolve().parent / "pdfs"


def get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or DEFAULT_GEMINI_API_KEY
    if not api_key:
        raise RuntimeError(
            "Missing GEMINI_API_KEY. Set it in your environment or .env file."
        )
    return api_key


def load_documents(pdf_dir: Optional[str | os.PathLike] = None, uploaded_file=None):
    if PyPDFLoader is None or DirectoryLoader is None:
        return [], str(pdf_dir or DEFAULT_PDF_DIR)

    if uploaded_file is not None:
        suffix = Path(getattr(uploaded_file, "name", "uploaded.pdf")).suffix or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name
        try:
            return PyPDFLoader(temp_path).load(), temp_path
        finally:
            os.remove(temp_path)

    resolved_dir = Path(pdf_dir or DEFAULT_PDF_DIR)
    if not resolved_dir.exists():
        raise FileNotFoundError(f"PDF directory not found: {resolved_dir}")

    loader = DirectoryLoader(
        path=str(resolved_dir),
        glob="*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=False,
    )
    return loader.load(), str(resolved_dir)


def build_context(documents) -> str:
    if not documents:
        return ""

    texts = []
    for doc in documents:
        text = (doc.page_content or "").strip()
        if text:
            texts.append(text)

    return "\n\n".join(texts)


def answer_question(
    question: str,
    pdf_dir: Optional[str | os.PathLike] = None,
    uploaded_file=None,
    documents=None,
) -> str:
    if ChatGoogleGenerativeAI is None or PromptTemplate is None:
        return "The Gemini assistant dependencies are not available in this deployment yet. Please make sure the app dependencies are installed."

    try:
        if documents is None:
            documents, _ = load_documents(pdf_dir=pdf_dir, uploaded_file=uploaded_file)

        if not documents:
            return "No PDF content was loaded. Please upload a PDF or ensure the pdfs folder contains documents."

        context = build_context(documents)
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are an Air India support assistant. Answer the user's question using only the provided context.
If the answer is not present in the supplied documents, say you do not have enough information.

Context:
{context}

Question:
{question}

Answer:
""",
        )

        chat = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            api_key=get_api_key(),
        )

        result = chat.invoke(prompt.format(context=context, question=question))
        return getattr(result, "content", str(result))
    except Exception as exc:
        return f"I couldn't generate a response right now. Error: {exc}"


def get_document_stats(pdf_dir: Optional[str | os.PathLike] = None, uploaded_file=None):
    try:
        documents, _ = load_documents(pdf_dir=pdf_dir, uploaded_file=uploaded_file)
        return {"pages": len(documents), "chunks": len(documents)}
    except Exception:
        return {"pages": 0, "chunks": 0}
