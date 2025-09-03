import os

# 对于每组pipeline，第2-3和第6-7的分辨率分别是1280x720和640x360，和3840x2160不是偶数倍。因此，需要先进行lancos upsampleing 1.5倍，再做deep upsampling 2x and 4x。

# 整体流程：
# 1. 对每组pipeline的第2-3和第6-7进行lanczos upsampling 1.5倍，得到640x360和960x540的图像。
# 2. 把所有视频yuv2rgb，得到median frames，以bmp的形式。 (1和2都用/data0/shuyanz/code/yuv2rgb.py处理)
# 3. 对每组bmp图像进行swinir处理，得到3840x2160的图像。
# 4. 对所有视频进行rgb2yuv，得到yuv格式的视频。


# command 2-3 6-7
# postfilering 33-40
cmd1 = 'python main_test_swinir.py --task real_sr --scale 2 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x2_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/pipeline34_median_frames/'
cmd2 = 'python main_test_swinir.py --task real_sr --scale 2 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x2_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/pipeline35_median_frames/'
cmd3 = 'python main_test_swinir.py --task real_sr --scale 2 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x2_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/pipeline36_median_frames/'
cmd4 = 'python main_test_swinir.py --task real_sr --scale 4 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/pipeline37_median_frames/'
cmd5 = 'python main_test_swinir.py --task real_sr --scale 4 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/pipeline38_median_frames/'
cmd6 = 'python main_test_swinir.py --task real_sr --scale 4 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/pipeline39_median_frames/'
cmd7 = 'python main_test_swinir.py --task real_sr --scale 4 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/pipeline40_median_frames/'

# combination 73-80
ccmd0 = 'python main_test_swinir.py --task real_sr --scale 2 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x2_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/combination73_median_frames/'
ccmd1 = 'python main_test_swinir.py --task real_sr --scale 2 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x2_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/combination74_median_frames/'
ccmd2 = 'python main_test_swinir.py --task real_sr --scale 2 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x2_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/combination75_median_frames/'
ccmd3 = 'python main_test_swinir.py --task real_sr --scale 2 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x2_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/combination76_median_frames/'
ccmd4 = 'python main_test_swinir.py --task real_sr --scale 4 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/combination77_median_frames/'
ccmd5 = 'python main_test_swinir.py --task real_sr --scale 4 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/combination78_median_frames/'
ccmd6 = 'python main_test_swinir.py --task real_sr --scale 4 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/combination79_median_frames/'
ccmd7 = 'python main_test_swinir.py --task real_sr --scale 4 --model_path model_zoo/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth --folder_lq /data0/shuyanz/BVI_SR_processed/combination80_median_frames/'

# cmds = [ cmd2, cmd3, cmd4, cmd5, cmd6, cmd7]
# def run_commands(commands):
#     for cmd in commands:
#         print(f'Running command: {cmd}')
#         os.system(cmd)

cmds = [ccmd0, ccmd1, ccmd2, ccmd3, ccmd4, ccmd5, ccmd6, ccmd7]
cmds = [ccmd2, ccmd3, ccmd6, ccmd7]
# cmds = [ccmd0]
for cmd in cmds:
    print(f'Running command: {cmd}')
    os.system(cmd)

print('Done!')
