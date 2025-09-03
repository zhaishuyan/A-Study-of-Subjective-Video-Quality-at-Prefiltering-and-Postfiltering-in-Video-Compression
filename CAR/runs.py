import os

cmd0 = 'python run_upsample.py --img_dir /data5/shuyanz/BVI_SR_processed/combination97_median_frames/ --scale 2 --output_dir output_97'
cmd1 = 'python run_upsample.py --img_dir /data5/shuyanz/BVI_SR_processed/combination98_median_frames/ --scale 2 --output_dir output_98'
cmd2 = 'python run_upsample.py --img_dir /data5/shuyanz/BVI_SR_processed/combination99_median_frames/ --scale 2 --output_dir output_99'
cmd3 = 'python run_upsample.py --img_dir /data5/shuyanz/BVI_SR_processed/combination100_median_frames/ --scale 2 --output_dir output_100'
cmd4 = 'python run_upsample.py --img_dir /data5/shuyanz/BVI_SR_processed/combination101_median_frames/ --scale 4 --output_dir output_101'
cmd5 = 'python run_upsample.py --img_dir /data5/shuyanz/BVI_SR_processed/combination102_median_frames/ --scale 4 --output_dir output_102'
cmd6 = 'python run_upsample.py --img_dir /data5/shuyanz/BVI_SR_processed/combination103_median_frames/ --scale 4 --output_dir output_103'
cmd7 = 'python run_upsample.py --img_dir /data5/shuyanz/BVI_SR_processed/combination104_median_frames/ --scale 4 --output_dir output_104'


cmds = [cmd0, cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7]


for cmd in cmds:
    os.system(cmd)
    print(f"Executed command: {cmd}")