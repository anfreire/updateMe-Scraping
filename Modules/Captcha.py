import os
import threading
import pickle
from pathlib import Path
from typing import List, Tuple, Any
from pyvirtualdisplay import Display
from prompt_toolkit.shortcuts import radiolist_dialog
import time
import pyscreenshot as ImageGrab

RECORDS_PATH = Path("/home/anfreire/Documents/UpdateMe/Scrapping/Records/")


class CaptchaSolver:
    def __init__(self, visible: bool = False):
        self.records: List[Tuple[str, ...]] = []
        self.display = None
        self.__init_display(visible)
        self.__init_controller()
        self.__init_listener()
        self.recording = False

    def __del__(self):
        os.system("killall chromium > /dev/null 2>&1")

        self.__del_controller()
        self.__del_listener()
        self.__del_display()

    def __init_display(self, visible: bool = False):
        self.display_props = {
            "size": (800, 600),
            "visible": 0,
            "use_xauth": False,
        }
        self.display = Display(**self.display_props)
        self.display.start()
        os.environ["DISPLAY"] = f":{self.display.display}"

    def __del_display(self):
        try:
            if self.display:
                self.display.stop()
        except Exception as e:
            pass

    def __init_controller(self):
        from pynput import mouse

        self.controller = mouse.Controller()

    def __del_controller(self):
        try:
            if self.controller:
                self.controller.stop()
        except Exception as e:
            pass

    def __init_listener(self):
        from pynput import mouse

        self.listener = mouse.Listener(
            on_move=self.mouse_move_handler, on_click=self.mouse_click_handler
        )
        self.listener.start()

    def __del_listener(self):
        try:
            if self.listener:
                self.listener.stop()
        except Exception as e:
            pass

    def map_to_virtual_display(self, x: int, y: int) -> Tuple[int, int]:
        """Map actual screen coordinates to virtual display coordinates."""
        vx = max(0, min(x, self.display_props["size"][0] - 1))
        vy = max(0, min(y, self.display_props["size"][1] - 1))
        return vx, vy

    def mouse_move_handler(self, x: int, y: int) -> None:
        if self.recording:
            vx, vy = self.map_to_virtual_display(x, y)
            self.records.append(("move", vx, vy))

    def mouse_click_handler(self, x: int, y: int, button: any, pressed: bool) -> None:
        if self.recording:
            vx, vy = self.map_to_virtual_display(x, y)
            self.records.append(("click", vx, vy, button, pressed))

    def stop_listener(self) -> None:
        input("Press Enter to stop recording...")
        self.recording = False

    def start_recording(self, link: str) -> None:
        self.recording = True
        stop_listener_thread = threading.Thread(target=self.stop_listener)
        stop_listener_thread.start()

        self.open_chrome(link)

        stop_listener_thread.join()
        self.listener.stop()

    def save_records(self, filename: str) -> None:
        filepath = RECORDS_PATH / f"{filename}.pkl"
        with open(filepath, "wb") as file:
            pickle.dump(self.records, file)
        print(f"Recording saved to {filepath}")

    def open_chrome(self, link: str) -> None:
        os.system(
            f"chromium --user-data-dir={os.path.expanduser('~')}/.config/chromium --profile-directory='Profile 1' --window-size=800,600 --window-position=0,0 '{link}' > /dev/null 2>&1 &"
        )

    def record(self, link: str) -> None:
        self.start_recording(link)
        filename = input("Enter the filename to save the recording: ")
        self.save_records(filename)

    def play(self, link: str) -> None:
        files = [f for f in RECORDS_PATH.iterdir() if f.suffix == ".pkl"]
        import random
        file = files[random.randint(0, len(files) - 1)]

        try:
            with open(file, "rb") as f:
                records = pickle.load(f)

            self.open_chrome(link)
            time.sleep(5)
            from pynput.mouse import Button

            for record in records:
                try:
                    if record[0] == "move":
                        self.controller.position = (record[1], record[2])
                    elif record[0] == "click":
                        self.controller.position = (record[1], record[2])
                        button = (
                            Button.left if record[3] == Button.left else Button.right
                        )
                        self.controller.click(button)
                    time.sleep(0.01)
                except Exception as e:
                    print(f"Error during playback action: {e}")
                    break
            print("Playback completed successfully.")
        except Exception as e:
            print(f"An error occurred during playback: {e}")
        finally:
            time.sleep(3)
            screenshot = ImageGrab.grab(
                bbox=(
                    0,
                    0,
                    self.display_props["size"][0],
                    self.display_props["size"][1],
                )
            )
            filepath = RECORDS_PATH / f"{file}_screenshot.png"
            screenshot.save(filepath)
            print(f"Screenshot saved to {filepath}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        exit("Usage: python Captcha.py <link>")
    link = sys.argv[1]
    recorder = CaptchaSolver(False)
    recorder.play(link)
