import tifffile
import numpy as np

img = tifffile.imread("Task1_Remote_Sensing/ms-BOCD Data/matrix_736.tif")

print(img.dtype)  # devrait afficher float64

img32 = img.astype(np.float32)

print(img.dtype)

tifffile.imwrite("Task1_Remote_Sensing/ms-BOCD Data/matrix_736_float32.tif", img32)