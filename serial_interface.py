import serial
import serial.tools.list_ports
import threading
import datetime
import time
from collections import deque

from dearpygui.core import log, log_info, log_error, log_warning, is_dearpygui_running


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
        # self.buff = []
        self.running = True
        log_info(f"Starting serial interface at {port} with baud {baudrate}", logger=self.log_window)
        self.ser = serial.Serial(port, baudrate)  # opens the serial port
        log_info(f"serial interface started", logger=self.log_window)
        self.ser.flushInput()  # clears the buffers to start clean
        self.serial_listener_thread = self.serial_listener()  # starts the serial listener
        self.buf = bytearray()

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.ser.in_waiting))
            data = self.ser.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)

    def close(self):
        self.running = False
        self.serial_listener_thread.join()

    def parse_point(self, s: str):
        t = time.time()
        t_str = time.strftime("%T", time.localtime(t))

        s = s.strip()
        raw_str = f"{t_str}: {s}"
        if(self.raw_log_window != ""):
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
            log_warning(warning_msg, logger=self.log_window)
            self.data["warnings"].append(warning_msg)

        else:
            info_msg = f"{t_str}: {s.strip(';')}"
            log_info(info_msg, logger=self.log_window)
            self.data["messages"].append(info_msg)

    @threaded
    def serial_listener(self):
        # listen to what is being sent on the bus

        while self.running and is_dearpygui_running():
            try:
                data = self.readline()
                self.parse_point(data.decode("utf-8"))
            except:
                pass
            
        self.ser.close()

    def get_data(self):
        return self.data


def list_ports():
    ports = []
    for port in serial.tools.list_ports.comports():
        ports.append(port.device)
        print(port.device)

    return ports


if __name__ == "__main__":
    # s = serial_interface("com1", 115200)
    print("test")
    list_ports()
    ser = serial_interface('COM8', 115200)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
    print(ser.get_data())
    print("closing serial port")
    ser.close()
    print("port is closed")
    # ser = serial.Serial('COM8', 115200)
    # print("serial interrface started")
    # ser.flushInput()
    # while 1:
    #     try:
    #         ser_bytes = ser.readline()
    #         decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
    #         # print("data:")
    #         print(decoded_bytes)
    #     except:
    #         print("exception")
    #         break
    # time.sleep(0.5)
    # print(s.get_data())
