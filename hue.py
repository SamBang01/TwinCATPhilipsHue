import pyads
import cv2
import numpy as np
from ctypes import sizeof
import colorsys
from skimage import io

def rgb2xyb(r,g,b):
        r = ((r+0.055)/1.055)**2.4 if r > 0.04045 else r/12.92
        g = ((g+0.055)/1.055)**2.4 if g > 0.04045 else g/12.92
        b = ((b+0.055)/1.055)**2.4 if b > 0.04045 else b/12.92

        X = r * 0.4124 + g * 0.3576 + b * 0.1805
        Y = r * 0.2126 + g * 0.7152 + b * 0.0722
        Z = r * 0.0193 + g * 0.1192 + b * 0.9505

        return X / (X + Y + Z), Y / (X + Y + Z), int(Y*254)

f = open("ads.config" , "r")

ads_net_id= f.read()
plc=pyads.Connection(ads_net_id,pyads.PORT_TC3PLC1)
print('Connecting to TwinCAT PLC..')
plc.open()
print('Current connection status:',plc.is_open)
print('Current Status:',plc.read_state())
  
# define a video capture object
vid = cv2.VideoCapture(0)
  
while(True):
      
    # Capture the video frame
    # by frame
    ret, frame = vid.read()

    #Compute the average color
    average_color_row = np.average(frame, axis=0)
    average_color = np.average(average_color_row, axis=0)
    print(average_color)
  
    # Display the resulting frame
    cv2.imshow('frame', frame)

    #Turn the average color into a percentage
    average_color = average_color /255
    print(average_color)

    #Compute the X and Y values for the HUE lights
    xyArray = rgb2xyb(average_color[2], average_color[1], average_color[0])
    print(xyArray)
    
    #Write the values to the plc
    print('Writing Values..')
    plc.write_by_name(data_name='MAIN.x',value=xyArray[0],plc_datatype=pyads.PLCTYPE_LREAL)
    plc.write_by_name(data_name='MAIN.y',value=xyArray[1],plc_datatype=pyads.PLCTYPE_LREAL)
    plc.write_by_name(data_name='MAIN.nBrightness',value=100,plc_datatype=pyads.PLCTYPE_UINT)

    print('Reading Values..')
    x=plc.read_by_name(data_name='MAIN.x',plc_datatype=pyads.PLCTYPE_LREAL)
    y=plc.read_by_name(data_name='MAIN.y',plc_datatype=pyads.PLCTYPE_LREAL)
    bri=plc.read_by_name(data_name='MAIN.nBrightness',plc_datatype=pyads.PLCTYPE_UINT)
    print('MAIN.x is',x)
    print('MAIN.y is',y)
    print('MAIN.nBrightness is',bri)
      
    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()

print('Closing the Connections..')
plc.close()
print('Current Status:',plc.is_open)

