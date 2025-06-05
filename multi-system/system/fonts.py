# pip install fonttools

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import tempfile


class FontInfo:
    """字体信息类"""
    
    def __init__(self, name: str = "", path: str = "", font_type: str = "", 
                 size: int = 0, family_name: str = "", style_name: str = "",
                 full_name: str = "", postscript_name: str = "", glyph_count: int = 0):
        self.name = name
        self.path = path
        self.type = font_type
        self.size = size
        self.family_name = family_name
        self.style_name = style_name
        self.full_name = full_name
        self.postscript_name = postscript_name
        self.glyph_count = glyph_count
    
    def __str__(self) -> str:
        return f"{self.name} ({self.type}) - {self.size} bytes"
    
    def __repr__(self) -> str:
        return f"FontInfo(name='{self.name}', type='{self.type}', size={self.size})"
    
    def to_dict(self) -> Dict[str, any]:
        """转换为字典格式（兼容性方法）"""
        return {
            'name': self.name,
            'path': self.path,
            'type': self.type,
            'size': self.size,
            'family_name': self.family_name,
            'style_name': self.style_name,
            'full_name': self.full_name,
            'postscript_name': self.postscript_name,
            'glyph_count': self.glyph_count
        }


class FontManager:
    """跨平台字体管理器"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.font_paths = self._get_font_paths()
    
    def _get_font_paths(self) -> Dict[str, List[str]]:
        """获取系统字体路径"""
        if self.system == 'windows':
            return {
                'system': [
                    os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
                ],
                'user': [
                    os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Microsoft', 'Windows', 'Fonts'),
                ]
            }
        elif self.system == 'darwin':  # macOS
            return {
                'system': [
                    '/System/Library/Fonts',
                    '/Library/Fonts',
                ],
                'user': [
                    os.path.join(os.path.expanduser('~'), 'Library', 'Fonts'),
                ]
            }
        elif self.system == 'linux':
            return {
                'system': [
                    '/usr/share/fonts',
                    '/usr/local/share/fonts',
                ],
                'user': [
                    os.path.join(os.path.expanduser('~'), '.fonts'),
                    os.path.join(os.path.expanduser('~'), '.local', 'share', 'fonts'),
                ]
            }
        else:
            raise OSError(f"不支持的操作系统: {self.system}")
    
    def list_installed_fonts(self, user_only: bool = False) -> List[FontInfo]:
        """列举已安装的字体
        
        Args:
            user_only: 是否只列举用户字体
            
        Returns:
            字体信息列表
        """
        fonts = []
        paths_to_check = []
        
        if user_only:
            paths_to_check = self.font_paths['user']
        else:
            paths_to_check = self.font_paths['system'] + self.font_paths['user']
        
        for font_dir in paths_to_check:
            if os.path.exists(font_dir):
                for root, dirs, files in os.walk(font_dir):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.otf')):
                            font_path = os.path.join(root, file)
                            font_info = FontInfo(
                                name=os.path.splitext(file)[0],
                                path=font_path,
                                font_type=os.path.splitext(file)[1].lower(),
                                size=os.path.getsize(font_path)
                            )
                            fonts.append(font_info)
        
        return sorted(fonts, key=lambda x: x.name)
    
    def read_font_info(self, font_path: str) -> FontInfo:
        """读取字体文件信息
        
        Args:
            font_path: 字体文件路径
            
        Returns:
            字体详细信息
        """
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"字体文件不存在: {font_path}")
        
        if not font_path.lower().endswith(('.ttf', '.otf')):
            raise ValueError("不支持的字体格式，仅支持TTF和OTF")
        
        try:
            # 尝试使用fontTools读取字体信息
            from fontTools.ttLib import TTFont
            font = TTFont(font_path)
            
            # 获取字体名称表
            name_table = font['name']
            font_names = {}
            
            for record in name_table.names:
                if record.nameID in [1, 2, 4, 6]:  # 字体族名、样式、全名、PostScript名
                    try:
                        name = record.toUnicodeString()
                        font_names[record.nameID] = name
                    except:
                        continue
            
            return FontInfo(
                name=os.path.splitext(os.path.basename(font_path))[0],
                path=font_path,
                font_type=os.path.splitext(font_path)[1].lower(),
                size=os.path.getsize(font_path),
                family_name=font_names.get(1, 'Unknown'),
                style_name=font_names.get(2, 'Regular'),
                full_name=font_names.get(4, 'Unknown'),
                postscript_name=font_names.get(6, 'Unknown'),
                glyph_count=font.getGlyphSet().keys().__len__()
            )
            
        except ImportError:
            # 如果没有fontTools，返回基本信息
            return FontInfo(
                name=os.path.splitext(os.path.basename(font_path))[0],
                path=font_path,
                font_type=os.path.splitext(font_path)[1].lower(),
                size=os.path.getsize(font_path),
                family_name=os.path.splitext(os.path.basename(font_path))[0],
                style_name='Unknown',
                full_name=os.path.splitext(os.path.basename(font_path))[0],
                postscript_name='Unknown',
                glyph_count=0
            )
    
    def install_font(self, font_path: str, user_install: bool = True) -> bool:
        """安装字体文件
        
        Args:
            font_path: 字体文件路径
            user_install: 是否安装到用户目录
            
        Returns:
            安装是否成功
        """
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"字体文件不存在: {font_path}")
        
        if not font_path.lower().endswith(('.ttf', '.otf')):
            raise ValueError("不支持的字体格式，仅支持TTF和OTF")
        
        try:
            font_name = os.path.basename(font_path)
            
            if user_install:
                target_dirs = self.font_paths['user']
            else:
                target_dirs = self.font_paths['system']
            
            # 选择第一个可用的目标目录
            target_dir = None
            for dir_path in target_dirs:
                if user_install or os.access(os.path.dirname(dir_path), os.W_OK):
                    target_dir = dir_path
                    break
            
            if not target_dir:
                raise PermissionError("没有权限安装字体")
            
            # 确保目标目录存在
            os.makedirs(target_dir, exist_ok=True)
            
            target_path = os.path.join(target_dir, font_name)
            
            # 复制字体文件
            shutil.copy2(font_path, target_path)
            
            # 系统特定的安装步骤
            if self.system == 'windows':
                self._windows_register_font(target_path, user_install)
            elif self.system == 'linux':
                self._linux_refresh_font_cache()
            elif self.system == 'darwin':
                # macOS通常不需要额外步骤
                pass
            
            return True
            
        except Exception as e:
            print(f"安装字体失败: {e}")
            return False
    
    def uninstall_font(self, font_name: str, user_only: bool = True) -> bool:
        """卸载字体
        
        Args:
            font_name: 字体名称（文件名）
            user_only: 是否只从用户目录卸载
            
        Returns:
            卸载是否成功
        """
        try:
            paths_to_check = []
            
            if user_only:
                paths_to_check = self.font_paths['user']
            else:
                paths_to_check = self.font_paths['system'] + self.font_paths['user']
            
            removed = False
            
            for font_dir in paths_to_check:
                if os.path.exists(font_dir):
                    for file in os.listdir(font_dir):
                        if file.lower() == font_name.lower() or \
                           os.path.splitext(file)[0].lower() == font_name.lower():
                            font_path = os.path.join(font_dir, file)
                            try:
                                # Windows需要先取消注册
                                if self.system == 'windows':
                                    self._windows_unregister_font(font_path, font_dir in self.font_paths['user'])
                                
                                os.remove(font_path)
                                removed = True
                                print(f"已删除字体: {font_path}")
                                
                            except PermissionError:
                                print(f"权限不足，无法删除: {font_path}")
                            except Exception as e:
                                print(f"删除字体失败 {font_path}: {e}")
            
            if removed and self.system == 'linux':
                self._linux_refresh_font_cache()
            
            return removed
            
        except Exception as e:
            print(f"卸载字体失败: {e}")
            return False
    
    def _windows_register_font(self, font_path: str, user_install: bool):
        """Windows字体注册"""
        try:
            import winreg
            
            # 读取字体名称
            font_info = self.read_font_info(font_path)
            font_name = font_info.full_name
            font_file = os.path.basename(font_path)
            
            if user_install:
                # 用户字体注册
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
                registry_key = winreg.HKEY_CURRENT_USER
            else:
                # 系统字体注册
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
                registry_key = winreg.HKEY_LOCAL_MACHINE
            
            with winreg.OpenKey(registry_key, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, f"{font_name} (TrueType)", 0, winreg.REG_SZ, font_file)
                
        except Exception as e:
            print(f"Windows字体注册失败: {e}")
    
    def _windows_unregister_font(self, font_path: str, user_install: bool):
        """Windows字体取消注册"""
        try:
            import winreg
            
            font_info = self.read_font_info(font_path)
            font_name = font_info.full_name
            
            if user_install:
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
                registry_key = winreg.HKEY_CURRENT_USER
            else:
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
                registry_key = winreg.HKEY_LOCAL_MACHINE
            
            with winreg.OpenKey(registry_key, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, f"{font_name} (TrueType)")
                
        except Exception as e:
            print(f"Windows字体取消注册失败: {e}")
    
    def _linux_refresh_font_cache(self):
        """Linux刷新字体缓存"""
        try:
            subprocess.run(['fc-cache', '-f'], check=False, capture_output=True)
        except Exception as e:
            print(f"刷新Linux字体缓存失败: {e}")
    
    def get_system_info(self) -> Dict[str, any]:
        """获取系统字体信息"""
        return {
            'system': self.system,
            'font_paths': self.font_paths,
            'total_fonts': len(self.list_installed_fonts()),
            'user_fonts': len(self.list_installed_fonts(user_only=True))
        }


# 使用示例
if __name__ == "__main__":
    font_manager = FontManager()
    
    # 获取系统信息
    print("系统信息:")
    system_info = font_manager.get_system_info()
    for key, value in system_info.items():
        print(f"  {key}: {value}")
    
    # 列举字体
    print(f"\n已安装字体数量: {len(font_manager.list_installed_fonts())}")
    
    # 显示前5个字体
    fonts = font_manager.list_installed_fonts()[:5]
    print("\n前5个字体:")
    for font in fonts:
        print(f"  {font.name} ({font.type}) - {font.size} bytes")
        # 如果需要更详细信息
        detailed_info = font_manager.read_font_info(font.path)
        print(f"    族名: {detailed_info.family_name}, 样式: {detailed_info.style_name}")
