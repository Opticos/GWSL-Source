# import time
# import os
import subprocess
from queue import Queue, Empty
from subprocess import PIPE, Popen
from threading import Thread


class Cmd:
    def __init__(self, command, console=False):
        self.proc = None
        self.console = console
        self.q = []
        self.done = False
        self.error = False
        if not console:
            self.start(command, shell=False)
        else:
            self.start(command, shell=True)

    def start(self, command, shell=False):
        if not shell:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            self.proc = Popen(
                command,
                stdout=PIPE,
                stdin=PIPE,
                stderr=PIPE,
                bufsize=1,
                startupinfo=startupinfo,
                universal_newlines=True)

            def listener(out, newqueue):
                for line in iter(out.readline, b''):
                    newqueue.put(line)
                out.close()

            def active_listener():
                while True:
                    try:
                        line = read_queue.get_nowait()
                    except Empty:
                        pass
                    else:
                        if line != "":
                            pass  # print(line)
                        if "fatal error" in line.lower():
                            self.error = True
                            self.kill()
                        if "exit" in line.lower() or "done" in line.lower():
                            for i in self.q:
                                removes = []
                                if i.lower() in line.lower():
                                    removes.append(i)
                                for i in removes:
                                    self.q.remove(i)
                        if len(self.q) == 0:
                            self.done = True

            read_queue = Queue()
            stdout_listener = Thread(
                target=listener, args=[
                    self.proc.stdout, read_queue])
            stdout_listener.daemon = True
            stdout_listener.start()

            stderr_listener = Thread(
                target=listener, args=[
                    self.proc.stderr, read_queue])
            stderr_listener.daemon = True
            stderr_listener.start()

            queue = Thread(target=active_listener, args=[])
            queue.daemon = True
            queue.start()

        else:
            pass

            # print(p.pid)
            # while True:
            #    running = get_running("GWSL_plink.exe")
            #    if running == True:
            #        time.sleep(1)
            #    else:
            #        break

    def kill(self):
        self.proc.kill()

    def run(self, command, wait=False, ident=None):
        if self.proc is not None and self.console is False:
            if wait:
                command += " &"
            if " " in command:
                commands = command.split(" ")
                for c in commands:
                    self.proc.stdin.write(c + " ")
                self.proc.stdin.write("\n")

            else:
                self.proc.stdin.write(command + " \n")

            if wait:
                self.q.append(ident)
                self.proc.stdin.write("wait \n")
