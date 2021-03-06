
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import math



def region_of_interest(img,vertices):
	"""
	Only keeps the region of the image defined by the polygon formed from
	'vertices'. The rest of the image is set to black
	"""
	#defining a blank mask to start whit
	mask = np.zeros_like(img)

	if len(img.shape) > 2:
		channel_count = img.shape[2]
		ignore_mask_color = (255,) * channel_count
	else:
		ignore_mask_color = 255

	cv2.fillPoly(mask, vertices, ignore_mask_color)

	masked_image = cv2.bitwise_and(img, mask)
	
	return masked_image





def mean_lines(img, lines): # color, thickeness):
	
	imshape = img.shape

	ymin_global = img.shape[0]
	ymax_global = 0



	all_left_grad = []
	all_left_y = []
	all_left_x = []

	all_right_grad = []
	all_right_y = []
	all_right_x = []

###########################	
	#for line in lines:
	#	for x1,y1,x2,y2 in line:
	#		cv2.line(img,(x1,y1),(x2,y2),[0,255,0],1)
	
	#cv2.imshow('lineas',img) #Mostrar imagen

	#cv2.waitKey(10000) 
###########################

	for line in lines:
		for x1,y1,x2,y2 in line:
			x_1 = float(x1)	
			x_2 = float(x2)	
			y_1 = float(y1)			
			y_2 = float(y2)		
			if (x2 != x1):			
				gradient = -(y_2-y_1) / (x_2-x_1)
			
				ymin_global = min(min(y1,y2), ymin_global)
				ymax_global = max(max(y1,y2), ymax_global)
				if (gradient > 0):
					all_left_grad += [gradient]
					all_left_y += [y_1, y_2]
					all_left_x += [x_1, x_2]
				else:
					all_right_grad += [gradient]
					all_right_y += [y_1, y_2]
					all_right_x += [x_1, x_2]

	left_mean_grad = -np.mean(all_left_grad)
	left_y_mean = np.mean(all_left_y)
	left_x_mean = np.mean(all_left_x)
	left_intercept = left_y_mean - (left_mean_grad*left_x_mean)


	right_mean_grad = -np.mean(all_right_grad)
	right_y_mean = np.mean(all_right_y)
	right_x_mean = np.mean(all_right_x)
	right_intercept = right_y_mean - (right_mean_grad*right_x_mean)



	if ((len(all_left_grad) >0) and (len(all_right_grad) >0)):
		upper_left_x = int((ymin_global - left_intercept) / left_mean_grad)
		lower_left_x = int((ymax_global - left_intercept) / left_mean_grad)
		upper_right_x = int((ymin_global - right_intercept) / right_mean_grad)
		lower_right_x =  int((ymax_global - right_intercept) / right_mean_grad)

		#cv2.line(img, (upper_left_x, ymin_global), (lower_left_x, ymax_global), color, thickeness)
		#cv2.line(img, (upper_right_x, ymin_global), (lower_right_x, ymax_global), color, thickeness)
                upper_center_x = (upper_left_x+upper_right_x)/2
		lower_center_x = (lower_left_x+lower_right_x)/2

		#cv2.line(img,(upper_center_x, ymin_global),(lower_center_x, ymax_global),[0,255,0],thickeness)
		
		left_lane = np.array([upper_left_x, ymin_global, lower_left_x, ymax_global])
		right_lane = np.array([upper_right_x, ymin_global, lower_right_x, ymax_global])	
		center_lane = np.array([upper_center_x, ymin_global, lower_center_x, ymax_global])
		
		return left_lane, right_lane, center_lane




def lane_warping(lane, tMtx):
	
	x1 = lane[0]
	y1 = lane[1]
	x2 = lane[2]
	y2 = lane[3]
	
	wx1 = (tMtx[0,0]*x1+tMtx[0,1]*y1+tMtx[0,2])/(tMtx[2,0]*x1+tMtx[2,1]*y1+tMtx[2,2])
	wy1 = (tMtx[1,0]*x1+tMtx[1,1]*y1+tMtx[1,2])/(tMtx[2,0]*x1+tMtx[2,1]*y1+tMtx[2,2])
	wx2 = (tMtx[0,0]*x2+tMtx[0,1]*y2+tMtx[0,2])/(tMtx[2,0]*x2+tMtx[2,1]*y2+tMtx[2,2])
	wy2 = (tMtx[1,0]*x2+tMtx[1,1]*y2+tMtx[1,2])/(tMtx[2,0]*x2+tMtx[2,1]*y2+tMtx[2,2])
	wlane = np.array([wx1,wy1,wx2,wy2])
	wlane = wlane.astype(int)
	return wlane
 



