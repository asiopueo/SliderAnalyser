import PIL
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import cv2







def HLS_Channel(img_bgr, thresh=(0,255), channel='l'):

	img_hls = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HLS)
	
	if channel == 'h':
		colorChannel = img_hls[:,:,0]		
	
	elif channel == 'l':
		colorChannel = img_hls[:,:,1]
	
	elif channel == 's':
		colorChannel = img_hls[:,:,2]

	else:
		raise

	binary = np.zeros_like(colorChannel)
	binary[(colorChannel >= thresh[0]) & (colorChannel <= thresh[1])] = 1

	return binary





if __name__=='__main__':

	image_bgr = cv2.imread('./test_images/signs_vehicles_xygrad.png')
	
	h_binary = HLS_Channel(image_bgr, 'h', thresh=(5,30))
	l_binary = HLS_Channel(image_bgr, 'l', thresh=(5,30))
	s_binary = HLS_Channel(image_bgr, 's', thresh=(5,30))

	plt.imshow(s_binary, cmap='gray')
	plt.show()

	mpimg.imsave('./output_images/h_binary.png', h_binary, cmap='gray')
	mpimg.imsave('./output_images/l_binary.png', l_binary, cmap='gray')
	mpimg.imsave('./output_images/s_binary.png', s_binary, cmap='gray')










