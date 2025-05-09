import os
import subprocess
import time
import argparse
import logging
from datetime import datetime


def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"命令执行失败: {cmd}\n错误信息: {result.stderr}")
        print(f"命令执行失败: {cmd}\n错误信息: {result.stderr}")
    else:
        logging.info(f"命令执行成功: {cmd}\n输出: {result.stdout}")
        print(result.stdout)
    return result.returncode == 0


def git_push(repo_path, commit_msg):
    os.chdir(repo_path)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间

    # 记录开始时间
    logging.info(f"开始Git操作 | 提交信息: {commit_msg}")

    # 执行git操作
    add_success = run_cmd("git add .")
    commit_success = run_cmd(f'git commit -m "{commit_msg}"')
    push_success = run_cmd("git push origin master")

    # 记录结束时间和结果
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if all([add_success, commit_success, push_success]):
        logging.info(f"Git操作成功 | 开始时间: {current_time} | 结束时间: {end_time}")
    else:
        logging.error(f"Git操作失败 | 开始时间: {current_time} | 结束时间: {end_time}")

    return True


def main():
    # 配置日志系统
    logging.basicConfig(
        filename='git_operations.log',  # 日志文件名
        filemode='a',  # 追加模式
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        encoding='utf-8'  # 防止中文乱码
    )

    parser = argparse.ArgumentParser(description="定时多次上传当前文件夹到GitHub")
    parser.add_argument('--count', type=int, default=10, help='上传次数')
    parser.add_argument('--interval', type=int, default=10, help='每次上传间隔（秒）')
    args = parser.parse_args()

    repo_path = os.path.dirname(os.path.abspath(__file__))

    for i in range(args.count):
        print(f"第{i + 1}次上传...")
        commit_msg = f"auto_git_push:{i + 1}"
        git_push(repo_path, commit_msg)
        if i < args.count - 1:
            print(f"等待{args.interval}秒后进行下一次上传...")
            time.sleep(args.interval)


if __name__ == "__main__":
    main()