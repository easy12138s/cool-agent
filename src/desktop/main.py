import time


def run():
    """启动桌面应用程序主逻辑"""
    print("Desktop App: 初始化中...")
    print("Desktop App: 正在加载组件...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDesktop App: 正在退出...")


if __name__ == "__main__":
    run()
