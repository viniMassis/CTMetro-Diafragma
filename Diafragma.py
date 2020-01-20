import numpy as np
import cv2

# TODO: implementar condição de início de contagem 
# TODO: automatizar processo de obtenção de região de interesse


class Diafragma(object):
    def __init__(self, window_name, videopath):
        self.window_name = window_name # Name for our window
        self.cap = cv2.VideoCapture(videopath)
        self.coord_ini = (1,1)
        self.coord_end = (10,10)
        self.drawing = False
        self.volume = 0
        with open("teste.csv", "w") as csvfile:
            #for d in p.dados:
            csvfile.write("Volume"+","+"Frame"+"\n")
            csvfile.close()
        
    def zoom(self, img, scale_percent = 100):
        #scale_percent = 500 # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        zoom = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        return zoom
     
    def desenha(self, event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.coord_ini = (x,y)
            self.coord_end = (x,y)
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing == True:
                self.coord_end = (x,y)       
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.coord_end = (x,y)
            if self.coord_end[0]<self.coord_ini[0]:
                xini, yini = self.coord_ini
                xend, yend = self.coord_end
                self.coord_ini = (xend,yini) 
                self.coord_end = (xini, yend)            
            if self.coord_end[1]<self.coord_ini[1]:
                xini, yini = self.coord_ini
                xend, yend = self.coord_end
                self.coord_ini = (xini, yend)
                self.coord_end = (xend, yini)
                
    
    # Seleção area de interessse:
    def regiao(self):
        cv2.namedWindow("selecao")
        cv2.setMouseCallback("selecao", self.desenha)
        
        _, frame = self.cap.read()
        while 1:
            frame_copy = self.zoom(frame, scale_percent = 600)
            #frame_copy = frame.copy()
            cv2.rectangle(frame_copy,self.coord_ini,self.coord_end,(0,255,0),0)
            cv2.imshow("selecao",frame_copy)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break 
        cv2.destroyAllWindows()
 
    def run(self, volumemaximo):
        contagem = 0
        conta = True
        quadro = 0
        while 1:
            ret, frame = self.cap.read()
            if ret == True:
                frame_zoom = self.zoom(frame, scale_percent = 600)
                frame_crop = frame_zoom[self.coord_ini[1]:self.coord_end[1], self.coord_ini[0]:self.coord_end[0]]
                frame_gray = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2GRAY)
                #sub = cv2.subtract(frame_gray, background)
                sub = frame_gray.copy()
                _,thr = cv2.threshold(sub, 160,255,cv2.THRESH_BINARY)
                kernel = np.ones((3,3), np.uint8)
                morph = cv2.dilate(thr, kernel, iterations=10)
                im2, contours, hierarchy = cv2.findContours(morph, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(frame_crop, contours, -1, (0,255,0), 3)
                z = frame_crop.shape[0]/4
                larg = frame_crop.shape[1]
                try:
                    c = max(contours, key = cv2.contourArea)
                    epsilon = 0.01*cv2.arcLength(c,True)
                    aprox = cv2.approxPolyDP(c,epsilon,True)
                    #cv2.drawContours(frame_crop, [aprox], -1, (0,255,0), 3)
                    x,y,w,h = cv2.boundingRect(aprox)
                    cv2.rectangle(frame_crop,(x,y),(x+w,y+h),(255,255,0),2)

                    if y<z and y+h>z*0.75 and conta == True:
                        contagem+=1
                        conta = False   
                    elif y>z:
                        conta = True            
                except:
                    pass
                self.volume = round((contagem-1)*0.2, 2)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, str(round((contagem-1)*0.2, 2))+" litros", (5,round(z*3)), font, 1,(0, 0, 255), 1)
                cv2.line(frame_crop,(0,round(z)),(larg,round(z)),(0,0,255),2)
                cv2.line(frame_crop,(0,round(z*0.75)),(larg,round(z*0.75)),(0,0,255),2)

                cv2.imshow('original', frame)
                #cv2.imshow('frame', frame_crop)
                
                quadro += 1
                with open("teste.csv", "a") as csvfile:
                    #for d in p.dados:
                    csvfile.write(str(self.volume)+","+str(quadro)+"\n")
                    csvfile.close()
                
                if self.volume >= volumemaximo:
                    break               
                
                k = cv2.waitKey(1) & 0xFF
                if k == 27 or k == 1:
                    break 
            else:
                break
        
        print(quadro/30)
        self.cap.release()
        cv2.destroyAllWindows()
        return False