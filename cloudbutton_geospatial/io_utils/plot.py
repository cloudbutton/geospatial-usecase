from matplotlib import pyplot as plt
from ibm_botocore.client import Config, ClientError
import rasterio
import random
import ibm_boto3

def plot_random_blocks(bucket, item, num):
    """
    Plot num random blocks from IBM COS item located at bucket
    """
    
    fig, axs = plt.subplots(num, figsize=(20,30))
    cos = ibm_boto3.resource("s3",
                             config=Config(signature_version="oauth"),
                             endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud"
                             )
    obj = cos.Object(bucket, item)
    with rasterio.open(obj.get()['Body']) as src:
        for j in range(0,num):
            ij, window = random.choice(list(src.block_windows()))
            arr = src.read(1, window=window)
            plt.subplot(1 + (num-1)/2, 2, j+1)
            plt.gca().set_title(item)
            plt.imshow(arr)
            plt.colorbar(shrink=0.5)
    plt.show()

def plot_results(bucket, results):
    """
    Plot an array of COS from IBM Cloud
    """
    size = len(results)
    fig, axs = plt.subplots(len(results), figsize=(20,30))

    cos = ibm_boto3.resource("s3",
                             config=Config(signature_version="oauth"),
                             endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud"
                             )
    i = 1
    for item in results:
        obj = cos.Object(bucket, item)
        with rasterio.open(obj.get()['Body']) as src:
            arr = src.read(1, out_shape=(src.height//10, src.width//10))
            plt.subplot(1 + (size-1)/2, 2, i)
            plt.gca().set_title(item)
            plt.imshow(arr)
            plt.colorbar(shrink=0.5)
            i += 1
    
    plt.show()

def tiff_overview(tiff_url):
    """
    Plot the a little version of the map (thumbnail)
    """
    with rasterio.open(tiff_url) as dataset:
        oviews = dataset.overviews(1)  # list of overviews from biggest to smallest
        oview = oviews[-1]  # let's look at the smallest thumbnail
        print('Decimation factor= {}'.format(oview))
        # NOTE this is using a 'decimated read' (http://rasterio.readthedocs.io/en/latest/topics/resampling.html)
        thumbnail = dataset.read(1, out_shape=(1, int(dataset.height // oview), int(dataset.width // oview)))

    print('array type: ', type(thumbnail))

    plt.figure(figsize=(5, 5))
    plt.imshow(thumbnail)
    plt.colorbar()
    plt.title('Overview - Band 4 {}'.format(thumbnail.shape))
    plt.xlabel('Column #')
    plt.ylabel('Row #')


def plot_map(image, title, x_label="", y_label=""):
    plt.figure(figsize=(10, 15))
    plt.imshow(image)
    plt.colorbar(shrink=0.5)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
