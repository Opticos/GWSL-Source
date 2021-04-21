import subprocess, time, sys




def kill_audio():
    print(subprocess.getoutput("taskkill /IM pulseaudio.exe /F"))
    try:
        print(subprocess.getoutput(r"del %USERPROFILE%\.pulse\%USERDOMAIN%-runtime\pid /q"))
    except:
        pass
    try:
        print(subprocess.getoutput(r"del %USERPROFILE%\.pulse\%COMPUTERNAME%-runtime\pid /q"))
    except:
        pass

def start_audio():
    proc = subprocess.Popen("pulseaudio.exe --cleanup-shm", shell=True)
    proc = subprocess.Popen("pulseaudio.exe -D", shell=True)
    audio_server_PID = proc.pid

kill_audio()
start_audio()

for i in range(20):
    time.sleep(1)
    print(20-i)
    #service_name = subprocess.getoutput(f'tasklist /nh /fo csv /FI "PID eq {audio_server_PID}"').split(",")[0]

    service_name = subprocess.getoutput(f'tasklist /nh /fo csv /FI "IMAGENAME eq pulseaudio.exe"').split(",")[0]

    print(service_name)
    """
    if input(":") == "kill":
        print("stopping")
        print(subprocess.getoutput(f'taskkill /F /pid {audio_server_PID}'))
        print(subprocess.getoutput("taskkill /IM pulseaudio.exe /F"))
        sys.exit()
    else:
        print(subprocess.getoutput("pulseaudio.exe --check"))"""

kill_audio()
