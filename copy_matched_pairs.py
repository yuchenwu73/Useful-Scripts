""" 
脚本功能：这个脚本用于按可配置项将数据集从源目录整理到目标目录：
先根据配置检查/创建图片与标签子目录，支持按列表复制额外“特殊文件”（如 `classes.txt`），
然后在标签目录收集所有`.xml`文件的基名，并遍历图片目录中`.png`文件，按同名基名一一匹配，
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
#    注意：源基础目录是图片和标签子文件夹的共同上级目录。
SOURCE_BASE_DIR = r"C:\Users\18755\Desktop\7_Road_organized"
DEST_BASE_DIR = r"C:\Users\18755\Desktop\7_Road_organized_test"

# 2. 定义包含图片和标签的子文件夹名称
IMAGE_SUBDIR = '7_Road'
LABEL_SUBDIR = '7_Road_label'

# 3. 定义需要额外复制的特殊文件列表
#    这是一个列表，您可以添加多个需要复制的文件。
#    根据您的要求，这里设置为空列表，表示不复制任何额外文件。
SPECIAL_FILES_TO_COPY = []

# --- 配置区结束 ---
# ==============================================================================


def process_and_copy_files_for_xml():
    """
    根据配置，查找匹配的图片和XML标签文件，并复制它们到一个新的目录中。
    同时，也会复制在配置中指定的任何特殊文件。
    """
    # 1. 根据配置构建完整的路径
    source_image_dir = os.path.join(SOURCE_BASE_DIR, IMAGE_SUBDIR)
    source_label_dir = os.path.join(SOURCE_BASE_DIR, LABEL_SUBDIR)

    dest_image_dir = os.path.join(DEST_BASE_DIR, IMAGE_SUBDIR)
    dest_label_dir = os.path.join(DEST_BASE_DIR, LABEL_SUBDIR)

    # 检查核心的源文件夹是否存在
    if not os.path.isdir(source_image_dir):
        print(f"错误：找不到源图片文件夹 '{source_image_dir}'。请检查路径是否正确。")
        return
    if not os.path.isdir(source_label_dir):
        print(f"错误：找不到源标签文件夹 '{source_label_dir}'。请检查路径是否正确。")
        return

    # 2. 创建目标文件夹
    os.makedirs(dest_image_dir, exist_ok=True)
    os.makedirs(dest_label_dir, exist_ok=True)
    print(f"已创建或确认目标文件夹: {dest_image_dir} 和 {dest_label_dir}")

    # 3. 复制配置中指定的特殊文件 (此部分逻辑不变)
    if SPECIAL_FILES_TO_COPY:
        print("\n--- 开始处理特殊文件 ---")
        for file_info in SPECIAL_FILES_TO_COPY:
            try:
                from_dir = os.path.join(SOURCE_BASE_DIR, file_info["from_folder"])
                to_dir = os.path.join(DEST_BASE_DIR, file_info["to_folder"])
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
    else:
        print("\n未配置特殊文件，跳过复制。")

    # 4. 获取标签文件的基本名
    try:
        label_files = os.listdir(source_label_dir)
        # ---【修改点 1】--- 将 .txt 修改为 .xml
        label_basenames = {os.path.splitext(f)[0] for f in label_files if f.endswith('.xml')}
        if not label_basenames:
            # ---【修改点 1.1】--- 更新提示信息
            print(f"警告: 在 {source_label_dir} 中未找到任何 .xml 标签文件。")
            return
        print(f"在 {source_label_dir} 中找到 {len(label_basenames)} 个 .xml 标签文件。")
    except FileNotFoundError:
        print(f"错误: 找不到源标签文件夹 {source_label_dir}")
        return
        
    # 5. 遍历图片，进行匹配和复制
    copied_count = 0
    try:
        image_files = os.listdir(source_image_dir)
        # 注意：这里仍然查找 .png 图片，如果您的图片格式不是 .png (例如 .jpg)，也需要相应修改
        png_image_files = [f for f in image_files if f.endswith('.png')]
        print(f"在 {source_image_dir} 中找到 {len(png_image_files)} 个 .png 图片文件。开始匹配...")
        
        if not png_image_files:
            print(f"警告: 在 {source_image_dir} 中未找到任何 .png 图片文件。")
        
        for image_file in png_image_files:
            image_basename = os.path.splitext(image_file)[0]
            if image_basename in label_basenames:
                source_image_path = os.path.join(source_image_dir, image_file)
                # ---【修改点 2】--- 将 .txt 修改为 .xml
                source_label_path = os.path.join(source_label_dir, image_basename + '.xml')
                
                if not os.path.exists(source_label_path):
                    print(f"  [警告] 图片 '{image_file}' 的同名标签文件不存在，已跳过。")
                    continue

                dest_image_path = os.path.join(dest_image_dir, image_file)
                # ---【修改点 3】--- 将 .txt 修改为 .xml
                dest_label_path = os.path.join(dest_label_dir, image_basename + '.xml')
                
                shutil.copy2(source_image_path, dest_image_path)
                shutil.copy2(source_label_path, dest_label_path)
                copied_count += 1
    except FileNotFoundError:
        print(f"错误: 找不到源图片文件夹 {source_image_dir}")
        return

    # 6. 输出最终结果
    print("\n--------------------")
    print("处理完成！")
    print(f"总共成功匹配并复制了 {copied_count} 对文件。")
    print(f"图片已存入: {os.path.abspath(dest_image_dir)}")
    print(f"标签已存入: {os.path.abspath(dest_label_dir)}")
    print("--------------------")

if __name__ == "__main__":
    # 调用修改后的新函数
    process_and_copy_files_for_xml()
