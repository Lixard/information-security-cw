import tkinter as tk

# initializing
root = tk.Tk()

# setup theme
root.tk.call("source", "theme.tcl")

# resize window to the half of screen resolution
root.geometry(f"{root.winfo_screenwidth()//2}x{root.winfo_screenheight()//2}")

# infinite loop
root.mainloop()
