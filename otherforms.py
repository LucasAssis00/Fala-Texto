"""
import pyautogui
#resolution
print(pyautogui.size())
print(".")
#posição atualcursor
x, y = pyautogui.position()
print(x, y)
#cursor na tela?
#print(pyautogui.onScreen(-x, y))

pyautogui.moveTo(100,500, 2)

pyautogui.moveRel(500,200, 1)


import pyautogui
import time

time.sleep(1)


# Open edge
pyautogui.click(32,95)
time.sleep(1)
pyautogui.click(419,79)
pyautogui.write('https://docs.google.com/forms/d/1pk4Ecrw7ySOo1opqXJTxhD0ZUccttjQ8cFyeE1VP1Hw/viewform?edit_requested=true#response=ACYDBNgZyL-VrktsjYq2sr_DleYU2AYEnLbygvdITjWrWfx-GkNMYWjW7jbRk7xUOzbI69o')
pyautogui.press('enter')
time.sleep(2)  # Wait for Chrome to open
x, y = pyautogui.position()
print(x)
print(y)


import pyautogui
import time
import subprocess

# Open default web browser (works on Linux)
subprocess.Popen(["msedge", "https://facebook.com"])
time.sleep(2)  # Wait for the browser to open

# Interact with web elements as before
# For example:
# Click on the text box to focus it
pyautogui.click(x=500, y=300)  # Adjust coordinates based on your screen resolution and webpage layout

# Type the name "John Doe"
pyautogui.write('John Doe')
"""

import pyautogui
import time

#time.sleep(1)
#x, y = pyautogui.position()
#print(x, y)

pyautogui.moveTo(17, 402, duration=1)  
pyautogui.click()
pyautogui.moveTo(749, 79, duration=2)
pyautogui.click()
pyautogui.write('https://docs.google.com/forms/d/1pk4Ecrw7ySOo1opqXJTxhD0ZUccttjQ8cFyeE1VP1Hw/viewform?edit_requested=true#response=ACYDBNgZyL-VrktsjYq2sr_DleYU2AYEnLbygvdITjWrWfx-GkNMYWjW7jbRk7xUOzbI69o')
pyautogui.press('enter')
#752 338
pyautogui.moveTo(752, 338, duration=1)
pyautogui.click()
pyautogui.write('oi')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiiiiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiiiiiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiiiiiiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiiiiiiiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiiiiiiiiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiiiiiiiiiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiiiiiiiiiiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiiiiiiiiiiiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.write('oiiiiiiiiiiiiii')
pyautogui.press('tab')
time.sleep(1)
pyautogui.press('enter')
#time.sleep(1)

