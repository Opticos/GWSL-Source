import subprocess, time

subprocess.Popen("pulseaudio.exe", shell=True)

time.sleep(5)

print(subprocess.getoutput("taskkill /IM pulseaudio.exe /F"))
