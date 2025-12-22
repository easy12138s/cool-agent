from dotenv import load_dotenv
import os
from .settings import *

# 加载.env文件
load_dotenv()

class Env:
    def get(self, key, default=None):
        return os.getenv(key, default)

    def __getattr__(self, key):
        # 支持 env.KEY_NAME 的方式访问
        value = self.get(key)
        if value is None:
            raise AttributeError(f"环境变量 {key} 未定义")
        return value


env = Env()