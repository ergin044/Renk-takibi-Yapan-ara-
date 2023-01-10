import RPi.GPIO as GPIO
import time
import cv2
import imutils
import time
from imutils.video import VideoStream

red_low = (161, 155, 84) #kırmızı rengin max ve min HSV kodları
red_high = (179, 255, 255)

xc=0 #cismin : x-merkez 
yc=0 #  y-merkez

vs = VideoStream(usePiCamera=True).start() #pi kamerayı başlattık
time.sleep(2)#Gecikme

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#Motor pinleri tanıtılıyor
ena =17
in2 = 27
in1 = 22
in3 = 23 
in4 = 24
enb = 25

GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(in3,GPIO.OUT)
GPIO.setup(in4,GPIO.OUT)
GPIO.setup(ena,GPIO.OUT)
GPIO.setup(enb,GPIO.OUT)

GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
GPIO.output(in3,GPIO.LOW)
GPIO.output(in4,GPIO.LOW)
#Mesafe Sensörü pinleri
TRIG_PIN = 20
ECHO_PIN = 21

 
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

pwm1=GPIO.PWM(ena,100)

pwm2=GPIO.PWM(enb,100)

      
def ileri():
    pwm1.start(0)
    pwm2.start(0)
    pwm1.ChangeDutyCycle(30)#pwm özelliğini kullanarak motorlara %30 güç verdik
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.HIGH)
    
    pwm2.ChangeDutyCycle(30)
    GPIO.output(in3,GPIO.LOW)
    GPIO.output(in4,GPIO.HIGH)
def geri():
    pwm1.start(0)
    pwm2.start(0)
    pwm1.ChangeDutyCycle(30)
    GPIO.output(in1,GPIO.HIGH)
    GPIO.output(in2,GPIO.LOW)
    
    pwm2.ChangeDutyCycle(30)
    GPIO.output(in3,GPIO.HIGH)
    GPIO.output(in4,GPIO.LOW)
    
def sol():
    pwm1.start(0)
    pwm2.start(0)
    pwm1.ChangeDutyCycle(40)
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.HIGH)
    
    pwm2.ChangeDutyCycle(40)
    GPIO.output(in3,GPIO.HIGH)
    GPIO.output(in4,GPIO.LOW)
    
def sag():
    pwm1.start(0)
    pwm2.start(0)
    pwm1.ChangeDutyCycle(40)
    GPIO.output(in1,GPIO.HIGH)
    GPIO.output(in2,GPIO.LOW)
    
    pwm2.ChangeDutyCycle(40)
    GPIO.output(in3,GPIO.LOW)
    GPIO.output(in4,GPIO.HIGH)
    
    
def mesafe():
    
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
 
    while GPIO.input(ECHO_PIN) == 0:
        basla = time.time()
 
    while GPIO.input(ECHO_PIN) == 1:
        bitis = time.time()
 
    gecenZaman = bitis - basla
    mesafe = (gecenZaman * 34300) / 2
 
    return mesafe 

try:
    while True:
        m = mesafe()
        print ("Olculen mesafe = %.1f cm" % m)
        time.sleep(0.09)
        
        if m>11 and m<250:#nesne 11cm ve 250 cm aralığında ise kamera başlatılarak renk tespiti ve hareket kontrol edilir
            
            frame = vs.read() #kameradan okuma yapıyoruz
            frame = imutils.resize(frame, width=400) #önizleme ekranı oluşturduk

            if frame is None:
                break

            blurred = cv2.GaussianBlur(frame, (11, 11), 0) #görüntüyü sadeleştirmek için blur koyduk
            w, h = frame.shape[:2]
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) #görüntüyü HSV cinsine çevirdik
            mask = cv2.inRange(hsv, red_low, red_high) #HSV cinsinden tüm piksellerin renklerini kontrol ediyoruz
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            center = None

            if len(cnts) > 0:
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                xc=int(M["m10"] / M["m00"])
                yc=int(M["m01"] / M["m00"])
                center = (xc,yc)

                if radius > 10: #eğer kırmızı renk tespit edildiyse
                    cv2.rectangle(frame,(int(x-radius),int(y-radius)) , (int(x+radius),int(y+radius)), (0, 255, 255), 3)
            #cisme sarı çerçeve çizdik.
                    cv2.circle(frame, center, 5, (0, 0, 255), -1) #cismin merkezine kırmızı nokta koyduk

                    print(xc,yc)
                    #Araç ileri-sol-sağ hareketleri
                    if xc>0 and xc<130:
                        #sol
                        sol()
                        time.sleep(0.2)
                        pwm1.ChangeDutyCycle(0)
                        pwm2.ChangeDutyCycle(0)
                        pwm1.stop(0)
                        pwm2.stop(0)
                    elif xc>130 and xc<300:
                        #ileri
                        ileri()
                    elif xc>300:
                        #sag
                        sag()
                        time.sleep(0.2)
                        pwm1.ChangeDutyCycle(0)
                        pwm2.ChangeDutyCycle(0)
                        pwm1.stop(0)
                        pwm2.stop(0)
                    
                        
                        


    
            cv2.imshow("Frame", frame) #kapatmak için q tuşuna basın
            if cv2.waitKey(1) & 0xFF == ord('q'):
                    break    
           
        
        elif m<5:# mesafe 5 cm den küçükse araç geri hareket ettilirilir
            geri()
            time.sleep(0.5)
            pwm1.ChangeDutyCycle(0)
            pwm2.ChangeDutyCycle(0)
            pwm1.stop(0)
            pwm2.stop(0)
        else:
            print("burada")
            pwm1.ChangeDutyCycle(0)
            pwm2.ChangeDutyCycle(0)
            pwm1.stop(0)
            pwm2.stop(0)
        
           
        
        
        
        
       

    
except:
    GPIO.cleanup()
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    pwm1.stop(0)
    pwm2.stop(0)
    vs.release()
    cv2.destroyAllWindows() 
        
    
    
    
    
    
    
    



    
    
    
    
