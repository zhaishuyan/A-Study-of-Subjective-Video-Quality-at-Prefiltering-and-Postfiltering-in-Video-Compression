import torch
import numpy as np
from collections import OrderedDict
from net_stdf import MFVQE
import utils
from tqdm import tqdm
import os

# from pathlib import Path


ckp_path = 'exp/Vimeo90K_R3_enlarge300x/ckp_300000.pt'  # trained at QP37, LDP, HM16.5

raw_yuv_dir = '/data0/shuyanz/BVI_SR/orig_4k_30fps_8bit'
# lq_yuv_dir = '/data0/shuyanz/BVI_SR_processed/postfiltering57_median'
# save_yuv_dir = '/data5/shuyanz/BVI_SR_processed/postfiltering65'
# os.makedirs(save_yuv_dir, exist_ok=True)
video_names = sorted(os.listdir(raw_yuv_dir))
raw_yuv_paths = [os.path.join(raw_yuv_dir, name) for name in video_names]
# lq_yuv_paths = [os.path.join(lq_yuv_dir, name.split('.')[0] + '_us.yuv') for name in video_names]
# save_yuv_paths = [os.path.join(save_yuv_dir, name) for name in video_names]

# raw_yuv_path = '/data0/shuyanz/BVI_SR/orig_4k_30fps_8bit/Boat_3840x2160_30fps_8bit_420.yuv'
# lq_yuv_path = '/data0/shuyanz/BVI_SR_processed/postfiltering57_median/Boat_3840x2160_30fps_8bit_420_us.yuv'
h, w, nfs = 2160, 3840, 150  # nfs: number of frames


