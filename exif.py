import argparse
import yaml
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import exifread
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
from concurrent.futures import ThreadPoolExecutor

# 定义默认配置
DEFAULT_CONFIG = {
    'font': {
        'brand_font_path': 'fonts/MiSans-Bold.ttf',
        'model_font_path': 'fonts/AnotherFont.ttf',
        'lens_font_path': 'fonts/MiSans-Regular.ttf',
        'normal_size': 100,
        'small_size': 50
    },
    'image': {
        'box_height': 150,
        'logo_size': {
            'width': 364,
            'height': 200
        },
        'canon_logo_size': {
            'width': 182,
            'height': 100
        },
        'border_width': 10
    },
    'width_threshold': 1800
}

# 从 YAML 文件加载配置，若文件不存在则返回默认配置
def load_config(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
    else:
        print(f"INFO: 配置文件 {filename} 不存在，使用默认设置。")
        config = DEFAULT_CONFIG
    return config

def export_exif_info(tags):
    print("EXIF信息：")
    for tag in tags.keys():
        print(f"{tag}: {tags[tag]}")

def add_exif_watermark(input_image_path, output_image_path, force_add_watermark, debug, config, use_gpu, lens_model_param):
    print(f"正在读取文件: {input_image_path}")  # 打印文件路径
    image = cv2.imread(input_image_path)

    if image is None:
        print(f"ERR: 无法读取图像文件 {input_image_path}")
        return  # 读取失败，提前返回

    # 将三通道图像转换为四通道，即添加一个 alpha 通道
    image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)

    # 读取EXIF数据
    with open(input_image_path, 'rb') as f:
        tags = exifread.process_file(f)

    if debug:
        export_exif_info(tags)

    # 提取相机和镜头信息
    image_make = str(tags.get('Image Make', 'N/A'))
    image_model = str(tags.get('Image Model', 'N/A'))
    lens_model = str(tags.get('Image LensModel', 'N/A')) if 'Image LensModel' in tags else 'N/A'
    iso = str(tags.get('EXIF ISOSpeedRatings', 'N/A'))
    aperture = str(tags.get('EXIF FNumber', 'N/A'))
    shutter_speed = str(tags.get('EXIF ExposureTime', 'N/A'))
    
    # 打印EXIF镜头型号
    print(f"从EXIF获取的镜头型号: {lens_model}")  # 调试输出

    # 当 lens_model 为 'N/A' 且 lens_model_param 不为空，使用 lens_model_param
    if lens_model == 'N/A' and lens_model_param:
        lens_model = lens_model_param
        print(f"使用传入的镜头型号: {lens_model}")  # 调试输出

    # 如果 lens_model 还是 'N/A'，提示用户输入
    if lens_model == 'N/A':
        lens_model = input("无法从EXIF获取镜头型号，请手动输入镜头型号（或ID）：")

    print("品牌:", image_make)
    print("型号:", image_model)
    print("镜头型号:", lens_model)

    # 生成水印的其他步骤...
    box_height = config['image']['box_height']
    border_width = config['image']['border_width']

    # 创建新图像
    new_image_height = image.shape[0] + box_height + 2 * border_width  # 图像高度 + 水印高度 + 边框高度
    new_image_width = image.shape[1] + 2 * border_width  # 图像宽度 + 边框宽度
    new_image = np.ones((new_image_height, new_image_width, 4), dtype=np.uint8) * 255  # 创建白色背景图像

    # 将原图像放入新图像中
    new_image[border_width:border_width + image_rgba.shape[0], border_width:border_width + image_rgba.shape[1]] = image_rgba


    # Pillow处理文字
    pil_image = Image.fromarray(new_image)
    draw = ImageDraw.Draw(pil_image)

    # 创建字体（保持逻辑不变）
    brand_font = ImageFont.truetype(config['font']['brand_font_path'], config['font']['normal_size'])
    model_font = ImageFont.truetype(config['font']['model_font_path'], config['font']['normal_size'])
    lens_font = ImageFont.truetype(config['font']['lens_font_path'], config['font']['normal_size'])

    # 绘制品牌水印文本
    text_y_brand = image.shape[0] + border_width + 10
    draw.text((315, text_y_brand), image_make, font=brand_font, fill=(0, 0, 0))

    # 绘制型号水印文本
    text_y_model = text_y_brand + (config['font']['normal_size'] + 10)
    draw.text((315, text_y_model), image_model, font=model_font, fill=(0, 0, 0))

    # 计算拍摄信息
    lens_text_y = text_y_model + 0
    lens_text_x = new_image.shape[1] - 315
    lens_info_y = text_y_model - 115
    lens_info = f"|ISO{iso}|F{aperture}|{shutter_speed}|"  
    draw.text((lens_text_x, lens_info_y), lens_info, font=lens_font, fill=(0, 0, 0), anchor="ra")  
    draw.text((lens_text_x, lens_text_y), lens_model, font=lens_font, fill=(0, 0, 0), anchor="ra")  

    # 读取并绘制图标
    logo_path = 'img/Nikon.png' if "NIKON" in image_make.upper() else 'img/CANON.png'  # 根据品牌选择图标路径
    logo = Image.open(logo_path).convert("RGBA")
    logo_size = config['image']['logo_size']
    logo = logo.resize((logo_size['width'], logo_size['height']), Image.LANCZOS)

    # 计算图标绘制位置
    logo_position = (10, text_y_model - logo.height + 100)  # 将图标底部与型号文本对齐，并有一点间距
    pil_image.paste(logo, logo_position, logo)

    # 保存最终图像
    pil_image.save(output_image_path, "PNG")

def select_images():
    Tk().withdraw()  # 隐藏主窗口
    file_paths = askopenfilenames(title="选择图片", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    return file_paths

def process_image(input_image, output_image_path, force_add_watermark, debug, config, use_gpu, lens_model_param):
    add_exif_watermark(input_image, output_image_path, force_add_watermark, debug, config, use_gpu, lens_model_param)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add EXIF watermark to an image.')
    parser.add_argument('input_image', nargs='?', help='Input image path (optional if using --all)')
    parser.add_argument('output_image', nargs='?', help='Output image path (optional if using --all)')
    parser.add_argument('--lens_model', nargs='?', default='', help='Lens model parameter (optional)')
    parser.add_argument('--nosmalladd', action='store_true', help='Force add watermark even if the image is small')
    parser.add_argument('--all', action='store_true', help='Process all selected images')
    parser.add_argument('--debug', action='store_true', help='Export all EXIF information to console')
    parser.add_argument('--nogpu', action='store_true', help='Disable GPU rendering')

    args = parser.parse_args()
    config = load_config('photoexifset.yaml')

    use_gpu = not args.nogpu  # 使用GPU与否

    if args.all:
        os.makedirs('out', exist_ok=True)
        input_images = select_images()
        
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_image, input_image, os.path.join('out', os.path.basename(input_image)), args.nosmalladd, args.debug, config, use_gpu, args.lens_model or '')
                for input_image in input_images
            ]
            # 可以在此处添加对 futures 的监视和处理
    else:
        if args.input_image and args.output_image:
            add_exif_watermark(args.input_image, args.output_image, args.nosmalladd, args.debug, config, use_gpu, args.lens_model)
        else:
            print("ERR：请提供输入和输出的图片路径。")
