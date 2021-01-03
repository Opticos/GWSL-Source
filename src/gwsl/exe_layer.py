from subprocess import PIPE, Popen
import subprocess
from threading import Thread
from queue import Queue, Empty


class Cmd:
    def __init__(self, command, console=False):
        self.read_queue = Queue()
        self.proc = None
        self.console = console
        self.q = []
        self.done = False
        self.error = False
        self.start(command, shell=console)

    def start(self, command, shell=False):
        if shell:
            p = Popen(command, bufsize=1, universal_newlines=True)
            return

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
            universal_newlines=True,
        )

        stdout_listener = Thread(
            target=listener, args=[self.proc.stdout, self.read_queue]
        )
        stdout_listener.daemon = True
        stdout_listener.start()

        stderr_listener = Thread(
            target=listener, args=[self.proc.stderr, self.read_queue]
        )
        stderr_listener.daemon = True
        stderr_listener.start()

        queue = Thread(target=self.active_listener, args=[])
        queue.daemon = True
        queue.start()

    def active_listener(self):
        while True:
            try:
                line = self.read_queue.get_nowait().lower()
            except Empty:
                continue
            if "fatal error" in line:
                self.error = True
                self.kill()
            if "exit" in line or "done" in line:
                removes = [i for i in self.q if i.lower() in line]
                for j in removes:
                    self.q.remove(j)
            if not self.q:
                self.done = True

    def kill(self):
        self.proc.kill()

    def run(self, command, wait=False, ident=None):
        if self.proc is None or self.console:
            return
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


def listener(out, queue):
    for line in iter(out.readline, b""):
        queue.put(line)
    out.close()
