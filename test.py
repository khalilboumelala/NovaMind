from diffusers import MotionAdapter
import xformers
import accelerate
adapter = MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2")
print("Environment set up correctly!")