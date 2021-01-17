import time
import random
import datetime

from collections import deque
import threading

from dearpygui.core import log, log_info, log_error,log_warning, is_dearpygui_running


data_names = ["accx", "accy", "accz", "can1buff", "can2buff", "serialbuff"]


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


class serial_interface():
    def __init__(self, port, baudrate, maxlen=100, log_window="", raw_log_window="") -> None:
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.maxlen = maxlen
        self.log_window = log_window
        self.raw_log_window = raw_log_window
        self.data = {"plots": {},
                     "raw": deque([], maxlen=5000),
                     "messages": deque([], maxlen=500),
                     "errors": deque([], maxlen=500),
                     "warnings": deque([], maxlen=500)}

        self.buff = []
        self.running = True
        
        log_info(f"Starting serial interface at {port} with baud {baudrate}", logger=self.log_window)
        self.serial_listener_thread = self.serial_listener()
        
        log_info(f"serial interface started", logger=self.log_window)

    def close(self):
        self.running = False
        self.serial_listener_thread.join()

    def parse_point(self, s: str):
        t = time.time()
        t_str = time.strftime("%T", time.localtime(t))

        s = s.strip()
        raw_str = f"{t_str}: {s}"
        if(self.raw_log_window!=""):
            log(raw_str, logger=self.raw_log_window)
        self.data["raw"].append(raw_str)
        if s[0] == "#":
            # parse as a number
            a = s.strip("#;")
            a = a.split(":")
            name = a[0]
            val = float(a[1])
            if name in self.data["plots"]:
                if len(self.data["plots"][name]["x"]) >= self.maxlen:
                    self.data["plots"][name]["x"].pop(0)
                    self.data["plots"][name]["t"].pop(0)
                self.data["plots"][name]["x"].append(val)
                self.data["plots"][name]["t"].append(t)
            else:
                self.data["plots"][name] = {"x": (self.maxlen-1)*[0.]+[val],
                                            "t": self.maxlen*[t]}

        elif s[0] == "!":
            # parse as error
            error_msg = f"{t_str}: {s.strip('!;')}"
            log_error(error_msg, logger=self.log_window)
            self.data["errors"].append(error_msg)

        elif s[0] == "?":
            # parse as warning
            warning_msg = f"{t_str}: {s.strip('?;')}"
            log_warning(warning_msg,logger=self.log_window)
            self.data["warnings"].append(warning_msg)

        else:
            info_msg = f"{t_str}: {s.strip(';')}"
            log_info(info_msg,logger=self.log_window)
            self.data["messages"].append(info_msg)

    @threaded
    def serial_listener(self):
        # generate som erandom data
        while self.running and is_dearpygui_running():
            i = random.randint(0, len(data_names)-1)
            a = data_names[i]
            if i > 2:
                b = random.randint(0, 20)
            else:
                b = random.uniform(-2, 2)

            self.parse_point(f"#{a}:{b};\r\n")
            self.parse_point(self.get_random_msg())
            self.parse_point(self.get_random_error())
            self.parse_point(self.get_random_warning())
            time.sleep(0.01)

    def get_random_msg(self):
        return f"Test {random.randint(0, 1000)};\r\n"

    def get_random_error(self):
        return f"! test went wrong {random.randint(0, 1000)};\r\n"

    def get_random_warning(self):
        return f"?something may be going wrong {random.randint(0,1000)};\r\n"

    def get_data(self):
        return self.data


def list_ports():
    ports = []
    for i in range(0, random.randint(1, 4)):
        ports.append(f"COM{random.randint(0,10)}")
    return ports


if __name__ == "__main__":
    s = serial_interface("com1", 115200)

    while 1:
        time.sleep(0.5)
        print(s.get_data())