def draw_lane(img, lane, color, thickeness):

	cv2.line(img,(lane[0],lane[1]), (lane[2],lane[3]), color, thickeness)




def vehicle_position(lane):
	
	x1 = float(lane[0])
	y1 = float(lane[1])
	x2 = float(lane[2])
	y2 = float(lane[3])
	
	d = math.sqrt(math.pow(x2-x1,2)+math.pow(y2-y1,2))
	h = x1-x2
	ang_rad = math.asin(h/d)
	ang_deg = ang_rad*180/math.pi
	return ang_deg



def image_lanes(bin_im):                        	#Encuntra el/los carril(es) en una imagen binaria
	base_img = bin_im[320:480, 0:640]     		#Obtener imagen sobre cual buscar la base (solamente los primeros 50 pixeles)
 	histogram = np.sum(base_img[base_img.shape[0]/2:,:], axis=0)	
        
	###### Buscar puntos altos de histograma
	points = []
	i = 0
	for point in histogram:
		if point > 400:
			points += [i]
		i = i+1
	###### dividirlos en clusters


	lane1 = [points[0]]
	lane2 = []
	j = 0

	for point in points:
		if point-np.mean(lane1) < 50:              #CAMBIE A 50... para no equivocarme y poner un solo carril.. pero ver que paso con eso
			lane1 += [point]
		else:
			lane2 += [point]

	print(lane1)
	print(lane2)
	return lane1, lane2
	

def poly_for_lane(lane,im):		#out_image es im
	
	x_base = int(np.mean(lane))
	nwindows = 12		#Number of sections for lane
	window_height = int((480-320)/nwindows)

	nonzero = im.nonzero()
	nonzeroy = np.array(nonzero[0])
	nonzerox = np.array(nonzero[1])
	
	margin = 30	
	minpix = 10
	x_current = x_base
	lane_inds = []
	
	for window in range(nwindows):
		win_y_low = binary_warped.shape[0] - (window+1)*window_height
		win_y_high = binary_warped.shape[0] - (window)*window_height
		win_x_low = x_current - margin
		win_x_high = x_current + margin
		cv2.rectangle(im,(win_x_low,win_y_low),(win_x_high,win_y_high), (0,255,0),2)
		
		good_inds = ((nonzeroy >= win_y_low)&(nonzeroy < win_y_high)&(nonzerox >= win_x_low)&(nonzerox < win_x_high)).nonzero()[0]

		lane_inds.append(good_inds)
		#plt.imshow(im)
		#plt.show()
	
		if len(good_inds) > minpix:
			x_current = np.int(np.mean(nonzerox[good_inds]))
		
	lane_inds = np.concatenate(lane_inds)

	lane_x = nonzerox[lane_inds]
	lane_y = nonzeroy[lane_inds]

	poly = np.polyfit(lane_y,lane_x,2)
	
	return poly


def center_lane_f2(xr,xl,y):
	
	y_c = np.zeros(480)
	x_c = np.zeros(480)

	for j in range(0,479):
		d = 70
		x_c[j] = (xr[j]+xl[j])/2
		y_c[j] = y[j]


	center_poly = np.polyfit(y_c,x_c,2)

	return center_poly

def center_lane_f1(x,y,s):

	y_c = np.zeros(480)
	x_c = np.zeros(480)
	d = 85
	#if (x[479]>x[0]):		#RIGHT LANE
	if (s == 2):
		for j in range(0,479):
			
			x_c[j] = x[j]-d
			y_c[j] = y[j]
	elif (s == 3):
		
		for j in range(0,479):
			x_c[j] = x[j]+d
			y_c[j] = y[j]
	
	center_poly = np.polyfit(y_c,x_c,2)


	return center_poly




#########################################################MAIN

start_time = time.time()
state=1
cv_image = cv2.imread('BE_Lane_data/Test/25_30_der.jpg')        
#REVISAR DE 104 a 110.. ahi muere
gray = cv2.cvtColor(cv_image,cv2.COLOR_BGR2GRAY) #Transformar y mostrar a escala de grises

kernelSize = 5
blur1 = cv2.GaussianBlur(gray,(kernelSize,kernelSize),0) #Eliminar Ruido



minThreshold = 120#120
maxThreshold = 200#200

#sobl = cv2.Sobel(blur1,cv2.CV_8U,dx=1,dy=0,ksize=3)   #Para volver a lo de antes quitar esta parte
edge = cv2.Canny(blur1,minThreshold,maxThreshold) #Detectar esquinas   ####MOD, me salte la etapa de quitar ruido 1


kernelSize = 5
blur2 = cv2.GaussianBlur(edge,(kernelSize,kernelSize),0) #Eliminar Ruido

