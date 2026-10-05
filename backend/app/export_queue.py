from __future__ import annotations

import os
from datetime import timedelta

from vercel.queue import send

EXPORT_TOPIC = "employee-exports"


async def enqueue_employee_export(job_id: str) -> str | None:
    # `vercel dev` injects queue credentials and deployed functions receive
    # OIDC-backed queue authentication. Outside those environments, failing
    # explicitly is safer than claiming a job was queued when no worker can
    # ever consume it.
    if os.getenv("VERCEL") != "1" and not os.getenv("VERCEL_QUEUE_BASE_URL"):
        raise RuntimeError("Employee export queue is not configured")

    return await send(
        EXPORT_TOPIC,
        {"job_id": job_id},
        idempotency_key=f"employee-export/{job_id}",
        retention=timedelta(days=1),
    )
