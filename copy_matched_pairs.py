""" 
脚本功能：这个脚本用于按可配置项将数据集从源目录整理到目标目录：
先根据配置检查/创建图片与标签子目录，支持按列表复制额外“特殊文件”（如 `classes.txt`），
然后在标签目录收集所有`.txt`文件的基名，并遍历图片目录中`.png`文件，按同名基名一一匹配，
匹配成功则将图片与对应标签成对复制到目标结构（用 `shutil.copy2` 保留元数据），
过程中输出进度与异常提示（含缺失文件/文件夹的错误与警告），最后汇总成功复制的对数及目标路径。
 """

import os
import shutil

# ==============================================================================
# --- 用户可修改配置区 ---
#
# 您可以在这里根据您的项目结构，轻松修改所有相关的文件夹和文件名。
# ------------------------------------------------------------------------------

# 1. 定义主要的源文件夹和目标文件夹名称
SOURCE_BASE_DIR = r"D:\1.电子科技大学MIG\Datasets\Plane\RQ-4 quanqiuying"
DEST_BASE_DIR = r"D:\1.电子科技大学MIG\Datasets\Plane\RQ-4_quanqiuying_final"

# 2. 定义包含图片和标签的子文件夹名称
IMAGE_SUBDIR = 'RQ-4_quanqiuying'
LABEL_SUBDIR = 'RQ-4_quanqiuying_label'

# 3. 定义需要额外复制的特殊文件列表
#    这是一个列表，您可以添加多个需要复制的文件。
#    每个文件都是一个字典，包含三个键:
#    - "from_folder": 文件所在的源子文件夹 (相对于 SOURCE_BASE_DIR)
#    - "filename":    要复制的文件名
#    - "to_folder":   文件要复制到的目标子文件夹 (相对于 DEST_BASE_DIR)
#
#    如果不需要复制任何额外文件，请将此列表设置为空: SPECIAL_FILES_TO_COPY = []
SPECIAL_FILES_TO_COPY = [
    {
        "from_folder": "RQ-4_quanqiuying_label", 
        "filename": "classes.txt", 
        "to_folder": "class"  
    }
]

# --- 配置区结束 ---
# ==============================================================================


def process_and_copy_files():
    """
    根据配置，查找匹配的图片和标签文件，并复制它们到一个新的目录中。
    同时，也会复制在配置中指定的任何特殊文件。
    """
    # 1. 根据配置构建完整的路径
    source_image_dir = os.path.join(SOURCE_BASE_DIR, IMAGE_SUBDIR)
    source_label_dir = os.path.join(SOURCE_BASE_DIR, LABEL_SUBDIR)

    dest_image_dir = os.path.join(DEST_BASE_DIR, IMAGE_SUBDIR)
    dest_label_dir = os.path.join(DEST_BASE_DIR, LABEL_SUBDIR)

    # 检查核心的源文件夹是否存在
    if not os.path.isdir(source_image_dir) or not os.path.isdir(source_label_dir):
        print(f"错误：请确保脚本与 '{SOURCE_BASE_DIR}' 文件夹在同一目录下，"
              f"且该文件夹内包含 '{IMAGE_SUBDIR}' 和 '{LABEL_SUBDIR}' 子文件夹。")
        return

    # 2. 创建目标文件夹
    os.makedirs(dest_image_dir, exist_ok=True)
    os.makedirs(dest_label_dir, exist_ok=True)
    print(f"已创建或确认目标文件夹: {dest_image_dir} 和 {dest_label_dir}")

    # 3. (新增) 复制配置中指定的特殊文件
    if SPECIAL_FILES_TO_COPY:
        print("\n--- 开始处理特殊文件 ---")
        for file_info in SPECIAL_FILES_TO_COPY:
            try:
                from_dir = os.path.join(SOURCE_BASE_DIR, file_info["from_folder"])
                to_dir = os.path.join(DEST_BASE_DIR, file_info["to_folder"])
                
                # 确保特殊文件的目标目录也存在
                os.makedirs(to_dir, exist_ok=True)
                
                source_path = os.path.join(from_dir, file_info["filename"])
                dest_path = os.path.join(to_dir, file_info["filename"])

                shutil.copy2(source_path, dest_path)
                print(f"  [成功] 已复制 '{source_path}' -> '{dest_path}'")
            except FileNotFoundError:
                print(f"  [警告] 未找到特殊文件 '{source_path}'，已跳过。")
            except Exception as e:
                print(f"  [错误] 复制文件 '{source_path}' 时发生错误: {e}")
        print("--- 特殊文件处理完毕 ---\n")

    # 4. 获取标签文件的基本名
    try:
        label_files = os.listdir(source_label_dir)
        label_basenames = {os.path.splitext(f)[0] for f in label_files if f.endswith('.txt')}
        print(f"在 {source_label_dir} 中找到 {len(label_basenames)} 个 .txt 标签文件。")
    except FileNotFoundError:
        print(f"错误: 找不到源文件夹 {source_label_dir}")
        return
        
    # 5. 遍历图片，进行匹配和复制
    copied_count = 0
    try:
        image_files = os.listdir(source_image_dir)
        print(f"在 {source_image_dir} 中找到 {len([f for f in image_files if f.endswith('.png')])} 个 .png 图片文件。开始匹配...")
        for image_file in image_files:
            if not image_file.endswith('.png'):
                continue
            image_basename = os.path.splitext(image_file)[0]
            if image_basename in label_basenames:
                source_image_path = os.path.join(source_image_dir, image_file)
                source_label_path = os.path.join(source_label_dir, image_basename + '.txt')
                dest_image_path = os.path.join(dest_image_dir, image_file)
                dest_label_path = os.path.join(dest_label_dir, image_basename + '.txt')
                shutil.copy2(source_image_path, dest_image_path)
                shutil.copy2(source_label_path, dest_label_path)
                copied_count += 1
    except FileNotFoundError:
        print(f"错误: 找不到源文件夹 {source_image_dir}")
        return

    # 6. 输出最终结果
    print("\n--------------------")
    print("处理完成！")
    print(f"总共成功匹配并复制了 {copied_count} 对文件。")
    print(f"图片已存入: {os.path.abspath(dest_image_dir)}")
    print(f"标签已存入: {os.path.abspath(dest_label_dir)}")
    print("--------------------")

if __name__ == "__main__":
    process_and_copy_files()