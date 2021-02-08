import subprocess, time

subprocess.Popen("pulseaudio.exe")

while True:
    if input(":") == "kill":
        print("stopping")
        print(subprocess.getoutput("taskkill /IM pulseaudio.exe /F"))
