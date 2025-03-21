import os
from typing import List


def remove_empty_files(dir_path: str) -> List[str]:
    """
    删除指定目录下所有大小为0的空文件

    Args:
        dir_path: 要处理的目录路径

    Returns:
        删除的空文件列表
    """
    removed_files = []

    # 遍历目录
    for root, _, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            # 检查文件是否存在并且大小为0
            if os.path.isfile(file_path) and os.path.getsize(file_path) == 0:
                try:
                    os.remove(file_path)
                    removed_files.append(file_path)
                except OSError as e:
                    print(f"无法删除空文件 {file_path}: {e}")

    return removed_files


def remove_empty_dirs(dir_path: str) -> List[str]:
    """
    递归删除指定目录下所有空目录，包括删除文件后产生的新空目录

    Args:
        dir_path: 要处理的目录路径

    Returns:
        删除的空目录列表
    """
    removed_dirs = []

    # 持续扫描目录树，直到没有新的空目录被发现
    while True:
        found_empty = False

        # 使用自底向上的方式遍历目录树
        for root, dirs, files in os.walk(dir_path, topdown=False):
            # 跳过根目录
            if root == dir_path:
                continue

            # 检查当前目录是否为空目录
            if not files and not os.listdir(root):  # 确认目录真的是空的
                try:
                    os.rmdir(
                        root
                    )  # 使用os.rmdir代替shutil.rmtree，因为我们已确认目录为空
                    removed_dirs.append(root)
                    found_empty = True
                except OSError as e:
                    print(f"无法删除空目录 {root}: {e}")

        # 如果这次扫描没有发现新的空目录，说明已完成清理
        if not found_empty:
            break

    return removed_dirs


def cleanup_directory(dir_path: str) -> tuple:
    """
    清理目录：先删除空文件，再删除空目录

    Args:
        dir_path: 要清理的目录路径

    Returns:
        (deleted_files, deleted_dirs): 删除的文件和目录列表
    """
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"目录不存在: {dir_path}")

    # 先删除空文件
    deleted_files = remove_empty_files(dir_path)

    # 然后删除空目录
    deleted_dirs = remove_empty_dirs(dir_path)

    return deleted_files, deleted_dirs


if __name__ == "__main__":
    dir_path = r""
    deleted_files, deleted_dirs = cleanup_directory(dir_path)
    print(f"已删除 {len(deleted_files)} 个空文件")
    print(f"已删除 {len(deleted_dirs)} 个空目录")
