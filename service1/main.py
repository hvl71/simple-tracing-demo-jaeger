from fastapi import FastAPI
import requests
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

app = FastAPI()

# Configure tracing
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({"service.name": "service1"})
    )
)
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer(__name__)

@app.get("/process/{item_id}")
def process_item(item_id: int):
    with tracer.start_as_current_span("service1-process"):
        response = requests.get(f"http://service2:8002/finalize/{item_id}")
        return response.json()
