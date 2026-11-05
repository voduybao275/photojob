import tkinter as tk
BG = "#0f172a"
MIN_SIZE = (760, 460)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Giao diện toàn màn hình")
        self.configure(bg=BG)
        self.minsize(*MIN_SIZE)
        self.is_fullscreen = True
        #self.withdraw()
if __name__ == "__main__":
    App().mainloop()