#first = [0,0]    #ROI
lowerLeftPoint = [0, 480]
upperLeftPoint = [0,320]
upperRightPoint = [640,320]
lowerRightPoint = [640,480]
#last = [640,430]
pts = np.array([[lowerLeftPoint,upperLeftPoint,upperRightPoint,lowerRightPoint]], dtype=np.int32)
    
masked_image = region_of_interest(blur2,pts) ##Enmascarar area interesante 
    

################
pts1 = np.float32([[220,261],[389,264],[587,480],[29,480]])  #puntos obtenidos apartir de imagen prueba junto con mediciones
pts3 = np.float32([[260,190],[380,190],[380,480],[260,480]])
M_n = cv2.getPerspectiveTransform(pts1,pts3)


binary_warped = cv2.warpPerspective(masked_image,M_n,(640,480))  #Transformar la imagen a vista de ave, cada pixel corresponde a .25cm aprox
orig_warped = cv2.warpPerspective(cv_image,M_n,(640,480))


out_img = np.dstack((binary_warped, binary_warped, binary_warped))*255


lane1, lane2 = image_lanes(binary_warped)

#print('lane 1:')
#print(lane1)

#print('lane 2:')
#print(lane2)
	
	
if   ((lane1 != []) and (lane2 != [])):
	state = 1
elif ((lane1 != []) and (lane2 == []) and (state==1) and (np.mean(lane1)>320)):
	state = 2
elif ((lane1 != []) and (lane2 == []) and (state==1) and (np.mean(lane1)<320)):
	state = 3
elif ((lane1 != []) and (lane2 == []) and (state==2) ):
	state = 2
elif ((lane1 != []) and (lane2 == []) and (state==3) ):
	state = 3
elif ((lane1 == []) and (lane2 == [])):
	state = 4

if state == 1:
	#Utilizar los dos carriles para detectar error lateral
	left_fit = poly_for_lane(lane1,out_img)
	right_fit = poly_for_lane(lane2,out_img)
	
	ploty = np.linspace(0,binary_warped.shape[0]-1, binary_warped.shape[0])
	left_fitx = left_fit[0]*ploty**2+left_fit[1]*ploty+left_fit[2]
	right_fitx = right_fit[0]*ploty**2+right_fit[1]*ploty+right_fit[2]
	
	
	center_fit = center_lane_f2(right_fitx,left_fitx,ploty)

	center_fitx = center_fit[0]*ploty**2+center_fit[1]*ploty+center_fit[2]

	elapsed_time = time.time() - start_time
	print(elapsed_time)

	plt.imshow(orig_warped)
	plt.plot(left_fitx, ploty, color='green')
	plt.plot(right_fitx, ploty, color='green')
	plt.plot(center_fitx, ploty, color='yellow')
	plt.xlim(0,640)
	plt.ylim(480,320)
	plt.show()


	
elif state == 2:
	#Utilizar un carril para detectar error lateral
	poly_fit = poly_for_lane(lane1,out_img)
	ploty = np.linspace(0,binary_warped.shape[0]-1, binary_warped.shape[0])
	poly_fitx = poly_fit[0]*ploty**2+poly_fit[1]*ploty+poly_fit[2]

	center_fit =center_lane_f1(poly_fitx,ploty,state)	
	center_fitx = center_fit[0]*ploty**2+center_fit[1]*ploty+center_fit[2]
	
 	elapsed_time = time.time() - start_time
	print(elapsed_time)
	
	plt.imshow(orig_warped)
	plt.plot(poly_fitx, ploty, color='green')
	plt.plot(center_fitx, ploty, color='yellow')
	plt.xlim(0,640)
	plt.ylim(480,320)
	plt.show()
	
elif state == 3:
	#Utilizar un carril para detectar error lateral
	poly_fit = poly_for_lane(lane1,out_img)
	ploty = np.linspace(0,binary_warped.shape[0]-1, binary_warped.shape[0])
	poly_fitx = poly_fit[0]*ploty**2+poly_fit[1]*ploty+poly_fit[2]

	center_fit =center_lane_f1(poly_fitx,ploty,state)	
	center_fitx = center_fit[0]*ploty**2+center_fit[1]*ploty+center_fit[2]
	
        elapsed_time = time.time() - start_time
	print(elapsed_time)

	plt.imshow(orig_warped)
	plt.plot(poly_fitx, ploty, color='green')
	plt.plot(center_fitx, ploty, color='yellow')
	plt.xlim(0,640)
	plt.ylim(480,320)
	plt.show()



center_lane_pos = center_fit[0]*480**2+center_fit[1]*480+center_fit[2]

Le = (center_lane_pos-320)*.25

print("Lateral error= ", Le)





    



