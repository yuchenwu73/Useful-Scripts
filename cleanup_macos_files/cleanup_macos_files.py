#!/usr/bin/env python3
"""
macOS系统文件清理工具
===================

功能：
- 清理 .DS_Store 文件（Finder目录设置文件）
- 清理 ._* 文件（资源分支文件）
- 递归扫描当前目录及所有子目录
- 提供清理前后的统计信息
- 安全的批量删除操作

使用方法：
    python3 cleanup_macos_files.py

作者：AI Assistant
日期：2025-09-15
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import argparse

def get_macos_files(root_dir):
    """
    扫描指定目录下的所有macOS系统文件
    
    Args:
        root_dir (Path): 根目录路径
        
    Returns:
        tuple: (ds_store_files, resource_fork_files)
    """
    ds_store_files = []
    resource_fork_files = []
    
    # 递归扫描所有文件
    for file_path in root_dir.rglob('*'):
        if file_path.is_file():
            filename = file_path.name
            
            # 检查.DS_Store文件
            if filename == '.DS_Store':
                ds_store_files.append(file_path)
            
            # 检查._开头的资源分支文件
            elif filename.startswith('._'):
                resource_fork_files.append(file_path)
    
    return ds_store_files, resource_fork_files

def get_file_sizes(file_list):
    """
    计算文件列表的总大小
    
    Args:
        file_list (list): 文件路径列表
        
    Returns:
        int: 总大小（字节）
    """
    total_size = 0
    for file_path in file_list:
        try:
            total_size += file_path.stat().st_size
        except (OSError, FileNotFoundError):
            # 文件可能已被删除或无法访问
            pass
    return total_size

def format_size(size_bytes):
    """
    格式化文件大小显示
    
    Args:
        size_bytes (int): 字节数
        
    Returns:
        str: 格式化的大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"

def print_banner(target_dir=None):
    """
    打印程序横幅
    
    Args:
        target_dir (Path, optional): 实际处理的目标目录
    """
    print("🍎 macOS系统文件清理工具")
    print("=" * 50)
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💼 当前工作目录: {Path.cwd()}")
    if target_dir and target_dir != Path.cwd():
        print(f"🎯 实际处理目录: {target_dir}")
    else:
        print(f"🎯 实际处理目录: {target_dir or Path.cwd()}")
    print()

def print_statistics(ds_store_files, resource_fork_files):
    """
    打印扫描统计信息
    
    Args:
        ds_store_files (list): .DS_Store文件列表
        resource_fork_files (list): 资源分支文件列表
    """
    print("📊 扫描结果统计")
    print("-" * 30)
    print(f"🗂️  .DS_Store 文件: {len(ds_store_files)} 个")
    print(f"📦 ._* 资源文件: {len(resource_fork_files)} 个")
    print(f"📈 总计文件数: {len(ds_store_files) + len(resource_fork_files)} 个")
    
    # 计算总大小
    ds_size = get_file_sizes(ds_store_files)
    fork_size = get_file_sizes(resource_fork_files)
    total_size = ds_size + fork_size
    
    print(f"💾 .DS_Store 大小: {format_size(ds_size)}")
    print(f"💾 ._* 文件大小: {format_size(fork_size)}")
    print(f"💾 总占用空间: {format_size(total_size)}")
    print()

def delete_files(file_list, file_type, base_dir=None):
    """
    删除文件列表中的所有文件
    
    Args:
        file_list (list): 要删除的文件路径列表
        file_type (str): 文件类型描述
        base_dir (Path, optional): 基准目录，用于显示相对路径
        
    Returns:
        tuple: (成功删除数量, 删除失败数量)
    """
    success_count = 0
    error_count = 0
    
    if not file_list:
        print(f"ℹ️  没有找到 {file_type} 文件，跳过删除")
        return 0, 0
    
    # 确定用于显示的基准目录
    if base_dir is None:
        base_dir = Path.cwd()
    
    print(f"🗑️  正在删除 {len(file_list)} 个 {file_type} 文件...")
    
    for file_path in file_list:
        try:
            file_path.unlink()  # 删除文件
            success_count += 1
            # 尝试显示相对于基准目录的路径
            try:
                display_path = file_path.relative_to(base_dir)
            except ValueError:
                # 如果无法计算相对路径，使用绝对路径
                display_path = file_path
            print(f"   ✅ {display_path}")
        except (OSError, FileNotFoundError) as e:
            error_count += 1
            try:
                display_path = file_path.relative_to(base_dir)
            except ValueError:
                display_path = file_path
            print(f"   ❌ {display_path} - 错误: {e}")
    
    print(f"📊 {file_type} 删除结果: 成功 {success_count} 个, 失败 {error_count} 个")
    print()
    
    return success_count, error_count

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='清理当前目录及子目录中的macOS系统文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
    python3 cleanup_macos_files.py              # 交互式清理
    python3 cleanup_macos_files.py --auto       # 自动清理，不询问
    python3 cleanup_macos_files.py --scan-only  # 仅扫描，不删除
        """
    )
    parser.add_argument('--auto', action='store_true', 
                      help='自动删除，不询问确认')
    parser.add_argument('--scan-only', action='store_true',
                      help='仅扫描文件，不执行删除操作')
    parser.add_argument('--target-dir', type=str, default='.',
                      help='指定要清理的目录路径（默认为当前目录）')
    
    args = parser.parse_args()
    
    # 设置目标目录
    target_dir = Path(args.target_dir).resolve()
    if not target_dir.exists():
        print(f"❌ 错误: 目录 {target_dir} 不存在")
        sys.exit(1)
    
    # 打印横幅（包含目标目录信息）
    print_banner(target_dir)
    
    # 扫描macOS系统文件
    print("🔍 正在扫描macOS系统文件...")
    ds_store_files, resource_fork_files = get_macos_files(target_dir)
    
    # 显示统计信息
    print_statistics(ds_store_files, resource_fork_files)
    
    # 检查是否有文件需要清理
    total_files = len(ds_store_files) + len(resource_fork_files)
    if total_files == 0:
        print("✨ 恭喜！没有找到任何macOS系统文件，目录已经很干净了！")
        return
    
    # 如果只是扫描模式，直接返回
    if args.scan_only:
        print("📋 扫描完成（仅扫描模式，未执行删除操作）")
        return
    
    # 询问用户确认（除非是自动模式）
    if not args.auto:
        print("⚠️  即将删除上述所有macOS系统文件")
        confirm = input("是否继续? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            print("❌ 操作已取消")
            return
        print()
    
    # 执行删除操作
    print("🧹 开始清理操作...")
    print("-" * 30)
    
    ds_success, ds_error = delete_files(ds_store_files, '.DS_Store', target_dir)
    fork_success, fork_error = delete_files(resource_fork_files, '._* 资源文件', target_dir)
    
    # 总结报告
    total_success = ds_success + fork_success
    total_error = ds_error + fork_error
    
    print("🎉 清理操作完成")
    print("=" * 30)
    print(f"✅ 成功删除: {total_success} 个文件")
    if total_error > 0:
        print(f"❌ 删除失败: {total_error} 个文件")
        print("💡 建议检查文件权限或是否被其他程序占用")
    else:
        print("🎊 所有文件删除成功！")
    
    print(f"💾 释放空间: ~{format_size(get_file_sizes(ds_store_files + resource_fork_files))}")
    print("🚀 目录现在完全干净，没有macOS系统文件！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 发生意外错误: {e}")
        sys.exit(1)
