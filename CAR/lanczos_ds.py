import os
from fileinput import filename

from PIL import Image
from glob import glob


def downsample_with_lanczos(input_path, output_path, target_width, target_height):
    # 打开BMP图像
    with Image.open(input_path) as img:
        # 确保是RGB模式（Lanczos处理彩色图像）
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 使用Lanczos重采样进行下采样
        resized_img = img.resize(
            (target_width, target_height),
            resample=Image.Resampling.LANCZOS  # 或Image.LANCZOS (旧版本)
        )

        # 保存结果
        resized_img.save(output_path)


# 使用示例
if __name__ == "__main__":
    input_dir = '/data0/shuyanz/BVI_SR/frames_orig_4k_30fps_8bit/'
    output_dir = 'img_2560/'

    for img in glob(os.path.join(input_dir,'**', '*.bmp')):
        filename = os.path.basename(img)
        dir = img.split('/')[-2]
        input_image = img
        output_image = os.path.join(output_dir, dir, filename)

        # 确保输出目录存在
        os.makedirs(os.path.split(output_image)[0], exist_ok=True)

        # 设置目标分辨率
        target_width = 2560
        target_height = 1440

        # 调用下采样函数
        downsample_with_lanczos(input_image, output_image, target_width, target_height)
