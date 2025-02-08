import tkinter as tk
from PIL import ImageGrab
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BenchmarkApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Screen Update Benchmark")
        

        self.label2 = tk.Label(master, text="Timeout recording (seconds):")
        self.label2.pack(pady=5)
        self.timeout_number_input = tk.Entry(master, )
        self.timeout_number_input.insert(0, "10")
        self.timeout_number_input.pack(pady=20)


        self.start_button = tk.Button(master, text="Start Benchmark", command=self.start_benchmark)
        self.start_button.pack(pady=20)

        self.stop_button = tk.Button(master, text="Stop Benchmark", command=self.stop_benchmark, state=tk.DISABLED)
        self.stop_button.pack(pady=20)

        self.label = tk.Label(master, text="")
        self.label.pack(pady=20)

        self.running = False
        self.previous_image = None
        self.change_count = 0

        # Variables for rectangle selection
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.canvas = None

    def start_benchmark(self):
        self.running = True
        self.change_count = 0
        self.start_button.config(state=tk.DISABLED)
        self.master.attributes("-alpha", 0.5)  # Make the window semi-transparent
        self.stop_button.config(state=tk.NORMAL)
        self.label.config(text="Select an area on the screen...")
        logging.info("Benchmark started. Please select an area.")

        # Create a transparent canvas for selection
        self.create_selection_canvas()

    def create_selection_canvas(self):
        self.canvas = tk.Canvas(self.master, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)
        logging.info(f"Rectangle started at ({self.start_x}, {self.start_y}).")

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        logging.debug(f"Rectangle updated to ({self.start_x}, {self.start_y}, {event.x}, {event.y}).")

    def on_button_release(self, event):
        self.end_x, self.end_y = event.x, event.y
        self.canvas.destroy()  # Remove the selection canvas
        logging.info(f"Rectangle finalized from ({self.start_x}, {self.start_y}) to ({self.end_x}, {self.end_y}).")
        self.start_benchmark_capture()  # Start capturing the selected area

    def start_benchmark_capture(self):
        self.master.after(200, self.capture_area)
        self.master.after(int(self.timeout_number_input.get())*1000, self.stop_benchmark)
        # minimize the window
        self.master.iconify()

    def stop_benchmark(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        times_per_second = self.change_count / int(self.timeout_number_input.get())
        self.label.config(text=f"Changes detected: {times_per_second} times per second.")
        logging.info(f"Benchmark stopped. Total changes detected: {self.change_count}.")
        self.master.deiconify()
        self.master.attributes("-alpha", 1)

    def capture_area(self):
        if not self.running:
            return

        # Get the position of the application window
        x_offset = self.master.winfo_rootx()
        y_offset = self.master.winfo_rooty()

        # Calculate the actual screen coordinates for the selected area
        x1 = min(self.start_x, self.end_x) + x_offset
        y1 = min(self.start_y, self.end_y) + y_offset + self.label.winfo_y() + self.label.winfo_height() + 22  # Adjust for the label height
        x2 = max(self.start_x, self.end_x) + x_offset
        y2 = max(self.start_y, self.end_y) + y_offset + self.label.winfo_y() + self.label.winfo_height() + 22 # Adjust for the label height

        # Log the coordinates being captured
        logging.info(f"Capturing area: ({x1}, {y1}, {x2}, {y2})")

        # Capture the screen excluding the application window
        current_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        current_array = np.array(current_image)

        if self.previous_image is not None:
            # Compare the current image with the previous one
            if not np.array_equal(current_array, self.previous_image):
                self.change_count += 1
                logging.info("Change detected in the selected area.")

        self.previous_image = current_array
        self.master.after(50, self.capture_area)  # Capture every 100 ms

if __name__ == "__main__":
    root = tk.Tk()
    # root.attributes("-alpha", 0.5)  # Make the window semi-transparent
    app = BenchmarkApp(root)
    root.mainloop()