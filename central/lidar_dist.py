import serial
import math
import global_vars
import queue


class LidarData:
    def __init__(self,FSA,LSA,CS,Speed,TimeStamp,Confidence_i,Angle_i,Distance_i):
        self.FSA = FSA
        self.LSA = LSA
        self.CS = CS
        self.Speed = Speed
        self.TimeStamp = TimeStamp

        self.Confidence_i = Confidence_i
        self.Angle_i = Angle_i
        self.Distance_i = Distance_i



def CalcLidarData(str):
    str = str.replace(' ','')

    Speed = int(str[2:4]+str[0:2],16)/100
    FSA = float(int(str[6:8]+str[4:6],16))/100
    LSA = float(int(str[-8:-6]+str[-10:-8],16))/100
    TimeStamp = int(str[-4:-2]+str[-6:-4],16)
    CS = int(str[-2:],16)

    Confidence_i = list()
    Angle_i = list()
    Distance_i = list()
    count = 0
    if(LSA-FSA > 0):
        angleStep = float(LSA-FSA)/(12)
    else:
        angleStep = float((LSA+360)-FSA)/(12)
    
    counter = 0
    circle = lambda deg : deg - 360 if deg >= 360 else deg
    for i in range(0,6*12,6): 
        Distance_i.append(int(str[8+i+2:8+i+4] + str[8+i:8+i+2],16)/100)
        Confidence_i.append(int(str[8+i+4:8+i+6],16))
        Angle_i.append(circle(angleStep*counter+FSA)*math.pi/180.0)
        counter += 1
    

    lidarData = LidarData(FSA,LSA,CS,Speed,TimeStamp,Confidence_i,Angle_i,Distance_i)
    return lidarData
    


def start_lidar_distance(haptic):
    try:
        ser = serial.Serial(port='/dev/ttyUSB0',
                        baudrate=230400,
                        timeout=5.0,
                        bytesize=8,
                        parity='N',
                        stopbits=1)
        ser.flushInput()
        ser.flushOutput()
        tmpString = ""
        angles = list()
        distances = list()
        i = 0
        off_counter = 500

        while True:
            loopFlag = True
            flag2c = False

            if(i % 40 == 39):
                for dist in distances:
                    if not(dist*10 > 20 and dist*10 <= 150):
                        off_counter += 1 if (off_counter <= 500) else 0
                    else:
                        off_counter = 0
                
                # print("off_counter: ", off_counter)
                haptic.value = 0 if (off_counter > 150) else 1

                angles.clear()
                distances.clear()
                i = 0

            while loopFlag:
                b = ser.read()
                tmpInt = int.from_bytes(b, 'big')
                
                if (tmpInt == 0x54):
                    tmpString +=  b.hex()+" "
                    flag2c = True
                    continue
                
                elif(tmpInt == 0x2c and flag2c):
                    tmpString += b.hex()

                    if(not len(tmpString[0:-5].replace(' ','')) == 90 ):
                        tmpString = ""
                        loopFlag = False
                        flag2c = False
                        continue

                    lidarData = CalcLidarData(tmpString[0:-5])
                    # lidarData.Angle_i = [180*angle/math.pi for angle in lidarData.Angle_i]
                    # print(str(lidarData.Angle_i[0]) + ":::" + str(lidarData.Distance_i[0]))
                    

                    # if in between +40 degrees and -40 degrees (320 degrees), then analyze distance
                    current_angle = 180*lidarData.Angle_i[0]/math.pi

                    if (current_angle <= 50 or current_angle >= 310):
                        angles.extend(lidarData.Angle_i)
                        distances.extend(lidarData.Distance_i)

                        
                    tmpString = ""
                    loopFlag = False
                else:
                    tmpString += b.hex()+" "
                
                flag2c = False
            
            i +=1

        ser.close()
    except KeyboardInterrupt:
        print("Lidar Killed")



# Main program logic follows:
#This section won't be running during the thread
if __name__ == '__main__':
    start_lidar_distance()