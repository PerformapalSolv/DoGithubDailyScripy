import os
import subprocess
import time
import argparse
import logging
import signal
import platform
from datetime import datetime
import random

def run_cmd(cmd, timeout=None):
    """执行命令并加入超时控制"""
    try:
        # 创建独立进程组（仅Unix有效）
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=(os.name == 'posix')
        )
        start_time = time.time()
        
        # 实时读取输出
        stdout = []
        stderr = []
        while True:
            # 检查超时
            if timeout and (time.time() - start_time) > timeout:
                raise subprocess.TimeoutExpired(cmd, timeout)
            
            # 读取输出
            out = proc.stdout.read()
            err = proc.stderr.read()
            
            if out:
                stdout.append(out)
                print(out, end='')
            if err:
                stderr.append(err)
                print(err, end='', file=sys.stderr)
            
            # 检查进程是否结束
            if proc.poll() is not None:
                break
            
            time.sleep(0.1)
        
        # 合并输出结果
        full_stdout = ''.join(stdout)
        full_stderr = ''.join(stderr)
        
        # 记录日志
        if proc.returncode != 0:
            logging.error(f"命令执行失败: {cmd}\n错误信息: {full_stderr}")
            return False, full_stderr
        else:
            logging.info(f"命令执行成功: {cmd}\n输出: {full_stdout}")
            return True, full_stdout
    
    except subprocess.TimeoutExpired:
        # 终止进程
        if platform.system() == 'Windows':
            proc.kill()
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        logging.error(f"命令执行超时: {cmd}（超时时间：{timeout}秒）")
        return False, f"Command timed out after {timeout} seconds"

def git_push(repo_path, commit_msg):
    """执行git推送操作，带60秒总超时"""
    os.chdir(repo_path)
    start_time = time.time()
    timeout = 60  # 总超时时间60秒

    # 初始化状态
    success = False
    error_msg = ""
    current_step = "开始操作"

    try:
        logging.info(f"开始Git操作 | 提交信息: {commit_msg}")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 检查超时的嵌套函数
        def check_timeout():
            if time.time() - start_time > timeout:
                raise TimeoutError("操作超时")

        # 执行git add
        current_step = "git add"
        check_timeout()
        add_success, add_output = run_cmd("git add .", timeout=10)
        if not add_success:
            raise Exception("git add失败")

        # 执行git commit
        current_step = "git commit"
        check_timeout()
        commit_success, commit_output = run_cmd(f'git commit -m "{commit_msg}"', timeout=15)
        if not commit_success:
            raise Exception("git commit失败")

        # 执行git push
        current_step = "git push"
        check_timeout()
        push_success, push_output = run_cmd("git push origin master", timeout=35)
        if not push_success:
            raise Exception("git push失败")

        # 记录成功日志
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"Git操作成功 | 开始时间: {current_time} | 结束时间: {end_time}")
        success = True

    except TimeoutError as te:
        error_msg = f"连接超时（{current_step}阶段），操作已终止"
        logging.error(f"{error_msg} | 耗时：{time.time()-start_time:.1f}秒")
    except Exception as e:
        error_msg = f"操作失败：{str(e)}"
        logging.error(f"{error_msg} | 阶段：{current_step}")
    finally:
        if not success:
            print(f"\n错误：{error_msg}")
        return success

def main():
    # 配置日志系统
    logging.basicConfig(
        filename='git_operations.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        encoding='utf-8'
    )

    parser = argparse.ArgumentParser(description="定时多次上传当前文件夹到GitHub")
    parser.add_argument('--count', type=int, default=5, help='上传次数')
    parser.add_argument('--interval', type=int, default=2, help='每次上传间隔（秒）')
    args = parser.parse_args()

    # 添加随机增量
    random_increment = random.randint(1, 30)
    args.count += random_increment
    print(f"实际上传次数为：{args.count}次（原次数+随机增量 {random_increment}）")
    logging.info(f"随机增量生效 | 原次数：{args.count - random_increment} | 新增次数：{random_increment} | 总次数：{args.count}")

    repo_path = os.path.dirname(os.path.abspath(__file__))
    timeout_occurred = False

    for i in range(args.count):
        if timeout_occurred:
            break

        print(f"\n第{i + 1}次上传...")
        commit_msg = f"auto_git_push:{i + 1}"
        
        if not git_push(repo_path, commit_msg):
            print("连接超时，终止后续上传操作")
            timeout_occurred = True
            break

        if i < args.count - 1:
            print(f"等待{args.interval}秒后进行下一次上传...")
            time.sleep(args.interval)

    if timeout_occurred:
        print("\n警告：由于超时导致部分上传未完成！")

if __name__ == "__main__":
    main()