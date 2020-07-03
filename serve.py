import http.server
import socketserver
from urllib.parse import urlparse
from urllib.parse import parse_qs
import json
import cgi
from get_bot_response import talk
from get_analytics_parse import gen_dep_parse, gen_pos_parse, gen_ner_parse
from gtts import gTTS 
language = 'hi'
import playsound
import os

def speak(tts_text):
    hi_tts = gTTS(text=tts_text, lang=language, slow=False) 
    hi_tts.save("voice.mp3") 
    playsound.playsound('voice.mp3', True)
    os.remove('voice.mp3')               


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        # read the message and convert it into a python dictionary
        length = int(self.headers['Content-Length'])

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        message = json.loads(self.rfile.read(length).decode('utf-8'))
        # add a property to the object, just to mess with data

        if self.path == '/get_reply':
            customer_txt = message['customer']

            try:
                response = talk(customer_txt)
            except:
                response = "क्षमा करें, आपको समझ नहीं सका। कृपया फिर से लिखे।"
            response = response.replace('\n','<br>')

            message['response'] = response
            
            # send the message back
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(message),encoding='utf8'))
            speak(response)

        if self.path == '/get_dep_parse':
            customer_txt = message['customer']

            response = gen_dep_parse(customer_txt)

            message['response'] = response
            
            # send the message back
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(message),encoding='utf8'))

        if self.path == '/get_pos_parse':
            customer_txt = message['customer']

            response = gen_pos_parse(customer_txt)

            message['response'] = response
            
            # send the message back
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(message),encoding='utf8'))

        if self.path == '/get_ner_parse':
            customer_txt = message['customer']

            response = gen_ner_parse(customer_txt)

            message['response'] = response
            
            # send the message back
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(message),encoding='utf8'))

    def do_GET(self):
        if self.path == '/':
            self.path = '/html/chat.html'
        if self.path == '/chat?':
            self.path = '/html/chat.html'
            

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 8000
my_server = socketserver.TCPServer(("", PORT), handler_object)

# Star the server
my_server.serve_forever()