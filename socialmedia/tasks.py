# This is background task to send emails (confirmation emails for now) by FastAPI app

import logging

import httpx

from socialmedia.config import config

logger = logging.getLogger(__name__)


class APIResponseError(Exception):
    pass


async def send_email(to: str, subject: str, body: str):
    logger.debug(
        f"Sending test email to {to[:3]} with subject: {subject[:3]} and body: {body[:5]}"
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
                auth=("api", config.MAILGUN_API_KEY),
                data={
                    "from": f"Mohamed Ramadan <mailgun@{config.MAILGUN_DOMAIN}>",
                    "to": [to],
                    "subject": subject,
                    "text": body,
                },
            )
            response.raise_for_status()
            logger.debug(response.content)
            return response
        except httpx.HTTPStatusError as e:
            raise APIResponseError(
                f"API request to send email failed with status code : {e.response.status_code}"
            ) from e


async def send_registration_email(email: str, confirmation_url: str):
    return await send_email(
        email,
        "Please confirm your email",
        f"Hi {email}! , You've successfully signed up for our service.\n"
        f"Please confirm your email by clicking on this link : {confirmation_url}",
    )
