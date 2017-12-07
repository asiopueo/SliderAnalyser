import PIL
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
import numpy as np




def absSobelThresh(img, sobel_kernel=3, thresh=(0,255), orient='x'):
	if img.shape[2] > 1:
		gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

	if orient == 'x':
		sobelx = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
		abs_sobelx = np.absolute(sobelx)
		scaled_sobelx = np.uint8(255*abs_sobelx/np.max(abs_sobelx))
		sxbinary = np.zeros_like(scaled_sobelx)
		sxbinary[(scaled_sobelx >= thresh[0]) & (scaled_sobelx <= thresh[1])] = 1
		binary_output = sxbinary
	elif orient == 'y':
		sobely = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
		abs_sobely = np.absolute(sobely)
		scaled_sobely = np.uint8(255*abs_sobely/np.max(abs_sobely))
		sybinary = np.zeros_like(scaled_sobely)
		sybinary[(scaled_sobely >= thresh[0]) & (scaled_sobely <= thresh[1])] = 1
		binary_output = sybinary
	else:
		raise

	return binary_output


def dirThresh(img, sobel_kernel=3, thresh=(0, np.pi/2) ):
	if img.shape[2] > 1:
		gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
	
	sobelx = cv2.Sobel(gray, cv2.CV_64F, 0, 1, sobel_kernel)
	sobely = cv2.Sobel(gray, cv2.CV_64F, 1, 0, sobel_kernel)
	
	absgraddir = np.arctan2(np.absolute(sobely), np.absolute(sobelx))
	#  Rescaling is absolutely essential!
	scale_factor = np.max(absgraddir) / 255			
	absgraddir = (absgraddir/scale_factor).astype(np.uint8)
	
	binary_output = np.zeros_like(absgraddir)
	binary_output[(absgraddir >= thresh[0]) & (absgraddir <= thresh[1])] = 1

	return binary_output


def magThresh(img, sobel_kernel=3, thresh=(0,255) ):
	if img.shape[2] > 1:
		gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
	
	sobelx = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
	sobely = cv2.Sobel(gray, cv2.CV_64F, 1, 0)

	gradMag = np.sqrt(sobelx**2 + sobely**2)
	scale_factor = np.max(gradMag) / 255
	gradMag = (gradMag/scale_factor).astype(np.uint8)

	binary_output = np.zeros_like(gradMag)
	binary_output[(gradMag >= thresh[0]) & (gradMag <= thresh[1])] = 1
	
	return binary_output



if __name__=='__main__':

	ksize = 3

	image = cv2.imread('./test_images/straight_lines1.jpg')

	gradx = absSobelThresh(image, orient='x', sobel_kernel=ksize, thresh=(0,20))
	grady = absSobelThresh(image, orient='y', sobel_kernel=ksize, thresh=(0,20))

	mag_binary = magThresh(image, sobel_kernel=ksize, thresh=(0,25) )
	dir_binary = dirThresh(image, sobel_kernel=ksize, thresh=(0,np.pi/2.) )

	composite = np.zeros_like(dir_binary)
	composite[((gradx==0)|(grady==0)) & ((mag_binary==0)|(dir_binary==0)) ] = 1

	plt.imshow(composite, cmap='gray')
	plt.show()

	mpimg.imsave('./output_images/gradients_binary.png', composite, cmap=mpimg.cm.gray)










