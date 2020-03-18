# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 10:50:24 2020

@author: DataScience
"""

#import numpy as np
import cv2
import imutils
import requests
import json
import warnings
warnings.filterwarnings('ignore')
#peopleout,peoplein = 0,0

# Set ROI line1 for Confirming the Visitor
line1 = 300

#line2= 250

contours_previous = []
contours_now = []

fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

#fgmask = fgbg.apply(frame_empty)
width=1000
firstFrame= None


def post_req_in(peoplein):	
	    URL="http://nebula.digilogx.com/smart_retail/api/visitors.php"
	    code={
		'visitor_count':peoplein}
	    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	    req = requests.post(url = URL, data = json.dumps(code), headers = headers)
	    server_response = req.text
	    print(server_response)

cap = cv2.VideoCapture('rtsp://admin:ripplr@123@192.168.225.46:554') #Open video file
#cap = cv2.VideoCapture(0)

while(True):
		if not cap.isOpened():
			cap = cv2.VideoCapture('rtsp://admin:ripplr@123@192.168.225.46:554') #Open video file
#cap = cv2.VideoCapture(0))
		else:	

				ret, frame = cap.read()

				if not ret:
					print("[Info]: Camera connection is interupted,waiting for the camera to be online..............")
					cap.release()
					continue #read a frame  		
	    #cv2.waitKey(100)
	    #frame = imutils.resize(frame, width=width)    
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				gray = cv2.GaussianBlur(gray, (21, 21), 0)
			        #fgmask = fgbg.apply(frame) #Use the substractor
				if firstFrame is None:
				    firstFrame = gray
				    print(firstFrame.shape)
				    fgmask = fgbg.apply(firstFrame)
				    continue
				frameDelta = fgbg.apply(frame) #Use the substractor
				thresh = cv2.dilate(frameDelta, None, iterations=2)
		        #thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
		            
		        #thresh = cv2.dilate(fgmask, None, iterations=2)                  
				cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
				contours_now = []
				for c in cnts:
					if cv2.contourArea(c) < 15000:
					    continue
		                # compute the bounding box for the contour, draw it on the frame,
		                # and update the text
					(x, y, w, h) = cv2.boundingRect(c)
					cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
					contours_now.append([x,y])
		        
				if(len(contours_previous) == 0 ):
					contours_previous = contours_now 
					continue
		        
				closest_contour_list = []
		        
				for i in range(len(contours_now)):
					minimum = 1000000
		            
					for k in range(len(contours_previous)):
					    diff_x = contours_now[i][0] - contours_previous[k][0]
					    diff_y = contours_now[i][1] - contours_previous[k][1]
		                    
					    distance = diff_x * diff_x + diff_y * diff_y
		                
					    if(distance < minimum):
					        minimum =  distance
					        closest_contour = k
					closest_contour_list.append(closest_contour)
		            
				for i in range(len(contours_now)):
					x_previous = contours_previous[closest_contour_list[i]][0]
		            
					if( contours_now[i][0]<line1 and x_previous>=line1):
					   peoplein=0
					   peoplein = peoplein + 1 
					   print(peoplein)
					   post_req_in(peoplein)
		               
		            
		            #if((contours_now[i][0] > line1) and (x_previous <= line1)):
		               #peopleout = peopleout + 1
		            
				contours_previous = contours_now
		        
		        # Draw line
				cv2.line(frame,(line1,0),(line1,frame.shape[1]),(0,255,255),2)
		        
		        #cv2.line(frame,(line2,0),(line2,frame.shape[1]),(0,0,255),2)
		           
		        #cv2.putText(frame, "out: " + str(peopleout) ,(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
		        #cv2.putText(frame, "in: " + str(peoplein) ,(10,100),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)        
				cv2.imshow('Frame',frame)
		        
		        #Abort and exit with 'Q' or ESC
				k = cv2.waitKey(30) & 0xff
				if k == 27:
				    break            
	        
    
cap.release() #release video file
cv2.destroyAllWindows() #close all openCV windows
