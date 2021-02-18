import numpy as np
import cv2
from time import sleep


# TODO: automatizar processo de obtenção de região de interesse


class Diafragma(object):
    def __init__(self, window_name, videopath):
        self.window_name = window_name 
        self.cap = cv2.VideoCapture(videopath)
        self.coord_ini = (1,1)
        self.coord_end = (10,10)
        self.drawing = False
        self.volume = 0

        # cria documento registrando o volume acumulado em cada quadro
        with open("teste.csv", "w") as csvfile:
            csvfile.write("Volume"+","+"Frame"+"\n")
            csvfile.close()
    

    #####
    # Permite aumentar a imagem caso seja dificil ver/selecionar divisões do mostrador
    ###
    def zoom(self, img, scale_percent = 100):
        #scale_percent = 500 # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        zoom = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        return zoom
     

    #####
    # Método privado
    # Captura eventos do mouse e retorna pontos iniciais e finais região da seleção
    ###
    def _desenha(self, event,x,y,flags,param):
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
                
    
    #####
    # Seleção da area de interessse
    ###
    def regiao(self):
        cv2.namedWindow("selecao")
        cv2.setMouseCallback("selecao", self._desenha)
        
        _, frame = self.cap.read()
        while 1:
            frame_copy = self.zoom(frame, scale_percent = 100)
            cv2.rectangle(frame_copy,self.coord_ini,self.coord_end,(0,255,0),0)
            cv2.imshow("selecao",frame_copy)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break 
        cv2.destroyAllWindows()
 

    #####
    # Roda leitura do mostrador
    ###
    def run(self):
        contagem = -1
        conta = True
        quadro = 0
        nquadros  = 0
        while 1:
            ret, frame = self.cap.read()
            if ret == True:
                # aplica zoom
                frame_zoom = self.zoom(frame, scale_percent = 100)

                # desenha região de interesse no frame original
                frame = cv2.rectangle(frame, self.coord_ini, self.coord_end, (255,255,0), 1)

                # recorta regiao de interesse
                frame_crop = frame_zoom[self.coord_ini[1]:self.coord_end[1], self.coord_ini[0]:self.coord_end[0]]

                # preto e branco
                frame_gray = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2GRAY)

                # Binariza
                _,thr = cv2.threshold(frame_gray, 160,255,cv2.THRESH_BINARY)

                # Dilata
                kernel = np.ones((3,3), np.uint8)
                morph = cv2.dilate(thr, kernel, iterations=1)

                # identifica contornos e os desenha
                contours, hierarchy = cv2.findContours(morph, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(frame_crop, contours, -1, (0,255,0), 1)

                # identifica dimensões da região recortada
                z = frame_crop.shape[0]
                larg = frame_crop.shape[1]

                try:
                    # Identifica maior contorno  
                    ## se a area selecionada for adequada apenas um contorno deve estar presente por quadro
                    c = max(contours, key = cv2.contourArea)

                    ## Usa aproximaçao polinomial para traçar rentangulo mais estável em torno do contorno encontrado
                    # ver:  https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html
                    epsilon = 0.01*cv2.arcLength(c,True)
                    aprox = cv2.approxPolyDP(c,epsilon,True)
                    x,y,w,h = cv2.boundingRect(aprox)
                    cv2.rectangle(frame_crop,(x,y),(x+w,y+h),(255,255,0),1)

                    # Conta quando retangulo cruza centro da região de interesse
                    ## e essa condição e observada por dois quadros consecutivos
                    if y<z*0.5 and y+h>z*0.5 and conta == True:
                        nquadros += 1
                        if nquadros == 2:
                            contagem+=1
                            conta = False
                            nquadros = 0
                    elif y>z*0.5:
                        nquadros = 0
                        conta = True            
                except:
                    pass
                
                self.volume = round((contagem)*0.2, 2)

                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, str(round((contagem)*0.2, 2))+" litros", (15,round(z*7)), font, 1,(0, 0, 255), 1)
                cv2.line(frame_crop,(0,round(z*0.5)),(larg,round(z*0.5)),(255,0,0),1)
                

                cv2.imshow('original', frame)
                cv2.imshow('frame', frame_crop)
                
                # registra o volume acumulado em cada quadro
                quadro += 1
                with open("teste.csv", "a") as csvfile:
                    csvfile.write(str(self.volume)+","+str(quadro)+"\n")
                    csvfile.close()
                             
                k = cv2.waitKey(1) & 0xFF
                if k == 27 or k == 1:
                    break
            else:
                break

        
        self.cap.release()
        cv2.destroyAllWindows()
        return self.volume