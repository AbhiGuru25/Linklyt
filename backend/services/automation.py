import httpx
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def send_to_n8n(data: dict, webhook_url: str):
    """
    Sends processed research data to an external n8n webhook.
    Data format: { url, summary, ai_answer }
    """
    payload = {
        **data,
        "source": "Linklyt AI",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(webhook_url, json=payload)
            resp.raise_for_status()
            logger.info(f"Successfully triggered n8n webhook: {webhook_url}")
            return {"status": "success", "message": "Automation triggered successfully"}
    except Exception as e:
        logger.error(f"Failed to trigger n8n webhook: {str(e)}")
        return {"status": "error", "message": str(e)}
