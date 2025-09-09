#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旋转框(OBB)到水平框(HBB)转换工具
将旋转框标注转换为水平框标注，并生成可视化结果
"""

import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
import numpy as np
import cv2

# ==================== 配置区域 ====================
# 输入路径配置
IMAGE_DIR = r'7_Road'                    # 原始图像文件夹
XML_DIR = r'7_Road_Obb_label'               # 原始旋转框XML文件夹

# 输出路径配置  
OUTPUT_XML_DIR = r'7_Road_Hbb_label'    # 转换后的水平框XML文件夹
OUTPUT_VIS_DIR = r'Visualization'       # 可视化结果文件夹

# ==================== 参数配置 ====================
# 【重要】调整这个值，使得绿色框尽可能接近目标前景，但不过度裁掉前景
MAX_SHRINK_RATIO = 0.17

# 可视化配置 (BGR格式)
COLOR_ORIGINAL_BOX = (255, 100, 0)      # 蓝色 - 原始旋转框
COLOR_CONVERTED_BOX = (0, 255, 0)       # 绿色 - 转换后水平框
BOX_THICKNESS = 2


# ====================================================

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("旋转框(OBB)到水平框(HBB)转换工具")
    print("=" * 60)

def ensure_directories():
    """确保输出目录存在"""
    os.makedirs(OUTPUT_XML_DIR, exist_ok=True)
    os.makedirs(OUTPUT_VIS_DIR, exist_ok=True)
    print(f"输出目录已准备：")
    print(f"  - XML输出: {OUTPUT_XML_DIR}")
    print(f"  - 可视化输出: {OUTPUT_VIS_DIR}")

def check_paths():
    """检查必要的路径是否存在"""
    print("检查输入路径...")
    
    if not os.path.exists(IMAGE_DIR):
        print(f"❌ 图像目录不存在: {IMAGE_DIR}")
        return False
    else:
        image_count = len([f for f in os.listdir(IMAGE_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))])
        print(f"✅ 图像目录存在，包含 {image_count} 个图像文件")
    
    if not os.path.exists(XML_DIR):
        print(f"❌ XML目录不存在: {XML_DIR}")
        return False
    else:
        xml_count = len([f for f in os.listdir(XML_DIR) if f.endswith('.xml')])
        print(f"✅ XML目录存在，包含 {xml_count} 个XML文件")
    
    return True

def convert_robndbox_to_corners(cx, cy, w_rot, h_rot, angle_rad):
    """将旋转框参数转换为四个角点坐标"""
    corners = np.array([
        [-w_rot / 2, -h_rot / 2],  # 左上
        [w_rot / 2, -h_rot / 2],   # 右上
        [w_rot / 2, h_rot / 2],    # 右下
        [-w_rot / 2, h_rot / 2]    # 左下
    ])
    
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad), np.cos(angle_rad)]
    ])
    
    rotated_corners = corners.dot(rotation_matrix.T) + np.array([cx, cy])
    return rotated_corners

def calculate_heuristic_shrink_bbox(corners, angle_rad):
    """计算启发式收缩的水平边界框"""
    x_min_enclosing, y_min_enclosing = np.min(corners, axis=0)
    x_max_enclosing, y_max_enclosing = np.max(corners, axis=0)
    
    width_enclosing = x_max_enclosing - x_min_enclosing
    height_enclosing = y_max_enclosing - y_min_enclosing
    
    # 根据旋转角度计算收缩因子
    shrink_factor = MAX_SHRINK_RATIO * abs(np.sin(2 * angle_rad))
    
    total_shrink_x = width_enclosing * shrink_factor
    total_shrink_y = height_enclosing * shrink_factor
    
    x_min_tight = x_min_enclosing + total_shrink_x / 2
    x_max_tight = x_max_enclosing - total_shrink_x / 2
    y_min_tight = y_min_enclosing + total_shrink_y / 2
    y_max_tight = y_max_enclosing - total_shrink_y / 2
    
    return int(x_min_tight), int(y_min_tight), int(x_max_tight), int(y_max_tight)

def parse_robndbox(robndbox_element):
    """解析robndbox元素，返回参数"""
    try:
        cx = float(robndbox_element.find('cx').text)
        cy = float(robndbox_element.find('cy').text)
        w = float(robndbox_element.find('w').text)
        h = float(robndbox_element.find('h').text)
        angle = float(robndbox_element.find('angle').text)
        return cx, cy, w, h, angle
    except (AttributeError, TypeError, ValueError):
        return None

def create_bndbox_element(parent, xmin, ymin, xmax, ymax):
    """创建标准PASCAL VOC格式的bndbox元素"""
    bndbox = ET.SubElement(parent, 'bndbox')
    ET.SubElement(bndbox, 'xmin').text = str(xmin)
    ET.SubElement(bndbox, 'ymin').text = str(ymin)
    ET.SubElement(bndbox, 'xmax').text = str(xmax)
    ET.SubElement(bndbox, 'ymax').text = str(ymax)
    return bndbox



def process_single_xml_file(xml_filename):
    """处理单个XML文件"""
    input_xml_path = os.path.join(XML_DIR, xml_filename)
    output_xml_path = os.path.join(OUTPUT_XML_DIR, xml_filename)
    
    try:
        # 解析XML文件
        tree = ET.parse(input_xml_path)
        root = tree.getroot()
        
        # 获取图片路径
        path_element = root.find('path')
        if path_element is None or path_element.text is None:
            print(f"[错误] XML文件 {xml_filename} 中缺少 <path> 标签，已跳过")
            return None, None
        
        image_basename = os.path.basename(path_element.text)
        
        # 存储转换信息用于可视化
        conversion_info = []
        converted_objects = 0
        
        # 更新folder和path信息
        folder_element = root.find('folder')
        if folder_element is not None:
            folder_element.text = 'test'
        
        path_element = root.find('path')
        if path_element is not None:
            # 更新路径为test文件夹
            original_path = path_element.text
            if original_path:
                filename = os.path.basename(original_path)
                new_path = f"C:\\Users\\18755\\Desktop\\test\\{filename}"
                path_element.text = new_path
        
        # 处理每个object
        for obj in root.findall('object'):
            robndbox = obj.find('robndbox')
            type_element = obj.find('type')
            
            if robndbox is not None:
                # 解析旋转框参数
                params = parse_robndbox(robndbox)
                if params is None:
                    print(f"  [警告] 在 {xml_filename} 中发现无效的 robndbox，已跳过")
                    continue
                
                cx, cy, w_rot, h_rot, angle_rad = params
                
                # 计算旋转框的四个角点
                corners = convert_robndbox_to_corners(cx, cy, w_rot, h_rot, angle_rad)
                
                # 计算水平框
                xmin, ymin, xmax, ymax = calculate_heuristic_shrink_bbox(corners, angle_rad)
                
                # 存储转换信息
                conversion_info.append({
                    'original_corners': corners,
                    'horizontal_box': (xmin, ymin, xmax, ymax),
                    'center': (cx, cy),
                    'size': (w_rot, h_rot),
                    'angle': angle_rad
                })
                
                # 更新type元素
                if type_element is not None:
                    type_element.text = 'bndbox'
                
                # 移除原始的robndbox，添加新的bndbox
                obj.remove(robndbox)
                create_bndbox_element(obj, xmin, ymin, xmax, ymax)
                converted_objects += 1
        
        # 保存转换后的XML（带格式化）
        # 先转换为字符串
        xml_string = ET.tostring(root, encoding='unicode')
        
        # 使用minidom美化格式
        dom = xml.dom.minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent='  ', encoding=None)
        
        # 移除空行
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        formatted_xml = '\n'.join(lines)
        
        # 写入文件
        with open(output_xml_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            # 跳过第一行（XML声明）
            content_lines = formatted_xml.split('\n')[1:]
            f.write('\n'.join(content_lines))
        
        return image_basename, conversion_info
        
    except Exception as e:
        print(f"[错误] 处理 {xml_filename} 失败: {e}")
        return None, None

def create_visualization(image_basename, conversion_info, enable_vis=True):
    """创建可视化图像"""
    if not enable_vis or not conversion_info:
        return False
    
    try:
        # 加载图像
        image_path = os.path.join(IMAGE_DIR, image_basename)
        
        # 使用cv2.imdecode处理中文路径
        image_data = np.fromfile(image_path, dtype=np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        
        if image is None:
            print(f"  [警告] 无法加载图像: {image_basename}")
            return False
        
        # 绘制转换结果
        for info in conversion_info:
            # 绘制原始旋转框（蓝色）
            original_corners = info['original_corners'].astype(np.int32)
            cv2.polylines(image, [original_corners], True, COLOR_ORIGINAL_BOX, BOX_THICKNESS, cv2.LINE_AA)
            
            # 绘制转换后的水平框（绿色）
            xmin, ymin, xmax, ymax = info['horizontal_box']
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), COLOR_CONVERTED_BOX, BOX_THICKNESS)
        
        # 保存可视化结果
        output_vis_path = os.path.join(OUTPUT_VIS_DIR, f"vis_{image_basename}")
        
        # 使用cv2.imencode处理中文路径
        success, encoded_img = cv2.imencode('.png', image)
        if success:
            with open(output_vis_path, 'wb') as f:
                f.write(encoded_img.tobytes())
            return True
        else:
            return False
        
    except Exception as e:
        print(f"  [警告] 创建可视化失败 {image_basename}: {e}")
        return False

def run_conversion():
    """运行主转换程序"""
    print("\n" + "-" * 40)
    print("执行转换")
    print("-" * 40)
    
    print("开始全量转换处理，将为所有文件生成可视化图像...")
    print("- 蓝色框：原始旋转框标注")
    print("- 绿色框：转换后的水平框")
    print("-" * 40)
    
    # 获取所有XML文件
    try:
        xml_files = [f for f in os.listdir(XML_DIR) if f.endswith('.xml')]
    except Exception as e:
        print(f"[错误] 无法读取XML目录: {e}")
        return False
    
    if not xml_files:
        print(f"[错误] 在 {XML_DIR} 中未找到XML文件")
        return False
    
    print(f"找到 {len(xml_files)} 个XML文件")
    print("-" * 40)
    
    # 处理文件
    successful_conversions = 0
    total_objects_converted = 0
    visualization_count = 0
    
    for i, xml_file in enumerate(xml_files, 1):
        print(f"[{i}/{len(xml_files)}] 处理: {xml_file}")
        
        image_basename, conversion_info = process_single_xml_file(xml_file)
        
        if image_basename and conversion_info:
            successful_conversions += 1
            total_objects_converted += len(conversion_info)
            print(f"  -> 已转换: {len(conversion_info)} 个对象")
            
            # 创建可视化（总是启用）
            if create_visualization(image_basename, conversion_info, True):
                visualization_count += 1
                print(f"  -> 可视化已生成: vis_{image_basename}")
    
    print("\n" + "=" * 60)
    print("转换完成！")
    print(f"成功转换: {successful_conversions}/{len(xml_files)} 个XML文件")
    print(f"转换对象总数: {total_objects_converted}")
    print(f"生成可视化: {visualization_count} 个图像")
    print(f"输出位置:")
    print(f"  - XML文件: {OUTPUT_XML_DIR}")
    print(f"  - 可视化: {OUTPUT_VIS_DIR}")
    print("=" * 60)
    
    return successful_conversions > 0

def get_user_confirmation():
    """获取用户确认是否继续"""
    print(f"\n当前参数设置:")
    print(f"  - MAX_SHRINK_RATIO: {MAX_SHRINK_RATIO}")
    print(f"  - 图像目录: {IMAGE_DIR}")
    print(f"  - XML目录: {XML_DIR}")
    print(f"  - 输出XML目录: {OUTPUT_XML_DIR}")
    print(f"  - 输出可视化目录: {OUTPUT_VIS_DIR}")
    
    choice = input("\n是否继续执行转换? (y/n): ").lower().strip()
    return choice == 'y'

def main():
    """主程序"""
    print_banner()
    print("工作目录:", os.getcwd())
    print("输出目录: 7_Road_organized 文件夹")
    print("-" * 60)
    
    # 检查路径
    if not check_paths():
        print("\n❌ 路径检查失败，请确认文件路径配置正确")
        input("按回车键退出...")
        return
    
    # 确保输出目录存在
    ensure_directories()
    
    # 获取用户确认
    if not get_user_confirmation():
        print("已取消操作")
        input("按回车键退出...")
        return
    
    
    # 执行转换
    if run_conversion():
        print("\n" + "=" * 60)
        print("🎉 任务完成！")
        print("\n转换结果:")
        print("- 已生成所有文件的XML转换结果")
        print("- 已生成所有文件的可视化图像")
        print("- 蓝色框：原始旋转框标注")
        print("- 绿色框：转换后的水平框")
        print("\n下一步建议:")
        print("1. 检查 Visualization 文件夹中的可视化结果")
        print("2. 验证绿色框位置是否合适")
        print("3. 如需调整效果，可修改 MAX_SHRINK_RATIO 参数重新运行")
        print("\n输出文件结构:")
        print("7_Road_organized/")
        print("├── 7_Road_Obb_label/        # 转换后的XML文件")
        print("├── Visualization/            # 可视化结果（蓝框+绿框）")
        print("└── obb2hbb_converter.py      # 本转换工具")
        print("=" * 60)
    else:
        print("\n❌ 转换失败")
    
    input("\n按回车键退出...")

if __name__ == '__main__':
    main()