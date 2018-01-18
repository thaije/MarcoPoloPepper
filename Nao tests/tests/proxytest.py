import naoqi
ip = "192.168.1.143"
port = 9559
# t o d e f i n e a proxy , u se ALProxy , p a s si n g the name o f the proxy , i p and p o r t
tts = naoqi.ALProxy ( "ALTextToSpeech" , ip , port )
tts.say ("How you doing")
