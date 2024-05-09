from diffusers.utils import load_image
from controlnet_aux import OpenposeDetector


print('初期画像の準備')

# 初期画像をロードしてリサイズする
init_image = load_image("waif.png")  # 画像をロード
init_image = init_image.resize((512, 512))  # 512x512にリサイズ

# 初期画像の確認（ノートブック上で表示）
init_image