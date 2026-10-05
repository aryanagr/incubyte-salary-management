from __future__ import annotations

import base64
import os

import httpx


RESEND_API_URL = "https://api.resend.com/emails"


def send_employee_export_email(*, job_id: str, recipient_email: str, csv_bytes: bytes, row_count: int) -> str:
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError("Email delivery is not configured")

    from_email = os.getenv("EXPORT_FROM_EMAIL")
    if not from_email:
        raise RuntimeError("Email sender is not configured")

    filename = f"employee-export-{job_id[:8]}.csv"
    payload = {
        "from": from_email,
        "to": [recipient_email],
        "subject": f"Employee directory export ({row_count:,} rows)",
        "html": (
            "<p>Your Compensation Console export is ready.</p>"
            f"<p>The attached CSV contains <strong>{row_count:,}</strong> employee rows matching the filters "
            "that were active when you requested the export.</p>"
            "<p>This message contains compensation data. Store and forward it only according to your organization's policies.</p>"
        ),
        "attachments": [
            {
                "filename": filename,
                "content": base64.b64encode(csv_bytes).decode("ascii"),
            }
        ],
    }

    response = httpx.post(
        RESEND_API_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Idempotency-Key": f"employee-export/{job_id}",
        },
        timeout=20.0,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Email provider rejected export delivery ({response.status_code})")

    body = response.json()
    message_id = body.get("id")
    if not message_id:
        raise RuntimeError("Email provider response did not include a message id")
    return str(message_id)
