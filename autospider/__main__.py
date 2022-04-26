import argparse
import subprocess


parser = argparse.ArgumentParser(description="脚本")
subparsers = parser.add_subparsers(help="子命令")

installcommand = subparsers.add_parser("install", help="安装依赖工具")
installcommand.set_defaults(func=lambda i: install(i))
installcommand.add_argument("-force", dest="force", action="store_true", default=False)
installcommand.add_argument(
    "-browser",
    dest="browser",
    nargs="+",
    choices=["chromium", "firefox", "webkit"],
    default=["chromium"],
)


def install(args: argparse.Namespace):
    cmds = ["playwright", "install"]
    if args.force:
        cmds.append("--force")

    for item in args.browser:
        cmds.append(str(item))

    pipe = subprocess.Popen(
        cmds,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=-1,
    )
    if pipe.stdout is None or pipe.stderr is None:
        pipe.terminate()
        pipe.wait()
        raise Exception("pipe创建失败")
    else:
        # 获取实时输出 当info为b''时停止
        print(cmds)
        for info in iter(pipe.stdout.readline, b""):
            print(info)
        if pipe.returncode != 0:
            print(pipe.stderr.read().decode("utf8"))
        pipe.terminate()
        pipe.wait()


def cmd(args: list[str] = None):
    try:
        argdata = parser.parse_args(args=args)
        if hasattr(argdata, "func"):
            argdata.func(argdata)
        else:
            parser.print_help()
    except Exception as e:
        print(f"未知错误: {e}")


if __name__ == "__main__":
    cmd()
