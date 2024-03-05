import serial
import math
import global_vars
import queue

distance_mode_map = [400, 300, 200, 100, 50]

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
    


def start_lidar_distance(haptic, distance_mode):
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
        # off_counter = 500
        on_counter = 0
        counter_average_len = 5
        counter_average = [0]*counter_average_len

        while True:
            # print("Current distance mode: " + str(distance_mode.value))
            loopFlag = True
            flag2c = False

            if(i % 40 == 39):
                on_counter = 0
                # off_counter = 0
                # print(distances)
                for dist in distances:
                    if (dist*10 > 50 and dist*10 <= distance_mode_map[distance_mode.value]):
                    #     off_counter += 1 if (off_counter <= 500) else 0
                    # else:
                        # print("Dist: " + str(dist*10))
                        on_counter += 1 if (on_counter <= 100) else 0
                # print(on_counter)
                counter_average.append(on_counter)
                counter_average.pop(0)
                print(str(on_counter) + " average: " + str(sum(counter_average)/counter_average_len))

                
                
                    
                # print("off_counter: ", off_counter)
                # if(on_counter > 35):
                if(sum(counter_average)/counter_average_len > 35):
                    haptic.value = 1
                else:
                    
                    haptic.value = 0 
                # elif(on_counter > 5):
                #     haptic.value = 1

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