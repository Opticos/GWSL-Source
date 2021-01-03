import subprocess


def start_service():
    """Starts the GWSL_service if not already running."""
    if not is_running("GWSL_service"):
        print("Starting GWSL service...")
        try:
            subprocess.Popen("GWSL_service.exe")
        except FileNotFoundError:
            raise ValueError("Cannot find GWSL_service.exe")


def is_running(process: str) -> bool:
    """Return true if the process is found in the running windows tasks."""
    proc_list = subprocess.getoutput(f'tasklist /NH /FI "IMAGENAME eq {process}"')
    return process in proc_list


def start_server(port, mode, clipboard):
    clp = "" if clipboard else "no"
    mode_map = {"multi": "-multiwindow", "full": "-fullscreen"}
    cmd = [
        "VCXSRV/GWSL_instance.exe",
        f":{port}",
        "-ac",
        "-wgl",
        "-compositewm",
        "-notrayicon",
        "-dpi",
        "auto",
        mode_map.get(mode, ""),
        f"-{clp}clibboard"
        f"-{clp}primery"
    ]
    return subprocess.Popen(cmd).pid


if __name__ == "__main__":
    start_service()
