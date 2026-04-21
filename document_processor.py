import io
import os
from PIL import Image


def pdf_to_images(pdf_bytes: bytes) -> list[tuple[int, bytes, str]]:
    """
    Convert PDF bytes to a list of (page_number, image_bytes, mime_type).
    Uses pypdfium2 — no poppler dependency needed.
    """
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(pdf_bytes)
    pages = []

    for i, page in enumerate(pdf):
        scale = 2.0  # 2x = ~144 DPI, good balance of quality vs size
        bitmap = page.render(scale=scale, rotation=0)
        pil_image = bitmap.to_pil()

        buf = io.BytesIO()
        pil_image.save(buf, format="JPEG", quality=90)
        pages.append((i + 1, buf.getvalue(), "image/jpeg"))

    return pages


def prepare_image(file_bytes: bytes, filename: str) -> tuple[bytes, str]:
    """
    Normalise an uploaded image to JPEG bytes.
    Returns (image_bytes, mime_type).
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        pages = pdf_to_images(file_bytes)
        if not pages:
            raise ValueError("PDF appears to be empty")
        # For single-image flow, return first page
        return pages[0][1], pages[0][2]

    # Image file — normalise to JPEG
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")

    # Resize if very large (keeps API costs low and speeds up response)
    max_dim = 2048
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue(), "image/jpeg"


def pdf_page_count(pdf_bytes: bytes) -> int:
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(pdf_bytes)
    return len(pdf)
