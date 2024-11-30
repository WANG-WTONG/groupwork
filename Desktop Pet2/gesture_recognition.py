# -*- coding: utf-8 -*-
import cv2
import numpy as np
import math

result = 'none'
close2 = 0

def opencv2_func():
    global result, close2
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    while True:
        if close2 == 1:
            break
            
        ret, frame = cap.read()
        if not ret:
            continue
            
        frame = cv2.flip(frame, 1)
        
        try:
            # 使用整个画面作为ROI
            roi = frame.copy()
            
            # 在hsv色彩空间内检测出皮肤
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            lower_skin = np.array([0,28,70], dtype=np.uint8)
            upper_skin = np.array([20,255,255], dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # 预处理
            kernel = np.ones((2,2), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=4)
            mask = cv2.GaussianBlur(mask, (5,5), 100)
            
            # 找出轮廓
            contours, h = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                result = 'none'
                cv2.putText(frame, result, (20,80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)
                cv2.imshow('frame', frame)
                continue
                
            # 从所有轮廓中找到最大的
            cnt = max(contours, key=lambda x: cv2.contourArea(x))
            areacnt = cv2.contourArea(cnt)
            
            # 获取凸包
            hull = cv2.convexHull(cnt)
            areahull = cv2.contourArea(hull)
            
            if areahull == 0:
                result = 'none'
                cv2.putText(frame, result, (20,80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)
                cv2.imshow('frame', frame)
                continue
                
            arearatio = areacnt/areahull
            
            # 获取凸缺陷
            hull = cv2.convexHull(cnt, returnPoints=False)
            defects = cv2.convexityDefects(cnt, hull)
            
            if defects is None:
                result = 'none'
                cv2.putText(frame, result, (20,80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)
                cv2.imshow('frame', frame)
                continue
                
            # 凸缺陷处理
            n = 0
            
            for i in range(defects.shape[0]):
                s,e,f,d = defects[i,0]
                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                far = tuple(cnt[f][0])
                
                a = math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
                b = math.sqrt((far[0]-start[0])**2 + (far[1]-start[1])**2)
                c = math.sqrt((end[0]-far[0])**2 + (end[1]-far[1])**2)
                
                if b*c == 0:
                    continue
                    
                angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57
                
                if angle <= 80 and d > 20:
                    n += 1
                    cv2.circle(roi, far, 3, [255,0,0], -1)
                cv2.line(roi, start, end, [0,255,0], 2)
            
            # 判断手势
            if n == 0:
                if arearatio > 0.9:
                    result = 'stone'
                else:
                    result = 'none'
            elif n == 1:
                result = 'scissors'
            elif n == 4:
                result = 'cloth'
            else:
                result = 'none'
                
            # 显示识别结果
            cv2.putText(frame, result, (20,80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)
            
            # 只在检测到有效手势时显示轮廓
            if result != 'none':
                try:
                    hull_draw = cv2.convexHull(cnt)  # 重新计算用于绘制的凸包
                    cv2.drawContours(frame, [cnt], -1, (0,255,0), 2)
                    cv2.drawContours(frame, [hull_draw], -1, (0,0,255), 2)
                except:
                    pass
                    
        except Exception as e:
            result = 'none'
            print(f"Error: {str(e)}")
            
        cv2.imshow('frame', frame)
        
        if cv2.waitKey(1) == 27:
            break
            
    cv2.destroyAllWindows()
    cap.release()

if __name__ == '__main__':
    opencv2_func()