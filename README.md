# A-VQA-Dataset-for-Prefiltering-and-Postfiltering-in-Video-Compression
This initiative created a dedicated video quality assessment dataset to drive the development of intelligent pre-processing and post-processing filters for next-generation video compression.

## Video Source

[BVI-SR](https://data.bris.ac.uk/data/dataset/1gqlebyalf4ha25k228qxh5rqz)

## Pipeline

### Baseline

yuv $\rightarrow$ **Lanczos Downsampling** $\rightarrow$ yuv $\rightarrow$ **Encoding** $\rightarrow$ mp4 $\rightarrow$ **Decoding** $\rightarrow$ yuv $\rightarrow$ **Lanczos Upsampling** yuv

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

WIDTH_DS = [1920, 1280, 960, 640]
HEIGHT_DS = [1080, 720, 540, 360]
BIT_RATE = ['5800k', '3000k', '1750k', '750k']
BUF_SIZE = ['11600k', '6000k', '3500k', '1500k']
