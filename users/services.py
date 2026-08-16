"""Сервисные функции для работы со Stripe API."""

import requests
from django.conf import settings
from requests.exceptions import RequestException

STRIPE_API_URL = "https://api.stripe.com/v1"


class StripeServiceError(Exception):
    """Ошибка при обращении к Stripe."""


def _get_headers() -> dict:
    """Заголовки авторизации Stripe."""
    return {"Authorization": f"Bearer {settings.STRIPE_API_KEY}"}


def _stripe_request(method: str, endpoint: str, data: dict | None = None) -> dict:
    """Выполняет запрос к Stripe и возвращает JSON."""
    url = f"{STRIPE_API_URL}{endpoint}"
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=_get_headers(),
            data=data,
            timeout=30,
        )
    except RequestException as exc:
        raise StripeServiceError(str(exc)) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise StripeServiceError("Некорректный ответ Stripe") from exc

    if not response.ok:
        error = payload.get("error", {})
        message = error.get("message") or response.text
        raise StripeServiceError(message)

    return payload


def create_stripe_product(name: str) -> dict:
    """Создаёт продукт в Stripe."""
    return _stripe_request("POST", "/products", data={"name": name})


def create_stripe_price(product_id: str, amount) -> dict:
    """Создаёт цену в Stripe. Сумма передаётся в копейках."""
    unit_amount = int(amount * 100)
    return _stripe_request(
        "POST",
        "/prices",
        data={
            "product": product_id,
            "unit_amount": unit_amount,
            "currency": "rub",
        },
    )


def create_stripe_session(price_id: str) -> dict:
    """Создаёт Checkout Session и возвращает ссылку на оплату."""
    return _stripe_request(
        "POST",
        "/checkout/sessions",
        data={
            "success_url": settings.STRIPE_SUCCESS_URL,
            "cancel_url": settings.STRIPE_CANCEL_URL,
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": 1,
            "mode": "payment",
        },
    )


def retrieve_stripe_session(session_id: str) -> dict:
    """Получает данные сессии Stripe по идентификатору."""
    return _stripe_request("GET", f"/checkout/sessions/{session_id}")