def main():
    # ==========
    # Load pre-trained model
    # ==========
    opts_dict = {
        'radius': 3,
        'stdf': {
            'in_nc': 1,
            'out_nc': 64,
            'nf': 32,
            'nb': 3,
            'base_ks': 3,
            'deform_ks': 3,
        },
        'qenet': {
            'in_nc': 64,
            'out_nc': 1,
            'nf': 48,
            'nb': 8,
            'base_ks': 3,
        },
    }
    model = MFVQE(opts_dict=opts_dict)
    msg = f'loading model {ckp_path}...'
    print(msg)
    checkpoint = torch.load(ckp_path)
    if 'module.' in list(checkpoint['state_dict'].keys())[0]:  # multi-gpu training
        new_state_dict = OrderedDict()
        for k, v in checkpoint['state_dict'].items():
            name = k[7:]  # remove module
            new_state_dict[name] = v
        model.load_state_dict(new_state_dict)
    else:  # single-gpu training
        model.load_state_dict(checkpoint['state_dict'])

    msg = f'> model {ckp_path} loaded.'
    print(msg)
    model = model.cuda()
    model.eval()

    # ==========
    # Load entire video
    # ==========

    # pipeline 65-72
    # for piper_idx in range(58, 65):
    #     lq_yuv_dir = f'/data0/shuyanz/BVI_SR_processed/postfiltering{piper_idx}_median'
    #     lq_yuv_paths = [os.path.join(lq_yuv_dir, name.split('.')[0] + '_us.yuv') for name in video_names]
    #     save_yuv_dir = f'/data5/shuyanz/BVI_SR_processed/postfiltering{piper_idx+8}'

    # pipeline 89 - 96
    for piper_idx in range(85, 89):
        lq_yuv_dir = f'/data5/shuyanz/BVI_SR_processed/combination{piper_idx}_median'
        lq_yuv_paths = [os.path.join(lq_yuv_dir, name.split('.')[0] + '_us.yuv') for name in video_names]
        save_yuv_dir = f'/data5/shuyanz/BVI_SR_processed/combination{piper_idx+8}'
        os.makedirs(save_yuv_dir, exist_ok=True)
        save_yuv_paths = [os.path.join(save_yuv_dir, name) for name in video_names]
        for raw_yuv_path, lq_yuv_path, save_yuv_path in zip(raw_yuv_paths, lq_yuv_paths, save_yuv_paths):
            msg = f'loading raw and low-quality yuv...'
            print(msg)
            # print(lq_yuv_path)
            raw_y, raw_u, raw_v = utils.import_yuv(
                seq_path=raw_yuv_path, h=h, w=w, tot_frm=nfs, start_frm=0, only_y=False
            )
            lq_y, lq_u, lq_v = utils.import_yuv(
                seq_path=lq_yuv_path, h=h, w=w, tot_frm=nfs, start_frm=0, only_y=False
            )
            # print(len(lq_y),len(raw_y))
            raw_y = raw_y.astype(np.float32) / 255.
            lq_y = lq_y.astype(np.float32) / 255.
            msg = '> yuv loaded.'
            print(msg)

            # ==========
            # Define criterion
            # ==========
            criterion = utils.PSNR()
            unit = 'dB'

            # ==========
            # Test
            # ==========
            # pbar = tqdm(total=nfs, ncols=80)
            ori_psnr_counter = utils.Counter()
            enh_psnr_counter = utils.Counter()

            enh_frames = []
            for idx in range(nfs):
                # load lq
                idx_list = list(range(idx - 3, idx + 4))
                idx_list = np.clip(idx_list, 0, nfs - 1)
                input_data = []
                for idx_ in idx_list:
                    input_data.append(lq_y[idx_])
                input_data = torch.from_numpy(np.array(input_data))
                input_data = torch.unsqueeze(input_data, 0).cuda()

                # enhance
                with torch.inference_mode():
                    # with torch.cuda.amp.autocast(enabled=True, dtype=torch.float16):
                    # 如果你用了 model.half()，这里就可以不再 autocast
                    enhanced_frm = model(input_data)  # 推理
                # enhanced_frm = model(input_data)

                # eval
                gt_frm = torch.from_numpy(raw_y[idx])
                pred_y = enhanced_frm[0, 0].float().cpu()  # 回到 CPU 再算
                ori_y = input_data[0, 3].float().cpu()
                batch_ori = criterion(pred_y, gt_frm)
                batch_perf = criterion(ori_y, gt_frm)
                ori_psnr_counter.accum(volume=batch_ori)
                enh_psnr_counter.accum(volume=batch_perf)

                # display
                # pbar.set_description(
                #     "[{:.3f}] {:s} -> [{:.3f}] {:s}"
                #     .format(batch_ori, unit, batch_perf, unit)
                #     )
                # pbar.update()
                enh_np = enhanced_frm[0, 0].detach().cpu().numpy()
                enh_frames.append(enh_np)

            enh_y = (np.stack(enh_frames) * 255.0 + 0.5).astype(np.uint8)

            # 直接拿原 LQ 的 U/V（它们已是 uint8，shape: (nfs, h//2, w//2)）
            u_plane = lq_u[:nfs]  # 若 utils.import_yuv 返回的是 (N,H/2,W/2)
            v_plane = lq_v[:nfs]

            # utils.export_yuv 是 STDF 提供的辅助函数；如果仓库里没有，就用 numpy.tofile
            # save_path = 'results/Boat_MFVQE_Yonly.yuv'
            # utils.export_yuv(save_path, enh_y, u_plane, v_plane)
            np.concatenate([enh_y.reshape(nfs, -1), u_plane.reshape(nfs, -1), v_plane.reshape(nfs, -1)], axis=1).tofile(
                save_yuv_path)
            print(f'> enhanced sequence saved to {save_yuv_path}')

            # pbar.close()
            ori_ = ori_psnr_counter.get_ave()
            enh_ = enh_psnr_counter.get_ave()
            print('ave ori [{:.3f}] {:s}, enh [{:.3f}] {:s}, delta [{:.3f}] {:s}'.format(
                ori_, unit, enh_, unit, (enh_ - ori_), unit
            ))
    print('> done.')


if __name__ == '__main__':
    main()
