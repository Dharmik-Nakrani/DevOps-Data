import pyautogui as pg
from time import sleep

pg.position()

sleep(5)
while True:
    pg.leftClick(x=3057, y=606)
    pg.write('proxy/firmware/new_version')
    sleep(1)
    pg.leftClick(x=3107, y=685)
    sleep(2)
    pg.leftClick(x=4427, y=473)
    sleep(1)
    pg.leftClick(x=3799, y=987)
    sleep(2)
    pg.leftClick(x=4424, y=471)
    sleep(1)

