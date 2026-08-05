"""Валидаторы для материалов курса и урока."""

import re

from rest_framework.serializers import ValidationError


def validate_youtube_url(value):
    """Разрешает только ссылки на youtube.com. Текст без ссылок допускается."""
    if not value:
        return value

    links = re.findall(r"https?://[^\s<>\"']+", value)
    if not links and re.match(r"^(https?://|www\.)", value.strip(), re.IGNORECASE):
        links = [value.strip()]

    if not links:
        return value

    for link in links:
        link_lower = link.lower()
        if "youtube.com" not in link_lower and "youtu.be" not in link_lower:
            raise ValidationError("Разрешены только ссылки на youtube.com")

    return value
