import os
from celery import Celery

BROKER = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq//")
celery = Celery("notify", broker=BROKER, backend=None)

@celery.task(name="notify.send_purchase",autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_purchase(order: dict):
    # qui potresti inviare una mail vera; per ora logghiamo
    print(f"[NOTIFY] Ordine confermato -> user={order['user']}, "
          f"product={order['product_id']}, qty={order['quantity']}")
