import os
import subprocess
import time
import argparse

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"命令执行失败: {cmd}\n错误信息: {result.stderr}")
    else:
        print(result.stdout)
    return result.returncode == 0

def git_push(repo_path, commit_msg):
    os.chdir(repo_path)
    run_cmd("git add .")
    run_cmd(f'git commit -m "{commit_msg}"')
    run_cmd("git push origin master")

def main():
    parser = argparse.ArgumentParser(description="定时多次上传当前文件夹到GitHub")
    parser.add_argument('--count', type=int, default=10, help='上传次数')
    parser.add_argument('--interval', type=int, default=10, help='每次上传间隔（秒）')
    args = parser.parse_args()

    repo_path = os.path.dirname(os.path.abspath(__file__))

    for i in range(args.count):
        print(f"第{i+1}次上传...")
        commit_msg = f"auto_git_push:{i+1}"
        git_push(repo_path, commit_msg)
        if i < args.count - 1:
            print(f"等待{args.interval}秒后进行下一次上传...")
            time.sleep(args.interval)

if __name__ == "__main__":
    main() 