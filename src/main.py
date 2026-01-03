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
    """启动桌面应用程序（PyQt版本）。"""
    print("正在启动 PyQt 桌面应用程序...")
    try:
        from src.desktop.main import run as run_desktop

        run_desktop()
    except ImportError as e:
        print(f"启动桌面应用失败: {e}")
        sys.exit(1)


def start_desktop_tauri():
    """启动桌面应用程序（Tauri版本）。"""
    print("正在启动 Tauri 桌面应用程序...")
    import subprocess
    import os

    try:
        # 切换到 tauri 项目目录
        tauri_dir = os.path.join(os.path.dirname(__file__), "desktop-tauri")
        
        # 检查 npm 是否可用
        subprocess.run(["npm", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"正在 {tauri_dir} 目录下运行 'npm run tauri dev'...")
        # 启动 tauri 开发模式
        # 注意：在 Windows 上需要 shell=True
        subprocess.run(["npm", "run", "tauri", "dev"], cwd=tauri_dir, shell=True, check=True)
        
    except FileNotFoundError:
        print("错误: 未找到 npm，请确保已安装 Node.js。")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"启动 Tauri 应用失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"发生未知错误: {e}")
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
    elif mode == "desktop-tauri":
        start_desktop_tauri()
    elif mode == "cli":
        start_cli()
    else:
        print(f"错误: 未知的 APP_MODE '{mode}'。期望值为 'api', 'desktop', 'desktop-tauri' 或 'cli'。")
        sys.exit(1)


if __name__ == "__main__":
    main()
