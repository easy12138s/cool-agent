import sys
import os
import asyncio
import logging

# 添加项目根目录到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.tools.registry import ToolRegistry
from src.agents.models.model_adapter.xf_spark_model import XFSparkModel
from src.agents.service.react_agent import ReActAgent
from src.config import env

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    print(">>> Initializing ToolRegistry...")
    registry = ToolRegistry()
    registry.scan_skills()
    
    print(f">>> Loaded tools: {[t.name for t in registry.list_tools()]}")
    
    print(">>> Initializing Model (XFSpark)...")
    # 确保 .env 中有相关配置，或者直接在这里硬编码测试（如果 env 加载失败）
    config = {
        "name": "spark-lite",
        "api_key": env.get("XF_SPARK_LITE_API_KEY"),
        "base_url": env.get("XF_SPARK_OPENAI_API_URL"),
        "model": env.get("XF_SPARK_LITE_MODEL_ID"),
    }
    
    if not config["api_key"]:
        print("Error: XF_SPARK_LITE_API_KEY not found in env.")
        return

    model = XFSparkModel(config)
    
    print(">>> Initializing ReActAgent...")
    agent = ReActAgent(model=model, tools=registry)
    
    print(">>> Running Agent...")
    # 测试任务：查找刚刚创建的 react_agent.py 文件
    user_input = "请帮我查找 src/agents/service 目录下包含 'class ReActAgent' 的 python 文件"
    
    try:
        result = await agent.run(user_input)
        print(f"\n>>> Final Result: {result}")
    except Exception as e:
        print(f"\n>>> Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
