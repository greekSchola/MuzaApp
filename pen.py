import tkinter as tk
from pynput import mouse

class PenTrackerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Pen Simulator")

        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white")
        self.canvas.pack()

        self.pen_down = False
        self.current_stroke = []
        self.all_strokes = []

        # Start mouse listener
        self.listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move)
        self.listener.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            self.pen_down = pressed
            if not pressed and self.current_stroke:
                self.all_strokes.append(self.current_stroke)
                self.current_stroke = []

    def on_move(self, x, y):
        if self.pen_down:
            self.current_stroke.append((x, y))
            self.draw_point(x, y)

    def draw_point(self, x, y):
        self.canvas.create_oval(x-1, y-1, x+1, y+1, fill="black", outline="")

    def on_close(self):
        self.listener.stop()
        self.root.destroy()
        print("Saved strokes:", self.all_strokes)

if __name__ == "__main__":
    PenTrackerApp()
