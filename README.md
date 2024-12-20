# NIKON-WATERMARK-GENERATOR
NIKON-WATERMARK-GENERATOR 是一款开源的水印生成器，可以帮助你快速生成相机的水印，并将其导入到相机中。是@cooollawf开发的的一部分，用于解决国内软件对很多人不友好的烦恼







### 从源码安装

从 [Github](https://github.com/cooollawf/Nikon-watermark-generator)下载ZIP包 


#### 环境

- Python 3.10+
- Windows/MacOS/Linux, x86/arm均可 (凡是python支持的环境都可以)


- Clone 并安装依赖

```bash
git clone https://github.com/cooollawf/Nikon-watermark-generator
cd Nikon-watermark-generator
## 安装依赖
pip install -r requirements.txt
## 运行
python exif.py
```

3. 如果你看到了 `ERR：请提供输入和输出的图片路径。` 的报错, 说明一切正常, 该设置附加参数了

### 设置参数

- `python exif.py 这块是你的图片(必须是jpg格式).jpg 这块是你要导出文件的名称（后缀jpg格式）.jpg`

- 然后你会看到一大堆的提示，正常只需要等待就可以了。

- 最后你会在你设置的目录下看到一个新的文件，这就是你生成的水印图片文件。

### 其他参数
- 处理一个较小的图像并强制添加水印：
- `python exif.py input_image.jpg output_image.png --nosmalladd`
- 处理多个图像并将结果保存到 out 文件夹：
- `python exif.py --all`
- 以调试模式运行以查看 EXIF 信息：
- `python exif.py input_image.jpg output_image.png --debug`
- 不使用GPU加速：
- `python exif.py input_image.jpg output_image.png --nogpu`


### GPU BOOST（only nvdia gpu）（可选）


根据您的操作系统和 CUDA 版本选择合适的命令进行安装。

1. **访问 [PyTorch 官网](https://pytorch.org/)**：根据您的系统、语言和包管理工具获取相应的安装命令。

2. **基本安装命令**：
   - 对于 **CPU** 版本（适用于所有平台）：
     ```bash
     pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
     ```

   - 对于 **带 GPU 支持的安装**（适用于使用 NVIDIA GPU 的用户）：
     - 如果您的机器上已安装 CUDA 11.3：
     ```bash
     pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113
     ```
     - 如果您的机器上已安装 CUDA 10.2：
     ```bash
     pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu102
     ```

3. **验证安装**：
   在 Python 环境中运行以下命令以验证 PyTorch 是否成功安装：
   ```python
   import torch
   print(torch.__version__)  # 查看安装的 PyTorch 版本

### 特别感谢
- Python 库 [Pillow](https://github.com/python-pillow/Pillow) 提供了图像处理的能力。
- bangbang93的[OpenBMCLAPI](https://github.com/bangbang93/OpenBMCLAPI)项目提供了README模板。(俗称抄的)
- Python库[exifread](https://github.com/ianare/exif-py)提供了读取EXIF信息的能力。