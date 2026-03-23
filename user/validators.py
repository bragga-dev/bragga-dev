import os
from django.core.exceptions import ValidationError
from PIL import Image


def validate_image_file(value):
    if not value:
        return

    valid_formats = {"JPEG", "PNG", "WEBP"}
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    max_size_mb = 5
    max_width = 4000
    max_height = 4000

    # 🔹 1. Valida extensão (rápido, evita processamento desnecessário)
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Extensão inválida. Use JPG, PNG ou WEBP.")

    # 🔹 2. Valida tamanho antes de abrir (performance)
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"O arquivo não pode ultrapassar {max_size_mb}MB.")

    try:
        # 🔹 3. Abre e valida imagem
        img = Image.open(value)
        img.verify()
    except Exception:
        raise ValidationError("Arquivo inválido ou corrompido.")

    # 🔹 4. Reabre corretamente após verify()
    try:
        value.seek(0)
        img = Image.open(value)
    except Exception:
        raise ValidationError("Erro ao processar a imagem.")

    # 🔹 5. Valida formato real (segurança contra spoof)
    if img.format.upper() not in valid_formats:
        raise ValidationError("Formato inválido. Use JPG, PNG ou WEBP.")

    # 🔹 6. Valida dimensões
    width, height = img.size
    if width > max_width or height > max_height:
        raise ValidationError(
            f"A imagem não pode ultrapassar {max_width}x{max_height}px."
        )

    # 🔹 7. Proteção contra BOMBA de imagem (ataque DoS)
    if width * height > 16_000_000:  # ~16MP
        raise ValidationError("Imagem muito grande (risco de processamento).")

    return value