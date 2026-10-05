from __future__ import annotations

import asyncio

from vercel.queue import subscribe

from .employee_exports import process_export_job


@subscribe(topic="employee-exports")
async def process_employee_export(message: dict) -> None:
    job_id = str(message.get("job_id", "")).strip()
    if not job_id:
        # Malformed queue payload is not retryable work.
        return
    await asyncio.to_thread(process_export_job, job_id)
