from prometheus_client import Counter, Histogram, make_asgi_app
orders_total = Counter("orders_total", "Total number of orders received", ["symbol", "side", "type"])
orders_rejected_total = Counter("orders_rejected_total", "Total rejected orders", ["reason"])
order_latency = Histogram("order_handling_seconds", "Order handling latency in seconds")
metrics_app = make_asgi_app()
