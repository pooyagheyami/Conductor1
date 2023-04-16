#In the name of GOD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from pygame import mixer
from pygame.font import SysFont, Font

import cv2
import sys
import os

import mediapipe as mp

# a. states and counters
clock = pygame.time.Clock()
# timer events
TIC_EVENT = pygame.USEREVENT + 1
TIC_TIMER = 1000
with open('music1.txt', 'r') as f:
    lins = f.readlines()

    
#print(lins)
MUSICFILE = lins[0].replace('music = ','').replace('\n','')
SPEED     = int(lins[1].replace('speed = ', '').replace('\n',''))
PATERN    = eval(lins[2].replace('patern = ','').replace('\n',''))
#print(MUSICFILE,SPEED,PATERN)

def init():
    pygame.init()
    mixer.init()
    pygame.display.set_caption("Conductor Music Game")
    # Public Parameter
    camera = cv2.VideoCapture(0)
    screen = pygame.display.set_mode( (640,480) )
    pygame.font.init()
    ifont = SysFont('Calibri', 24)
    return camera, screen, ifont
    


def hand_dtct():
    mp_hand = mp.solutions.hands
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_draw = mp.solutions.drawing_utils
    hand_detection = mp_hand.Hands(model_complexity=0,min_detection_confidence=0.5)

    return hand_detection, mp_draw, mp_hand

    

def music():
    mixer.music.load(os.path.join(os.getcwd(),MUSICFILE))    #"heyyar.mp3")
    mixer.music.set_volume(0.7)
    

def surfinit():
    # Make a blue 24 x 24 circle
    blue_circ = pygame.Surface((48, 48))
    blue_circ.set_colorkey((0,0,0))
    pygame.draw.circle(blue_circ, (0, 0, 255), (19, 19), 19)

    circle_pos = [320, 240]  #pos_list_4[0]
    circle_speed = SPEED  #25
    next_pos_index = 0

    return blue_circ, circle_pos, circle_speed, next_pos_index


def move_circle(start_pos, end_pos, speed):
    circle_dir = pygame.math.Vector2(end_pos) - start_pos
    if circle_dir.length() < speed:
        end_pos = start_pos
        return -1
        
    else:
        circle_dir.scale_to_length(speed)
        new_pos = pygame.math.Vector2(start_pos) + circle_dir
        end_pos = (new_pos.x, new_pos.y)      
    return end_pos
    
def mv_Lft(pos, spd):
    spos = (40, 240)
    epos = (10, 240)
    return  move_circle(pos,epos, spd)
        
    
def mv_Rit(pos, spd):
    spos = (600, 240)
    epos = (630, 240)
    return move_circle(pos,epos, spd)

def mv_Dn(pos, spd):
    spos = (320, 440)
    epos = (320, 470)
    return  move_circle(pos,epos, spd)
        
    
def mv_Up(pos, spd):
    spos = (320, 40)
    epos = (320, 10)
    return move_circle(pos,epos, spd)

def chkindx(indx,ln):
    #print(indx, ln)
    if indx > ln-2:
        return 0
    else:
        return indx + 1
    

def app_loop(screen, camera,  myfont):
    clock = pygame.time.Clock()
    keepGo = True
    hand_d, mp_draw, mp_hand = hand_dtct()
    blue_circ, circle_pos, circle_speed, next_pos_index = surfinit()
    ptrn = PATERN #['Lft','Rit','Up','Dn','Lft','Rit','Up','Dn']
    indx = 0
    music()
    cx, cy = 0, 0
    score = 0
    txt_img = myfont.render(str(score), False, (255,0,0))
    #mixer.music.play()
    
    try:
        mixer.music.play()
        while keepGo:
            clock.tick(60)

            ret, frame = camera.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame.flags.writeable = False
            frame_height, frame_width, _ = frame.shape

            result2 = hand_d.process(frame)
            if result2.multi_hand_landmarks:
                for hand_lanmark in result2.multi_hand_landmarks:
                    for ids, landmark in enumerate(hand_lanmark.landmark):
                        #print(ids, landmark)
                        cx, cy = landmark.x * frame_width, landmark.y * frame_height
                        #print(cx,cy)
                    mp_draw.draw_landmarks(frame, hand_lanmark ,mp_hand.HAND_CONNECTIONS)
                    #print(hand_lanmark)
                
            frame = frame.swapaxes(0, 1)
            frame = cv2.flip(frame,0)


            pygame.surfarray.blit_array(screen, frame)
            
            #screen.blit(blue_circ, (round(circle_pos[0]), round(circle_pos[1])))
            if ptrn[indx] == 'Lft':               
                if mv_Lft(circle_pos, circle_speed) != -1:
                    circle_pos = mv_Lft(circle_pos, circle_speed)
                else:
                    indx = chkindx(indx, len(ptrn))
                       
            if ptrn[indx] == 'Rit':
                if mv_Rit(circle_pos, circle_speed) != -1:
                    circle_pos = mv_Rit(circle_pos, circle_speed)
                else:
                    indx = chkindx(indx, len(ptrn))

            if ptrn[indx] == 'Up':               
                if mv_Up(circle_pos, circle_speed) != -1:
                    circle_pos = mv_Up(circle_pos, circle_speed)
                else:
                    indx = chkindx(indx, len(ptrn))
                       
            if ptrn[indx] == 'Dn':
                if mv_Dn(circle_pos, circle_speed) != -1:
                    circle_pos = mv_Dn(circle_pos, circle_speed)
                else:
                    indx = chkindx(indx, len(ptrn))        

            #print(int(cx))
            if int( circle_pos[0] ) == int(cx):
                #print(score)
                score += 1
                txt_img = myfont.render(str(score), False, (255,0,0))
                screen.blit(txt_img,(10,10)) 
            if int( circle_pos[1] ) == int(cy):
                #print(score)
                score += 1
                txt_img = myfont.render(str(score), False, (255,0,0))
                screen.blit(txt_img,(10,10))
            screen.blit(blue_circ, (round(circle_pos[0]), round(circle_pos[1])))
            screen.blit(txt_img,(10,10))
  
            
            pygame.display.update()

            
            if not mixer.music.get_busy():
                print(score)
                keepGo = False


    except(KeyboardInterrupt, SystemExit):
        pygame.quit()
        cv2.destroyAllWindows()
        

            

def Allstop(camera):
    camera.release()
    cv2.destroyAllWindows()
    mixer.music.stop()
    

# the main function ====================
def main():
    camera, screen, ifont  = init()
    pygame.time.set_timer(TIC_EVENT, TIC_TIMER)
    
    app_loop(screen, camera, ifont)
    Allstop(camera)
    pygame.quit()
    #exit()


if __name__ == '__main__':
    main()
    
