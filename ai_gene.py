import torch
from diffusers import StableDiffusionPipeline
from diffusers import LCMScheduler

# Load the model
pipeline = StableDiffusionPipeline.from_pretrained(
    "SG161222/Realistic_Vision_V2.0",
    torch_dtype=torch.float16,
    )
pipeline = pipeline.to("cuda")

pipeline.load_lora_weights(".", weight_name="lora.safetensors")

def generate(prompt, negative_prompt=None, lora_params=None):
    pipeline.scheduler = LCMScheduler.from_config(pipeline.scheduler.config)
    image = pipeline(
        prompt,
        negative_prompt=negative_prompt,
        lora_params=lora_params,
        guidance_scale=1,
        num_inference_steps=4,
        num_images_per_prompt=1,
        height=256,
        width=256,
    ).images[0]
    return image


prompt = "8k, high quality, real photo, yellow taxi, full body"
ng_prompt = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
image = generate(prompt, ng_prompt)
image