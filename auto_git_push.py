# python auto_git_push.py --count 3 --interval 120
import os
import subprocess
import time
import argparse

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"命令: {cmd}")
    print(f"标准输出: {result.stdout}")
    print(f"标准错误: {result.stderr}")
    return result.returncode == 0, result.stdout, result.stderr

def is_git_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))

def has_changes():
    code, out, _ = run_cmd("git status --porcelain")
    return bool(out.strip())

def check_git_config():
    code_name, out_name, _ = run_cmd("git config user.name")
    code_email, out_email, _ = run_cmd("git config user.email")
    if not out_name.strip() or not out_email.strip():
        print("请先设置git用户名和邮箱：")
        print("git config --global user.name \"你的名字\"")
        print("git config --global user.email \"你的邮箱\"")
        return False
    return True

def git_push(repo_path, commit_msg):
    os.chdir(repo_path)
    if not is_git_repo(repo_path):
        print("当前目录不是git仓库，请先初始化并添加远程仓库。")
        return
    if not check_git_config():
        return
    run_cmd("git add .")
    if not has_changes():
        print("没有检测到更改，跳过提交。")
        return
    run_cmd(f'git commit -m "{commit_msg}"')
    run_cmd("git push")

def main():
    parser = argparse.ArgumentParser(description="定时多次上传当前文件夹到GitHub")
    parser.add_argument('--count', type=int, default=1, help='上传次数')
    parser.add_argument('--interval', type=int, default=60, help='每次上传间隔（秒）')
    args = parser.parse_args()

    repo_path = os.path.dirname(os.path.abspath(__file__))

    for i in range(args.count):
        print(f"第{i+1}次上传...")
        commit_msg = f"自动上传：第{i+1}次"
        git_push(repo_path, commit_msg)
        if i < args.count - 1:
            print(f"等待{args.interval}秒后进行下一次上传...")
            time.sleep(args.interval)

if __name__ == "__main__":
    main() 