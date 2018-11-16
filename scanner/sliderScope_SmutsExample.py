import sliderScope
import time

#sliderScope.initSlider()
example = sliderScope.sliderObject()
#sliderScope.enableUDP = True

while True:
    #time.sleep(0.5)
    example.sliderRunner()
    print(example.sliderValue)

