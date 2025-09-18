import os
import sys
import subprocess
import ctypes
import tempfile
from typing import Optional, List, Union


class UACManager:
    """Windows UAC权限管理器"""
    
    def __init__(self):
        self._is_admin = None
    
    def is_admin(self) -> bool:
        """检查当前进程是否具有管理员权限"""
        if self._is_admin is None:
            try:
                self._is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                self._is_admin = False
        return self._is_admin
    
    def request_admin_privileges(self) -> bool:
        """请求管理员权限（重启当前脚本）"""
        if self.is_admin():
            return True
        
        try:
            # 以管理员身份重新启动当前脚本
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                " ".join(sys.argv), 
                None, 
                1
            )
            return True
        except Exception as e:
            print(f"请求管理员权限失败: {e}")
            return False
    
    def run_as_admin(self, command: Union[str, List[str]], 
                     wait: bool = True, 
                     capture_output: bool = False,
                     working_dir: Optional[str] = None) -> Optional[subprocess.CompletedProcess]:
        """以管理员权限执行命令
        
        Args:
            command: 要执行的命令（字符串或列表）
            wait: 是否等待命令执行完成
            capture_output: 是否捕获输出
            working_dir: 工作目录
            
        Returns:
            如果wait=True，返回CompletedProcess对象；否则返回None
        """
        if isinstance(command, list):
            command = " ".join(command)
        
        try:
            if self.is_admin():
                # 如果已经是管理员，直接执行
                if capture_output:
                    result = subprocess.run(
                        command, 
                        shell=True, 
                        capture_output=True, 
                        text=True,
                        cwd=working_dir
                    )
                    return result
                else:
                    if wait:
                        result = subprocess.run(command, shell=True, cwd=working_dir)
                        return result
                    else:
                        subprocess.Popen(command, shell=True, cwd=working_dir)
                        return None
            else:
                # 需要UAC提权
                return self._run_elevated_command(command, wait, capture_output, working_dir)
                
        except Exception as e:
            print(f"执行命令失败: {e}")
            return None
    
    def _run_elevated_command(self, command: str, 
                             wait: bool = True, 
                             capture_output: bool = False,
                             working_dir: Optional[str] = None) -> Optional[subprocess.CompletedProcess]:
        """通过UAC提权执行命令"""
        try:
            if capture_output:
                # 如果需要捕获输出，创建临时脚本
                return self._run_with_output_capture(command, working_dir)
            else:
                # 直接通过PowerShell以管理员身份执行
                ps_command = f'Start-Process cmd -ArgumentList "/c {command}" -Verb RunAs'
                if not wait:
                    ps_command += ' -WindowStyle Hidden'
                
                if working_dir:
                    ps_command = f'cd "{working_dir}"; {ps_command}'
                
                result = subprocess.run([
                    'powershell', '-Command', ps_command
                ], capture_output=False)
                
                if wait:
                    return subprocess.CompletedProcess(
                        args=command,
                        returncode=result.returncode
                    )
                return None
                
        except Exception as e:
            print(f"UAC提权执行失败: {e}")
            return None
    
    def _run_with_output_capture(self, command: str, 
                                working_dir: Optional[str] = None) -> Optional[subprocess.CompletedProcess]:
        """通过临时脚本捕获提权命令的输出"""
        try:
            # 创建临时目录和文件
            temp_dir = tempfile.mkdtemp()
            script_file = os.path.join(temp_dir, "elevated_cmd.bat")
            output_file = os.path.join(temp_dir, "output.txt")
            error_file = os.path.join(temp_dir, "error.txt")
            
            # 创建批处理脚本
            script_content = f"""@echo off
cd /d "{working_dir if working_dir else os.getcwd()}"
({command}) > "{output_file}" 2> "{error_file}"
echo %ERRORLEVEL% > "{os.path.join(temp_dir, 'exitcode.txt')}"
"""
            
            with open(script_file, 'w', encoding='gbk') as f:
                f.write(script_content)
            
            # 以管理员身份执行批处理脚本
            ps_command = f'Start-Process "{script_file}" -Verb RunAs -Wait -WindowStyle Hidden'
            subprocess.run(['powershell', '-Command', ps_command], check=True)
            
            # 读取结果
            stdout = ""
            stderr = ""
            returncode = 0
            
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='gbk', errors='ignore') as f:
                    stdout = f.read()
            
            if os.path.exists(error_file):
                with open(error_file, 'r', encoding='gbk', errors='ignore') as f:
                    stderr = f.read()
            
            exitcode_file = os.path.join(temp_dir, 'exitcode.txt')
            if os.path.exists(exitcode_file):
                with open(exitcode_file, 'r') as f:
                    try:
                        returncode = int(f.read().strip())
                    except Exception:
                        returncode = 0
            
            # 清理临时文件
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except Exception:
                pass
            
            return subprocess.CompletedProcess(
                args=command,
                returncode=returncode,
                stdout=stdout,
                stderr=stderr
            )
            
        except Exception as e:
            print(f"捕获输出执行失败: {e}")
            return None
    
    def run_powershell_as_admin(self, script: str, 
                               wait: bool = True,
                               capture_output: bool = False) -> Optional[subprocess.CompletedProcess]:
        """以管理员权限执行PowerShell脚本
        
        Args:
            script: PowerShell脚本内容
            wait: 是否等待执行完成
            capture_output: 是否捕获输出
            
        Returns:
            CompletedProcess对象或None
        """
        try:
            if self.is_admin():
                # 已经是管理员，直接执行
                if capture_output:
                    result = subprocess.run([
                        'powershell', '-Command', script
                    ], capture_output=True, text=True)
                    return result
                else:
                    if wait:
                        result = subprocess.run(['powershell', '-Command', script])
                        return result
                    else:
                        subprocess.Popen(['powershell', '-Command', script])
                        return None
            else:
                # 需要UAC提权
                ps_command = f'Start-Process powershell -ArgumentList "-Command", "{script}" -Verb RunAs'
                if not wait:
                    ps_command += ' -WindowStyle Hidden'
                
                result = subprocess.run(['powershell', '-Command', ps_command])
                
                if wait:
                    return subprocess.CompletedProcess(
                        args=script,
                        returncode=result.returncode
                    )
                return None
                
        except Exception as e:
            print(f"PowerShell提权执行失败: {e}")
            return None
    
    def check_uac_level(self) -> dict:
        """检查UAC设置级别"""
        try:
            import winreg
            
            # 读取UAC相关注册表项
            uac_info = {}
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System") as key:
                try:
                    uac_info['EnableLUA'] = winreg.QueryValueEx(key, "EnableLUA")[0]
                except Exception:
                    uac_info['EnableLUA'] = None
                
                try:
                    uac_info['ConsentPromptBehaviorAdmin'] = winreg.QueryValueEx(key, "ConsentPromptBehaviorAdmin")[0]
                except Exception:
                    uac_info['ConsentPromptBehaviorAdmin'] = None
                
                try:
                    uac_info['ConsentPromptBehaviorUser'] = winreg.QueryValueEx(key, "ConsentPromptBehaviorUser")[0]
                except Exception:
                    uac_info['ConsentPromptBehaviorUser'] = None
                
                try:
                    uac_info['PromptOnSecureDesktop'] = winreg.QueryValueEx(key, "PromptOnSecureDesktop")[0]
                except Exception:
                    uac_info['PromptOnSecureDesktop'] = None
            
            # 解释UAC级别
            if uac_info['EnableLUA'] == 0:
                uac_info['level'] = "关闭"
                uac_info['description'] = "UAC已关闭"
            elif uac_info['ConsentPromptBehaviorAdmin'] == 0:
                uac_info['level'] = "从不通知"
                uac_info['description'] = "不会通知用户"
            elif uac_info['ConsentPromptBehaviorAdmin'] == 5 and uac_info['PromptOnSecureDesktop'] == 0:
                uac_info['level'] = "仅在应用尝试更改时通知（不调暗桌面）"
                uac_info['description'] = "中等安全级别"
            elif uac_info['ConsentPromptBehaviorAdmin'] == 5 and uac_info['PromptOnSecureDesktop'] == 1:
                uac_info['level'] = "仅在应用尝试更改时通知（默认）"
                uac_info['description'] = "推荐的安全级别"
            elif uac_info['ConsentPromptBehaviorAdmin'] == 2:
                uac_info['level'] = "始终通知"
                uac_info['description'] = "最高安全级别"
            else:
                uac_info['level'] = "未知"
                uac_info['description'] = "无法确定UAC级别"
            
            return uac_info
            
        except Exception as e:
            return {
                'error': str(e),
                'level': '检测失败',
                'description': '无法读取UAC设置'
            }


# 使用示例和测试
if __name__ == "__main__":
    uac = UACManager()
    
    print(f"当前是否为管理员: {uac.is_admin()}")
    
    # 检查UAC级别
    uac_info = uac.check_uac_level()
    print(f"UAC级别: {uac_info.get('level', '未知')}")
    print(f"描述: {uac_info.get('description', '无描述')}")
    
    # 测试命令执行
    print("\n测试执行命令:")
    
    # 简单命令测试
    result = uac.run_as_admin("echo Hello from elevated process", capture_output=True)
    if result:
        print(f"返回码: {result.returncode}")
        print(f"输出: {result.stdout}")
    
    # PowerShell命令测试
    ps_result = uac.run_powershell_as_admin("Get-Process | Select-Object -First 5", capture_output=True)
    if ps_result:
        print(f"PowerShell返回码: {ps_result.returncode}")
        print(f"PowerShell输出: {ps_result.stdout}")
    
    print("\n注意: 某些命令可能需要UAC提权对话框确认")
