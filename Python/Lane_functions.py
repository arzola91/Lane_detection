import cv2
import numpy
import matplotlib.pyplot as plt
import math


def region_of_interest(img,vertices):

	mask = numpy.zeros_like(img)

	if len(img.shape) > 2:
		channel_count = img.shape[2]
		ignore_mask_color = (255,) * channel_count
	else:
		ignore_mask_color = 255

	cv2.fillPoly(mask, vertices, ignore_mask_color)

	masked_image = cv2.bitwise_and(img, mask)
	
	return masked_image


def image_lanes(bin_im):              #Encuntra el/los carril(es) en una imagen binaria
    base_img = bin_im[160:240, 0:320]     #Obtener imagen sobre cual buscar la base 
    histogram = numpy.sum(base_img[base_img.shape[0]/2:,:], axis=0)	
        
###### Buscar puntos altos de histograma
    points = []
    i = 0
    for point in histogram:
        if point > 400:
            points += [i]
        i = i+1
###### dividirlos en clusters

    if (points != []):
        lane1 = [points[0]]
        lane2 = []
        j = 0

        for point in points:
            if point-numpy.mean(lane1) < 25:              #CAMBIE A 50... para no equivocarme y poner un solo carril.. pero ver que paso con eso
                lane1 += [point]
            else:
                lane2 += [point]
    else:
        lane1 = []
        lane2 = []
        
    print(lane1)
    print(lane2)
    return lane1, lane2

def poly_for_lane(lane,im):		#out_image es im

    x_base = int(numpy.mean(lane))
    nwindows = 12		#Number of sections for lane
    window_height = int((240-160)/nwindows)

    nonzero = im.nonzero()
    nonzeroy = numpy.array(nonzero[0])
    nonzerox = numpy.array(nonzero[1])

    margin = 15	
    minpix = 5
    x_current = x_base
    lane_inds = []

    for window in range(nwindows):
        win_y_low = im.shape[0] - (window+1)*window_height
        win_y_high = im.shape[0] - (window)*window_height
        win_x_low = x_current - margin
        win_x_high = x_current + margin
        cv2.rectangle(im,(win_x_low,win_y_low),(win_x_high,win_y_high), (0,255,0),2)

        good_inds = ((nonzeroy >= win_y_low)&(nonzeroy < win_y_high)&(nonzerox >= win_x_low)&(nonzerox < win_x_high)).nonzero()[0]

        lane_inds.append(good_inds)
		#plt.imshow(im)
		#plt.show()

        if len(good_inds) > minpix:
            x_current = numpy.int(numpy.mean(nonzerox[good_inds]))

    lane_inds = numpy.concatenate(lane_inds)

    lane_x = nonzerox[lane_inds]
    lane_y = nonzeroy[lane_inds]

    poly = numpy.polyfit(lane_y,lane_x,2)

    return poly


def center_lane_f2(xr,xl,y):

    y_c = numpy.zeros(240)
    x_c = numpy.zeros(240)

    for j in range(0,239):
        x_c[j] = (xr[j]+xl[j])/2
        y_c[j] = y[j]

    center_poly = numpy.polyfit(y_c,x_c,2)

    return center_poly

def center_lane_f1(x,y,s):

    y_c = numpy.zeros(240)
    x_c = numpy.zeros(240)
    d = 42
    if (s == 2):
        for j in range(0,239):

            x_c[j] = x[j]-d
            y_c[j] = y[j]
    elif (s == 3):

        for j in range(0,239):
            x_c[j] = x[j]+d
            y_c[j] = y[j]

    center_poly = numpy.polyfit(y_c,x_c,2)


    return center_poly


