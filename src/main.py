import uvicorn
import sys
from src.config import settings


def start_api():
    """启动 API 服务。"""
    print(f"正在以 {settings.ENVIRONMENT} 模式启动 API 服务...")
    uvicorn.run(
        "src.api.run:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=(settings.ENVIRONMENT == "local"),
        workers=1,
    )


def start_desktop():
    """启动桌面应用程序。"""
    print("正在启动桌面应用程序...")
    try:
        from src.desktop.main import run as run_desktop

        run_desktop()
    except ImportError as e:
        print(f"启动桌面应用失败: {e}")
        sys.exit(1)


def start_cli():
    """启动命令行工具。"""
    try:
        from src.cli.main import run as run_cli

        run_cli()
    except ImportError as e:
        print(f"启动 CLI 失败: {e}")
        sys.exit(1)


def main():
    """主程序入口点。"""
    mode = settings.APP_MODE

    if len(sys.argv) > 1:
        if "--mode" in sys.argv:
            try:
                idx = sys.argv.index("--mode")
                if idx + 1 < len(sys.argv):
                    mode = sys.argv[idx + 1]
                    del sys.argv[idx : idx + 2]
            except ValueError:
                pass

    if mode == "api":
        start_api()
    elif mode == "desktop":
        start_desktop()
    elif mode == "cli":
        start_cli()
    else:
        print(f"错误: 未知的 APP_MODE '{mode}'。期望值为 'api', 'desktop' 或 'cli'。")
        sys.exit(1)


if __name__ == "__main__":
    main()
