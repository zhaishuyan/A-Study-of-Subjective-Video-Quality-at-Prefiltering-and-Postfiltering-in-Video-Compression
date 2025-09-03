# A-VQA-Dataset-for-Prefiltering-and-Postfiltering-in-Video-Compression
This initiative created a dedicated video quality assessment dataset to drive the development of intelligent pre-processing and post-processing filters for next-generation video compression.

## Video Source

[BVI-SR](https://data.bris.ac.uk/data/dataset/1gqlebyalf4ha25k228qxh5rqz)

## Pipelines

For each category, we sample four bitrates, each corresponding to a distinct downsampling resolution, and apply them to both H.265 and AV1 encoders. This results in a total of eight pipelines per category.

### 1. Baseline

Pipeline:

yuv $\rightarrow$ **Lanczos Downsampling** $\rightarrow$ yuv $\rightarrow$ **Encoding** $\rightarrow$ mp4 $\rightarrow$ **Decoding** $\rightarrow$ yuv $\rightarrow$ **Lanczos Upsampling** $\rightarrow$ yuv

Commands:

- Lanczos downsampling

```
ffmpeg -s 3840x2160 -r 30 -pix_fmt yuv420p -f rawvideo -i Boat.yuv -vf scale={WIDTH_IN}:{HEIGHT_IN}:flags=lanczos -f rawvideo -pix_fmt yuv420p Boat_ds.yuv
```

- Encoding

```
# H.265
ffmpeg -s f'{WIDTH_DS}x{HEIGHT_DS}' -r 30 -pix_fmt yuv420p -f rawvideo -i Boat_ds.yuv -c:v libx265 -preset medium -b:v 30 -maxrate f'{BIT_RATE}' -bufsize f'{BUF_SIZE}' -x265-params profile=main -movflags +faststart Boat_ec.yuv
# AV1
ffmpeg -s f'{WIDTH_DS}x{HEIGHT_DS}' -r 30 -pix_fmt yuv420p -f rawvideo -i Boat_ds.yuv -c:v libsvtav1 -b:v f'{BIT_RATE}' -bufsize f'{BUF_SIZE}' -movflags +faststart Boat_ec.mp4
```

- Decoding

```
ffmpeg -i Boat_ec.mp4 -c:v rawvideo -pix_fmt yuv420p -f rawvideo Boat_dc.yuv
```

- Lanczos upsamling

```
ffmpeg -s f'{WIDTH_DS}x{HEIGHT_DS}' -r 30 -pix_fmt yuv420p -f rawvideo -i Boat_dc.yuv -vf scale=3840:2160:flags=lanczos -f rawvideo -pix_fmt yuv420p Boat_us.yuv
```

Here, the variable are valued as follow:

WIDTH_DS $\in$ [1920, 1280, 960, 640]

HEIGHT_DS $\in$ [1080, 720, 540, 360]

BIT_RATE $\in$ ['5800k', '3000k', '1750k', '750k']

BUF_SIZE $\in$ ['11600k', '6000k', '3500k', '1500k']

### 2. Prefiltering

#### 2.1 Deep Downsampling

Deep Downsampler: [Learned Image Downscaling for Upscaling using Content Adaptive Resampler. TIP 2020.](https://github.com/sunwj/CAR)

Pipeline:

yuv $\rightarrow$ **Deep Downsampling** $\rightarrow$ yuv $\rightarrow$ **Encoding** $\rightarrow$ mp4 $\rightarrow$ **Decoding** $\rightarrow$ yuv $\rightarrow$ **Lanczos Upsampling** $\rightarrow$ yuv

Commands:

Compared to the baseline, only the downsampling command is changed in this pipeline. The encoding, decoding and upsampling commands are the same as those in the baseline.

The deep downsampling procedure can be divided into three steps:

**Step 1 (optional).** 1.5x downsample the RGB images by the Lanczos filter

The published CAR parameters include 2x and 4x downsampling filters. Since our settings also require 3x and 6x downsampling, we first apply a 1.5x downsampling using the Lanczos filter.

**Step 2.**  Convert a yuv420p video to RGB images;

```
def YUVvideo2IMGs(yuv_video_path, output_dir, height, width):
    img_size = (height * width * 3 // 2)
    frames = int(os.path.getsize(yuv_video_path) / img_size)

    with open(yuv_video_path, 'rb') as f:
        for frame_idx in range(frames):
            yuv = np.zeros(shape=img_size, dtype='uint8', order='C')
            for j in range(img_size):
                yuv[j] = ord(f.read(1))
            img = yuv.reshape((height * 3 // 2, width))
            bgr_img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_I420)
            if bgr_img is not None:
                output_path = os.path.join(output_dir, f'frame_{frame_idx:05d}.bmp')
                cv2.imwrite(output_path, bgr_img)
```

**Step 3.**  Downsample the RGB images by CAR;

```
python run_downsample.py --img_dir /path/to/high/resolution/images/ --scale 2 --output_dir /path/to/low/resolution/images/
```

**Step 4.**  Convert RGB images to a yuv420p video.

```
def IMG2YUVvideo(img_dir, prefix, save_path):
    image_files = [f for f in os.listdir(img_dir)
                   if f.startswith(prefix) and f.lower().endswith(('.bmp'))]
    img_list = sorted(image_files)
    img = cv2.imread(os.path.join(img_dir, img_list[0]))
    (height, width, _) = img.shape
    with open(save_path, 'wb') as f:
        for img_name in img_list:
            img_path = os.path.join(img_dir, img_name)
            img = cv2.imread(img_path)
            yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420)
            yuv = yuv.reshape(height * width * 3 // 2)
            f.write(np.array(yuv, dtype='uint8').tobytes())
```

#### 2.2 Denoising

Denoising filter: BM3D

Pipeline:

yuv $\rightarrow$ **BM3D Denoising** $\rightarrow$ **Lanczos Downsampling** $\rightarrow$ yuv $\rightarrow$ **Encoding** $\rightarrow$ mp4 $\rightarrow$ **Decoding** $\rightarrow$ yuv $\rightarrow$ **Lanczos Upsampling** $\rightarrow$ yuv

Denoising should be operated before downsampling, which is claimed in [link](https://sonnati.wordpress.com/2012/10/19/ffmpeg-the-swiss-army-knife-of-internet-streaming-part-vi/).

Commands:

```
# Denoising
ffmpeg -s {WIDTH_IN}x{HEIGHT_IN} -r 30 -pix_fmt yuv420p -f rawvideo -i Boat.yuv -filter_complex bm3d=sigma=20:block=16:bstep=2:group=1:estim=basic -f rawvideo -pix_fmt yuv420p Boat_dn.yuv
```

Besides, the Lanczos downsampling command, encoding command, decoding command and Lanczos upsampling command are the same as those in the baseline.

### 2.3 Sharpening

Sharpening filter improves the end-to-end compression efficiency with respect to the original source video under a fixed heuristic filter parameter set, which is mentioned in [VMAF Based Rate-Distortion Optimization for Video Coding. MMSP 2020].

Sharpening filter: ffmpeg unsharp

Pipeline:

yuv $\rightarrow$ **Lanczos Downsampling** $\rightarrow$ **Sharpening** $\rightarrow$ yuv $\rightarrow$ **Encoding** $\rightarrow$ mp4 $\rightarrow$ **Decoding** $\rightarrow$ yuv $\rightarrow$ **Lanczos Upsampling** $\rightarrow$ yuv

Commands:
```
# Unsharp
ffmpeg -s {WIDTH_DS}x{HEIGHT_DS} -r str(FPS) -pix_fmt yuv420p -f rawvideo -i Boat_ds.yuv -vf unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=1.0:chroma_msize_x=3:chroma_msize_y=3:chroma_amount=0.0 -f rawvideo -pix_fmt yuv420p Boat_sharp.yuv
```

Besides, the Lanczos downsampling command, encoding command, decoding command and Lanczos upsampling command are the same as those in the baseline.
