import cv2
import numpy as np
import time
import math
import glob
import os
import image_process as img

def select_white(image, white):
    lower = np.uint8([white,white,white])
    upper = np.uint8([255,255,255])
    white_mask = cv2.inRange(image, lower, upper)
    return white_mask
    
def first_nonzero(arr, axis, invalid_val=-1):
    arr = np.flipud(arr)
    mask = arr!=0
    return np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)
    
def set_path3(image, forward_criteria):
    height, width = image.shape
    height = height-1
    width = width-1
    center=int(width/2)
    left=0
    right=width
    center = int((left+right)/2)       
    direction = 0

    #길 좌우 경계값 찾기
    try:      
        #맨 아랫줄, 왼쪽~센터, 다 흰색이면
        if image[height][:center].min(axis=0) == 255: 
            left = 0            
        #맨 아랫줄, 왼쪽~센터, 검은색이 하나라도 있다면
        else:
            #맨 아랫줄, 왼쪽~센터, 검은색, 가장 왼쪽의 위치   
            left = image[height][:center].argmin(axis=0) 
        #맨 아랫줄, 센터~오른쪽, 다 검은색이면
        if image[height][center:].max(axis=0) == 0:
            right = width
        #맨 아랫줄, 센터~오른쪽, 흰색이 하나라도 있다면    
        else:  
            #맨 아랫줄, 센터~오른쪽, 흰색, 가장 왼쪽의 위치  
            right = center+image[height][center:].argmax(axis=0)  
        
        #길의 중간값
        center = int((left+right)/2)  

        #가운데 직선의 가장 아래의 흰색
        forward = min(int(height),int(first_nonzero(image[:,center],0,height))-1)
        
        left_line = first_nonzero(image[height-forward:height,center:],1, width-center)
        right_line = first_nonzero(np.fliplr(image[height-forward:height,:center]),1, center)

        #left_coord = (center+1+left_line[i], 239-i) 실제 오른쪽
        #right_coord = (center+1-right_line[i], 239-i) 실제 왼쪽

        #기울기
        center_y = (np.ones(forward)*2*center-left_line+right_line)/2-center
        center_x = np.vstack((np.arange(forward), np.zeros(forward)))
        m, c = np.linalg.lstsq(center_x.T, center_y, rcond=-1)[0]
        
        #기울기 표시
        direction = ((int(width/2),height),(int(width/2)-int(forward*m),height-forward))

        #방향 결정
        if forward < 20 or forward < 50 and abs(m) < 0.35:
            action = 'x'
        elif abs(m) < forward_criteria:
            action = 'w'
        elif m > 0:
            action = 'q'
        else:
            action = 'e'
    except:
        action = 'x'
        m = 0
    
    return action, round(m,4), forward, left_line, right_line, center, direction



"""

if __name__ == "__main__":
    start_time=time.time()
    path = '*.jpg'
    file_list = glob.glob(path)
    cnt = 0
    for i in file_list:
        image = cv2.imread(i)
        #name, extension = os.path.splitext(os.path.basename(i))
        masked_image=select_white(image,160)
        result=set_path3(masked_image,0.25)

        
        #---cv2.line---

        line = []
        #오른쪽 라인        
        for j in range(result[2]):
            left_coord = (+result[5]+1+result[3][j], 239-j)
            line.append(left_coord)
            #masked_image = cv2.line(masked_image, left_coord, left_coord,(255,255,255), 5)
        #print(line)
        
        #왼쪽 라인
        for j in range(result[2]):
            right_coord = (result[5]+1-result[4][j], 239-j)
            line.append(right_coord)
            #masked_image = cv2.line(masked_image, right_coord, right_coord,(255,255,255), 5)
        #print(line)  

        #기울기
        try:
            masked_image = cv2.line(masked_image, result[6][0], result[6][1],(255,255,255), 5)
            print(result[6])
        except:
            pass

        print(result[0], result[1])
        
        
        cv2.imshow("video", masked_image)
        cv2.waitKey(0)        
    cv2.destroyAllWindows()
    #print('\nAvearage FPS:', round(len(file_list)/(time.time()-start_time),2), "Acurracy:", str(round(100*cnt/len(file_list), 2))+" %")
"""