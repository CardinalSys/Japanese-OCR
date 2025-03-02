import cv2
import numpy as np
import pytesseract
import tkinter as tk
from PIL import ImageGrab
import keyboard
import pyperclip

resizeScale = 1.0 
model = 4

def create_text_extractor_window():
    window = tk.Tk()
    window.geometry("500x500")
    window.lift()
    window.title("Japanese text extractor")
    window.wm_attributes("-topmost", True)
    window.wm_attributes("-transparentcolor", 'gray')

    preview_frame = tk.Frame(window, bd=2, relief=tk.RAISED, width=300, height=300)
    preview_frame.place(x=100, y=100)

    canvas = tk.Canvas(window, width=500, height=500, highlightthickness=5)
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.create_rectangle(0, 0, 500, 500, fill='gray', outline='gray')
    rect = canvas.create_rectangle(0, 0, window.winfo_width(), window.winfo_height(), fill='gray', outline='gray')
    
    def on_resize(event):
        canvas.coords(rect, 0, 0, event.width, event.height)
        window.wm_attributes("-transparentcolor", 'gray')
    canvas.bind("<Configure>", on_resize)
    
    return window, canvas

def create_options_window(master):
    options = tk.Toplevel(master)
    options.geometry("300x150")
    options.lift()
    options.title("Options")
    
    scale_var = tk.DoubleVar(value=0.5) 
    model_var = tk.IntVar(value=4)
    
    def apply():
        global resizeScale
        global model
        resizeScale = scale_var.get()
        model = model_var.get()
        print(f"New resize scale applied: {resizeScale}")

    tk.Label(options, text="OCR Model:").pack()
    model = tk.Scale(options, from_=1, to=12, orient=tk.HORIZONTAL, variable=model_var)
    model.pack()

    tk.Label(options, text="Resize Scale:").pack()
    scale = tk.Scale(options, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, variable=scale_var)
    scale.pack()




    apply_button = tk.Button(options, text="Apply", command=apply)
    apply_button.pack()

window, canvas = create_text_extractor_window()
create_options_window(window)

def detect_text():
    window.update_idletasks() 
    
    x = canvas.winfo_rootx()
    y = canvas.winfo_rooty()
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    print(f"Canvas geometry: x={x}, y={y}, w={w}, h={h}")
    
    if w == 0 or h == 0:
        print("Error: Canvas dimensions are zero.")
        return
    
    screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    screenshot = screenshot.convert("RGB")
    screenshot_np = np.array(screenshot)
    screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
    
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    custom_config = r'--oem 1 --psm '+ str(model) +' -l jpn'
    
    height_img, width_img = screenshot_np.shape
    print(f"Captured image shape: {width_img}x{height_img}")
    
    if width_img == 0 or height_img == 0:
        print("Error: Captured image is empty.")
        return
    

    new_width = int(width_img * resizeScale)
    new_height = int(height_img * resizeScale)
    smaller = cv2.resize(screenshot_np, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    text = pytesseract.image_to_string(smaller, config=custom_config)
    print("Extracted Text:", text)
    pyperclip.copy(text)

keyboard.add_hotkey("ctrl+q", detect_text)
window.mainloop()
