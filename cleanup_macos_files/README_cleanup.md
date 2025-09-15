# macOS系统文件清理工具 🍎

## 功能介绍

`cleanup_macos_files.py` 是一个专门清理macOS系统生成的多余文件的Python脚本，可以递归清理当前目录及所有子目录中的macOS系统文件。

### 清理的文件类型

- **`.DS_Store` 文件**：Finder目录设置文件，存储文件夹的显示选项
- **`._*` 文件**：资源分支文件，包含文件的元数据和扩展属性

## 使用方法

### 1. 基本用法

```bash
# 交互式清理（推荐）
python3 cleanup_macos_files.py

# 自动清理，不询问确认
python3 cleanup_macos_files.py --auto

# 仅扫描，不删除文件
python3 cleanup_macos_files.py --scan-only

# 清理指定目录
python3 cleanup_macos_files.py --target-dir /path/to/directory
```

### 2. 参数说明

| 参数 | 描述 |
|------|------|
| `--auto` | 自动删除模式，不询问用户确认 |
| `--scan-only` | 仅扫描文件，不执行删除操作 |
| `--target-dir` | 指定要清理的目录路径（默认为当前目录） |
| `--help` | 显示帮助信息 |

### 3. 使用示例

```bash
# 扫描当前目录
python3 cleanup_macos_files.py --scan-only

# 清理整个项目目录（交互式）
python3 cleanup_macos_files.py

# 自动清理指定目录
python3 cleanup_macos_files.py --auto --target-dir /data/my_project

# 批量清理脚本中使用
python3 cleanup_macos_files.py --auto >/dev/null 2>&1
```

## 输出信息说明

### 路径显示说明

脚本会清楚显示两个重要路径：
- **💼 当前工作目录**：执行脚本时的工作目录
- **🎯 实际处理目录**：脚本实际扫描和清理的目录

这样您可以确认脚本正在处理正确的目录！

### 扫描结果示例
```
🍎 macOS系统文件清理工具
==================================================
⏰ 执行时间: 2025-09-15 18:19:19
💼 当前工作目录: /data4/wuyuchen/labeling_information_synthesis
🎯 实际处理目录: /data4/wuyuchen/labeling_information_synthesis

📊 扫描结果统计
------------------------------
🗂️  .DS_Store 文件: 3 个
📦 ._* 资源文件: 4,111 个
📈 总计文件数: 4,114 个
💾 .DS_Store 大小: 218.0 KB
💾 ._* 文件大小: 16.1 MB
💾 总占用空间: 16.3 MB
```

### 清理结果示例
```
🎉 清理操作完成
==============================
✅ 成功删除: 4,114 个文件
🎊 所有文件删除成功！
💾 释放空间: ~16.3 MB
🚀 目录现在完全干净，没有macOS系统文件！
```

## 安全特性

- ✅ **安全删除**：只删除特定的macOS系统文件
- ✅ **批量处理**：支持递归处理所有子目录
- ✅ **详细统计**：提供删除前后的详细信息
- ✅ **错误处理**：优雅处理权限和访问错误
- ✅ **确认机制**：默认需要用户确认才执行删除

## 适用场景

1. **开发环境清理**：清理代码仓库中的macOS系统文件
2. **数据传输准备**：在向非macOS系统传输文件前清理
3. **存储空间优化**：释放被系统文件占用的存储空间
4. **自动化脚本**：集成到CI/CD流程中自动清理

## 注意事项

⚠️ **重要提醒**：
- 该脚本会永久删除macOS系统文件，删除后无法恢复
- 建议在重要项目中先使用 `--scan-only` 模式查看扫描结果
- 确保有足够的文件权限执行删除操作
- 如果文件被其他程序占用，可能删除失败

## 维护信息

- **创建时间**：2025-09-15
- **版本**：1.0
- **兼容性**：Python 3.6+
- **测试状态**：已在 `/data4/wuyuchen/labeling_information_synthesis` 项目中验证

---

💡 **小贴士**：建议将此脚本加入您的项目维护工具集，定期清理macOS系统文件，保持项目目录整洁！
