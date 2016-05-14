import cv2
import numpy as np
import time

capture = cv2.VideoCapture(0)
capture.set(15, -4) #set exposure
capture.set(5, 20) #set max fps
capture.set(3, 640) #set videostream width
capture.set(4, 480) #set videostream height
COLOR_MAX = np.array([180, 255, 255], np.uint8)

def draw_HUD(img, x, y, w, h, fps):
	cv2.line(img, (x, y), (319, 239), (0, 255, 0), 2)
	cv2.rectangle(img, (0, 0), (120, 48), (255, 255, 255), 2)
	cv2.rectangle(img, (580, 0), (638, 40), (255, 255, 255), 2)
	target_center_x = x
	target_center_y = (y + y + h) / 2
	displacement_x = 319 - target_center_x
	displacement_y = 239 - target_center_y
	text = "<%d, %d>" % (displacement_x, displacement_y)
	cv2.putText(img, "%s" % text, (2, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
	cv2.putText(img, "FPS: %s" % fps, (582, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))

def main():
	h = 160
	s = 50
	v = 50
	initial_time = time.time()
	total_frames = 0
	times = [time.time()]

	while True:
		ret, img = capture.read()

		total_frames += 1
		times.append(time.time())
		if len(times) > 10:
			times.pop(0)
		fps = (int)(1.0 / (times[-1] - times[-2]))

		flipped_img = cv2.flip(img, 1)
		COLOR_MIN = np.array([h, s, v], np.uint8)
		hsv_img = cv2.cvtColor(flipped_img, cv2.COLOR_BGR2HSV)
		threshold = cv2.inRange(hsv_img, COLOR_MIN, COLOR_MAX)

		areaArray = []
		contours, heirarchy = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

		if len(contours) != 0:
			for i, c in enumerate(contours):
				area = cv2.contourArea(c)
				areaArray.append(area)

			sortedData = sorted(zip(areaArray, contours), key=lambda x: x[0], reverse = True)
			largestContour = sortedData[0][1]

			epsilon = 0.012 * cv2.arcLength(largestContour, True)
			approx = cv2.approxPolyDP(largestContour, epsilon, True)

			extLeft = tuple(approx[approx[:, :, 0].argmin()][0])
			extRight = tuple(approx[approx[:, :, 0].argmax()][0])
			extTop = tuple(approx[approx[:, :, 1].argmin()][0])
			extBottom = tuple(approx[approx[:, :, 1].argmax()][0])
			
			x = extLeft[0]
			y = extTop[1]
			w = extRight[0] - x
			height = y - extBottom[1]
			draw_HUD(flipped_img, x, y, w, height, fps)

			cv2.drawContours(flipped_img, [approx], -1, (255, 255, 0), 2)

			cv2.imshow('tyr-vision', flipped_img)
		else :
			print 'Nothing found. '
			cv2.imshow('tyr-vision', flipped_img)


		key = cv2.waitKey(30) & 0xff
		if key == 27:
			break
		elif key == ord('w'):
			h += 1
		elif key == ord('s'):
			h -= 1
		elif key == ord('a'):
			s += 1
		elif key == ord('d'):
			s -= 1
		elif key == ord('1'):
			v -= 1
		elif key == ord('2'):
			v += 1
		
		print "H value: %d" % h 
		print "S value: %d" % s
		print "V value: %d" % v
	capture.release()
	cv2.destroyAllWindows()

if __name__ == '__main__':
	main()