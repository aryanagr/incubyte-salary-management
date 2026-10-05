from __future__ import annotations

import os
from datetime import timedelta

from vercel.queue import send

EXPORT_TOPIC = "employee-exports"


async def enqueue_employee_export(job_id: str) -> str | None:
    # Tests and plain local Python runs do not have Vercel queue credentials.
    # `vercel dev` injects VERCEL_QUEUE_BASE_URL / token, while deployed
    # functions expose VERCEL=1 and OIDC-backed queue authentication.
    if os.getenv("VERCEL") != "1" and not os.getenv("VERCEL_QUEUE_BASE_URL"):
        return None

    return await send(
        EXPORT_TOPIC,
        {"job_id": job_id},
        idempotency_key=f"employee-export/{job_id}",
        retention=timedelta(days=1),
    )
