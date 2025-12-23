from src.agents.models import ModelManager, ModelRegistry, model_factory
import asyncio

xf_config = {
    "name": "spark-lite",
    "provider": "xf-spark",
}
xf_spark_model = model_factory.create_model(xf_config)
registry = ModelRegistry()
registry.register(xf_spark_model)
manager = ModelManager(registry)


async def test_generate():
    result = await manager.generate("你好", "spark-lite")
    print(result)


asyncio.run(test_generate())
