from diffusers import StableDiffusionPipeline
import torch

# パイプラインの準備
pipe = StableDiffusionPipeline.from_single_file(
    "ProjectTurn8-Stella-pruned.safetensors",
    torch_dtype=torch.float16,
)

# EasyNegativeV2の準備
pipe.load_textual_inversion("embed/negative",weight_name="EasyNegativeV2.safetensors",token="EasyNegative")

# NSFWの無効化
pipe.safety_checker = lambda images, **kwargs: (images, [False] * len(images))

prompt = "cute cat ear maid"
negative_prompt = "EasyNegativeV2, bad face"

# 画像生成の実行
image = pipe(
    prompt,
    width  = 256, height = 256,
    negative_prompt=negative_prompt,
    num_inference_steps = 10,
    
).images[0]  

# 画像の保存と表示
image.save("output.png")
image