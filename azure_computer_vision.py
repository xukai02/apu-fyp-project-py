import base64
import io
import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import requests

url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRXHCx4tEGafs_V5PFUvbGYp1lEtuEJHubvDRntXWi4&s'

response = requests.get(url, stream=True)
if response.status_code == 200:
    with open('image.jpg', 'wb') as f:
        f.write(response.content)


# Set up authentication and endpoint variables
ENDPOINT = 'https://fypcomputervision.cognitiveservices.azure.com/'
SUBSCRIPTION_KEY = '7ab233fbcab34cf192d7a289f9873dcf'
computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(SUBSCRIPTION_KEY))

# # Specify the image URL
# image_url = 'https://fyptest.blob.core.windows.net/products/11/2023-04-11 00:11:54.056309.png'

# # Call the Computer Vision API to analyze the image
# image_analysis = computervision_client.analyze_image(image_url, visual_features=['Categories', 'Tags', 'Description'])
# image_path = 'D:/Downloads/archive/train/train/41/00fafcaa1ad5c30b38177384715e8198.jpg'
# with open(image_path, 'rb') as image_file:
#     image_data = image_file
#     image_analysis = computervision_client.analyze_image_in_stream(image_data,visual_features=['Categories','Tags','Description'])

# # Print the analysis results
# print(image_analysis)
# for category in image_analysis.categories:
#     print(category.name)
    
# for tag in image_analysis.tags:
#     print(tag.name, tag.confidence)
    
# print(image_analysis.description.captions[0].text)

def getImageDetails(base64Image):
    image_bytes = base64.b64decode(base64Image)
    image_stream = io.BytesIO(image_bytes)
    image_analysis = computervision_client.analyze_image_in_stream(image_stream,visual_features=['Tags','Description','Color','Objects','Brands'])
    print(image_analysis.color)
    tags = []
    for tag in image_analysis.tags:
        tags.append(tag.name)
    colors = image_analysis.color.dominant_colors
    brands =[]
    for brand in image_analysis.brands:
        brands.append(brand.name)
    objects = []
    for object in image_analysis.objects:
        objects.append(object.object_property)
    description = image_analysis.description.captions[0].text
    data = {
        'tags':tags,
        'colors':colors,
        'description': description,
        'objects':objects,
        'brands':brands
    }
    return data