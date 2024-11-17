import argparse
import yaml
from PIL import Image, ImageDraw, ImageFont
import exifread
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

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

# 计算文本的宽度和高度
def get_text_size(draw, font, text):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return (width, height)

def export_exif_info(tags):
    print("EXIF信息：")
    for tag in tags.keys():
        print(f"{tag}: {tags[tag]}")

def add_exif_watermark(input_image_path, output_image_path, force_add_watermark, debug):
    # 加载配置
    config = load_config('photoexifset.yaml')

    image = Image.open(input_image_path).convert("RGBA")

    # 读取EXIF数据
    with open(input_image_path, 'rb') as f:
        tags = exifread.process_file(f)

    if debug:
        # 调试模式，导出所有EXIF信息
        export_exif_info(tags)

    # 获取并转换指定的EXIF信息为字符串
    image_make = str(tags.get('Image Make', 'N/A'))
    image_model = str(tags.get('Image Model', 'N/A'))
    lens_model = str(tags.get('Image LensModel', 'N/A'))
    lens_id = str(tags.get('Image LensModel', 'N/A'))

    # 获取 ISO、光圈和快门速度
    iso = str(tags.get('EXIF ISOSpeedRatings', 'N/A'))
    aperture = str(tags.get('EXIF FNumber', 'N/A'))
    shutter_speed = str(tags.get('EXIF ExposureTime', 'N/A'))

    # 如果镜头型号获取失败，则使用镜头ID
    if lens_model == 'N/A':
        lens_model = lens_id

    # 如果都没有获取到，提示用户输入
    if lens_model == 'N/A':
        lens_model = input("无法从EXIF获取镜头型号或ID，请手动输入镜头型号（或ID）：")

    print("品牌:", image_make)
    print("型号:", image_model)
    print("镜头型号:", lens_model)

    # 根据图像品牌选择相应的框高度
    box_height = config['image']['box_height']
    
    if "CANON" in image_make.upper():
        box_height = config['image']['canon_logo_size']['height'] + 10

    border_width = config['image']['border_width']

    if not force_add_watermark and image.width < config['width_threshold']:
        print("ERR：图片太小，水印添加被跳过。")
        return

    new_image = Image.new("RGBA", (image.width + 2 * border_width, image.height + box_height + 2 * border_width), (255, 255, 255, 255))
    
    draw = ImageDraw.Draw(new_image)

    draw.rectangle(
        [(border_width - 1, border_width - 1), 
         (new_image.width - border_width + 1, new_image.height - border_width + 1)],
        outline=(255, 255, 255, 255), 
        width=border_width
    )

    new_image.paste(image, (border_width, border_width))

    brand_font_size = config['font']['normal_size']
    model_font_size = config['font']['normal_size']
    lens_font_size = config['font']['normal_lens_ISOinfo_size']

    text_y_brand = image.height + border_width + 10  
    text_y_model = text_y_brand + (brand_font_size + 10)

    brand_font_path = config['font']['brand_font_path']
    brand_font = ImageFont.truetype(brand_font_path, brand_font_size)

    model_font_path = config['font']['model_font_path']
    model_font = ImageFont.truetype(model_font_path, model_font_size)

    lens_font_path = config['font']['lens_font_path']
    lens_font = ImageFont.truetype(lens_font_path, lens_font_size)

    # 绘制品牌水印文本
    draw.text((315, text_y_brand), image_make, font=brand_font, fill=(0, 0, 0))

    # 绘制型号水印文本
    draw.text((315, text_y_model), image_model, font=model_font, fill=(0, 0, 0))

    # 计算镜头型号的字段
    lens_text_y = text_y_model + 10  
    lens_text_x = new_image.width - 315  
    # 设定 ISO、光圈和快门速度信息的 Y 坐标（让这个往上移动）
    lens_info_y = text_y_model - 35 # 将此值向下调整，例如从10改为20
    lens_info = f"/ISO{iso}/F{aperture}/{shutter_speed}/"  # 添加ISO、光圈和快门速度信息
    draw.text((lens_text_x, lens_info_y), lens_info, font=lens_font, fill=(0, 0, 0), anchor="ra")  # 黑色文本，右对齐
 
    

    # 绘制镜头型号水印文本，靠右
    draw.text((lens_text_x, lens_text_y + 20), lens_model, font=lens_font, fill=(0, 0, 0), anchor="ra")  # 黑色文本，右对齐

    if "NIKON" in image_make.upper() or "CANON" in image_make.upper():
        logo_path = 'img/Nikon.png' if "NIKON" in image_make.upper() else 'img/CANON.png'
        logo = Image.open(logo_path).convert("RGBA")
        
        logo_size = (config['image']['logo_size']['width'], config['image']['logo_size']['height'])
        logo = logo.resize(logo_size, Image.LANCZOS)

        model_text_size = get_text_size(draw, model_font, image_model)
        model_text_height = model_text_size[1]

        logo_y = text_y_model - model_text_height  

        new_image.paste(logo, (10, logo_y), logo)

    new_image.save(output_image_path, "PNG")

# 新增选择图片的功能
def select_images():
    Tk().withdraw()  # 隐藏主窗口
    file_paths = askopenfilenames(title="选择图片", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    return file_paths

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add EXIF watermark to an image.')
    parser.add_argument('input_image', nargs='?', help='Input image path (optional if using --all)')
    parser.add_argument('output_image', nargs='?', help='Output image path (optional if using --all)')
    parser.add_argument('--nosmalladd', action='store_true', help='Force add watermark even if the image is small')
    parser.add_argument('--all', action='store_true', help='Process all selected images')
    parser.add_argument('--debug', action='store_true', help='Export all EXIF information to console')

    args = parser.parse_args()

    if args.all:
        # 创建输出目录
        os.makedirs('out', exist_ok=True)
        input_images = select_images()
        for input_image in input_images:
            output_image_path = os.path.join('out', os.path.basename(input_image))
            add_exif_watermark(input_image, output_image_path, args.nosmalladd, args.debug)
    else:
        if args.input_image and args.output_image:
            add_exif_watermark(args.input_image, args.output_image, args.nosmalladd, args.debug)
        else:
            print("ERR：请提供输入和输出的图片路径。")
