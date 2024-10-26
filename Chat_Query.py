from LLM import *
from Knowledge import *

from enum import Enum
from PIL import Image
import base64
from io import BytesIO


class Role(Enum):
    system = "system"
    user = "user"
    ai = "assistant"
    agent = "agent"

class Chat_request:
    def __init__(self, prompt: str, images: list=None, knowledge: Knowledge=None, use_knowledge: bool | list=True, use_summary: bool=False, role=Role.user) -> None:
        self.role = role
        self.prompt = prompt
        self.images = self.process_image(images=images)
        self.knowledge = knowledge
        self.use_summary = use_summary
        
        if use_knowledge == True:
            if self.knowledge is None:
                # do not use knowledge at all
                self.use_knowledge = []
            else:
                # use all knowledge
                self.use_knowledge = list(range(len(self.knowledge.memories)))
            
        elif use_knowledge == False or use_knowledge is None:
            # do not use knowledge at all
            self.use_knowledge = []
        else:
            # use selected knowledge
            self.use_knowledge = use_knowledge

        
    def process_image(self, images: list):
        """
        Process a list of images by resizing them to maintain aspect ratio and then converting them to base64 format.
        
        Args:
            images (list): A list of image objects to be processed.

        Returns:
            list: A list of base64-encoded image strings if input is not None/empty, otherwise `None`.
        
        Note:
            - Images should be provided as a "list" even if there is only a single image to process.
        """
        base64_images = []
        
        if images != None:
            for image in images:
                image = self.resize_image_aspect_ratio(image=image)
                image = self.convert_to_base64(image=image)
                base64_images.append(image)

            return base64_images

        else:
            return None
        
    def convert_to_base64(self, image: Image) -> str:
        """
        Convert an image to a base64-encoded string.

        Args:
            image (Image): The image object to be converted to base64 format.

        Returns:
            str: The base64-encoded string representation of the image.

        Note:
            - The image format will default to 'JPEG' if the format is not specified.
        """

        
        buffered = BytesIO()
        format = image.format if image.format else 'JPEG'
        image.save(buffered, format=format)
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        return img_base64
    
    def resize_image_aspect_ratio(self, image: Image, target_length=1024):
        """
        Resize an image to a target length while maintaining its aspect ratio.

        Args:
            image (Image): The image object to be resized.
            target_length (int, optional): The target length for the larger dimension (default is 1024).

        Returns:
            Image: The resized image object with maintained aspect ratio.

        Note:
            - The smaller dimension is scaled proportionally based on the larger dimension to maintain aspect ratio.
            - If the image's aspect ratio is non-square, the target_length is applied to the larger dimension.
        """
        
        width, height = image.size
        
        if width > height:
            new_width = target_length
            new_height = int((target_length / width) * height)
        else:
            new_height = target_length
            new_width = int((target_length / height) * width)

        resized_image = image.resize((new_width, new_height))
        
        return resized_image
    
class Chat_response(Chat_request):
    def __init__(self, text: str, model: LLM, input_token: int, output_token: int, 
                 input_cost: float, output_cost: float, total_cost: float, 
                 error: bool = False, error_reason: str = None, 
                 prompt: str = '', images: list = None, knowledge=None, role=Role.ai) -> None:
        super().__init__(prompt=text, images=images, knowledge=knowledge, role=role)
        self.text = text
        self.model = model
        self.input_token = input_token
        self.output_token = output_token
        self.input_cost = input_cost
        self.output_cost = output_cost
        self.total_cost = total_cost
        self.error = error
        self.error_reason = error_reason
        