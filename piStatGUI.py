# Python driver for the test app

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.uix.slider import Slider
from kivy.clock import Clock
from functools import partial
import paho.mqtt.client as mqtt
import time


# Custom sliders
class LowSlider(Slider):
    limit = ObjectProperty()
class HiSlider(Slider):
    limit = ObjectProperty()

## Custom labeled sliders
# Labelled Slider BoxLayout implementation
class LabelledHiSlider(BoxLayout):
    # Limited Slider attributes that can be set by parents
    slider_barLimitPos = ObjectProperty()
    slider_currentPos = ObjectProperty()
    slider_value = NumericProperty()
# Labelled Slider BoxLayout implementation
class LabelledLowSlider(BoxLayout):
    # Limited Slider attributes that can be set by parents
    slider_barLimitPos = ObjectProperty()
    slider_currentPos = ObjectProperty()
    slider_value = NumericProperty()


## Zone control frame implementation
class ZoneControlFrame(BoxLayout):
    hiLimit = NumericProperty()
    lowLimit = NumericProperty()
    zone = StringProperty()
    currentTemp = StringProperty()

    def __init__(self, **kwargs):
        super(ZoneControlFrame, self).__init__(**kwargs)
        hiWidget = self.ids.hi
        lowWidget = self.ids.low
        lowWidget.ids.setting.bind(value = self.setLow)
        hiWidget.ids.setting.bind(value = self.setHi)
        self.currentTemp = 'Initializing...'
        Clock.schedule_once(partial(self.get_temperature, 'Living Room 1'), 1)
        Clock.schedule_interval(partial(self.get_temperature, 'Living Room 1'), 61)

    # MQTT protocols to fetch and set temperatures
    def get_temperature(self, zone, *largs):
        def on_message(client, userdata, msg):
            # print('Message received: '+msg.payload.decode('utf8'))
            self.currentTemp = str(float(msg.payload.decode('utf8')) * 1.8 + 32) + ' \N{DEGREE SIGN}F'
        def on_connect(client, userdata, flags, result_code):
            if result_code != 0:
                print('connection refused: '+ str(result_code))
#                return 'Bad CONNACK: '+str(result_code)
#            else:
#                print('connection successful')
        client = mqtt.Client('pistat')
        client.username_pw_set('fxxjapah','V3NDQTRepO6C')
        client.on_message = on_message
        client.on_connect = on_connect
        client.connect("m11.cloudmqtt.com", port = 13489, keepalive = 60)
        client.loop_start()
#        time.sleep(1)
        client.subscribe('rasqi/thermostat/'+zone)
        time.sleep(.5)
        client.disconnect()
        client.loop_stop()

    # Limits the sliders to their respective limit
    def setLow(self,instance,value):
        if self.lowLimit > (self.hiLimit-2):
            self.lowLimit = (self.hiLimit-2)
            instance.value = (self.hiLimit-2)
    def setHi(self,instance,value):
        if self.hiLimit < (self.lowLimit+2):
            self.hiLimit = (self.lowLimit+2)
            instance.value = (self.lowLimit+2)


class piStatGUI(App):
    pass


if __name__ == '__main__':
    piStatGUI().run()
