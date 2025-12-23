import click

@click.group()
def cli():
    """Cool Agent 命令行工具"""
    pass

@cli.command()
def info():
    """显示应用信息"""
    click.echo("Cool Agent CLI v0.1.0")
    click.echo("这是一个强大的 AI Agent 平台")

@cli.command()
@click.option('--name', default='User', help='要问候的名字')
def hello(name):
    """问候命令"""
    click.echo(f'Hello {name}! 欢迎使用 Cool Agent CLI。')

def run():
    """启动 CLI"""
    cli()

if __name__ == "__main__":
    run()
