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