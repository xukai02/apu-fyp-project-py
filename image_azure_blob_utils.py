import base64
from azure.storage.blob import BlobServiceClient
from flask import jsonify


connect_str='DefaultEndpointsProtocol=https;AccountName=fyptest;AccountKey=ayyZvGIYSC+XkNPlZxRAV1MK6XBaDiHOFurrDFhpJm2P/4w/qx3wlvTa3wffGSP84CxFPks/vfYc+AStYqLUxw==;EndpointSuffix=core.windows.net'

PRODUCT_CONTAINER_NAME = 'products'
RATE_CONTAINER_NAME = 'rates'
SHOPPROFILE_CONTAINER_NAME = 'shop-profile'
PROFILE_CONTAINER_NAME = 'profile'

blob_service_client = BlobServiceClient.from_connection_string(connect_str)

def getContainerClient(containerName):
    try:
        container_client = blob_service_client.create_container(containerName)
    except Exception as ex:
        container_client = blob_service_client.get_container_client(containerName)
    return container_client

def uploadImages(containerName, images):
    container_client = getContainerClient(containerName)
    for image in images:        
        try:
            container_client.upload_blob(image['name'],base64.b64decode(image['image']))
        except Exception as ex:
            print(ex)

def getImagesByProductId(containerName, productId):
    imageNameList=[]
    imageList =[]
    container_client = getContainerClient(containerName)
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        if str(productId) == str(blob.name).split('/')[0]:
            imageNameList.append(blob.name)

            blob_client = container_client.get_blob_client(blob.name)
            
            imageList.append(blob_client.url)
    return [{
        'name': imageName,
        'image': image
    }for imageName, image in zip(imageNameList,imageList)]

def deleteImagesByProductId(containerName, productId):
    container_client = getContainerClient(containerName)
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        if str(productId) == str(blob.name).split('/')[0]:
            blob_client = container_client.get_blob_client(blob.name)
            blob_client.delete_blob()
    return

def uploadShopProfileImage(containerName, shopId, image):
    container_client = getContainerClient(containerName)
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        if str(shopId) == str(blob.name).split('.')[0]:
            blob_client = container_client.get_blob_client(blob.name)
            blob_client.delete_blob()

    container_client = getContainerClient(containerName)   
    try:
        container_client.upload_blob(shopId + '.png',base64.b64decode(image))
    except Exception as ex:
        print(ex)

def uploadProfileImage(containerName, id, image):
    container_client = getContainerClient(containerName)
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        if str(id) == str(blob.name).split('.')[0]:
            blob_client = container_client.get_blob_client(blob.name)
            blob_client.delete_blob()

    container_client = getContainerClient(containerName)   
    try:
        container_client.upload_blob(str(id) + '.png',base64.b64decode(image))
    except Exception as ex:
        print(ex)

def getImageUrl(containerName, imageName):
    imageUrl = None
    container_client = getContainerClient(containerName)
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        if str(imageName) == str(blob.name).split('.')[0]:
            blob_client = container_client.get_blob_client(blob.name)
            imageUrl = blob_client.url
    return imageUrl

    