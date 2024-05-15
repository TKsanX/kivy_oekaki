import diffusers, torch
from diffusers import AutoencoderKL


#vae = AutoencoderKL.from_single_file("Counterfeit-V2.5.vae.pt")


pipe = diffusers.StableDiffusionPipeline.from_pretrained("xyn-ai/anything-v4.0",torch_dtype=torch.float16)
pipe.scheduler = diffusers.DDIMScheduler.from_config(pipe.scheduler.config)
pipe.load_textual_inversion("EasyNegative-test", weight_name="EasyNegative.safetensors", token="EasyNegative")
negative_prompt = "EasyNegative"


pipe.safety_checker = None
seeds = [12345]
steps = 28
prompt = "girl eating pizza"
negative_prompt = "EasyNegative, badhandv4"
for i, seed in enumerate(seeds):
    print(f"{i}: {seed}")
    torch.manual_seed(seed)
    result = pipe(prompt = prompt, negative_prompt = negative_prompt,
                  width  = 512, height = 512, num_inference_steps = steps)
    result.images[0].save(f"{seed}-{steps}-ddim-neg.png")