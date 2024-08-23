import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import keyboard
import pynput.mouse as Mouse
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode, Key
from sys import platform
import threading
import time
from random import uniform
import CTkToolTip


# Set initial delay and button
delay = 1
button = Button.left
start_stop_key = Key.esc
new_hotkey = []
start_app = False
record = False
theme = True
AOTactive = False
click_count = 0
ADactive = False
repActive = False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Auto Clicker")
        self.geometry("600x300")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.attributes('-alpha', 0.95)
        self.configure(fg_color="#353190")
        self.bind_all("<Button-1>", lambda event: event.widget.focus_set())

        self.attributes('-topmost', True)
        # self.update()
        # self.attributes('-topmost', False)

        self.settings_open = False
        self.start_stop_key = start_stop_key
        self.theme = theme
        self.AOTactive = AOTactive
        self.ADactive = ADactive
        self.repActive = repActive
        self.button = button
        self.delay = delay
        self.running = False
        self.program_running = True
        self.click_count = click_count
        self.cursorpos = False
        self.choseloc = False
        self.setx, self.sety = 0, 0

        self.create_widgets()
        self.update_click_count()

        self.click_thread = threading.Thread(target=self.click_mouse_function)
        self.click_thread.start()

        self.mouseclick = Mouse.Listener(on_click=self.getpos)
        self.mouseclick.start()

        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

    def create_widgets(self):

        self.title_bar = ctk.CTkFrame(self, height=30, width=600, fg_color="#2b0e72")
        self.title_bar.pack(side="top", fill="x")

        self.icoImg = ctk.CTkImage(Image.open('img/cursor.ico'))
        self.title_text = ctk.CTkLabel(self.title_bar, text=" Autoclicker", height=29, width=100, fg_color="#2b0e72", text_color="white", font=ctk.CTkFont(family="segoe ui", size=15, weight="bold"),
                                       image=self.icoImg, compound="left", anchor="w")
        self.title_text.place(x=5, y=0)

        self.close_button = ctk.CTkButton(self.title_bar, text='X', font=ctk.CTkFont(weight="bold"), command=self.quit_app, height=29, width=40, 
                                          fg_color="#2b0e72", text_color="white")
        self.close_button.place(x=560, y=0)

        self.minimize_button = ctk.CTkButton(self.title_bar, text='-', font=ctk.CTkFont(size=18, weight="bold"), command=self.minscr, height=29, width=40, 
                                             fg_color="#2b0e72", text_color="white")
        self.minimize_button.place(x=520, y=0)

        self.settingsimage = ctk.CTkImage(Image.open('img/settings.png'))
        self.settings_button = ctk.CTkButton(self.title_bar, text="", command=self.opensettings, fg_color="#2b0e72",
                                             image=self.settingsimage, width=40, height=29)
        self.settings_button.place(x=480, y=0)

        # self.quitimage = ctk.CTkImage(Image.open("img/exit.png"))
        # self.quit_button = ctk.CTkButton(self.content, text="quit", command=self.quit_app, fg_color="white", text_color="black",
        #                                  image=self.quitimage, width=100, height=50)
        # self.quit_button.place(x=500, y=200)

        self.content = ctk.CTkFrame(self, fg_color="#353190", width=600,height=270)
        self.content.place(x=0,y=30)

        def get_pos(event):
            xwin = app.winfo_x()
            ywin = app.winfo_y()
            startx = event.x_root
            starty = event.y_root

            ywin = ywin - starty
            xwin = xwin - startx


            def move_window(event):
                app.geometry("600x300" + '+{0}+{1}'.format(event.x_root + xwin, event.y_root + ywin))
            startx = event.x_root
            starty = event.y_root

            self.title_bar.bind('<B1-Motion>', move_window)
        self.title_bar.bind('<Button-1>', get_pos)


        self.speed_label = ctk.CTkLabel(self.content, text="Clicks per Second:", width=125, height=25, text_color="white")
        self.speed_label.place(x=0, y=20)

        self.speed_var = ctk.StringVar()
        self.speed_entry = ctk.CTkEntry(self.content, textvariable=self.speed_var, width=70, height=25)
        self.speed_entry.insert(0, "1")
        self.speed_entry.place(x=125, y=20)

        self.set_speed_button = ctk.CTkButton(self.content, text="Set", command=self.set_speed, width=50, height=25,
                                              fg_color="white", text_color="black")
        self.set_speed_button.place(x=205, y=20)

        self.start_label = ctk.CTkLabel(self.content, text="Toggle Key: ", width=125, height=25, text_color="white")
        self.start_label.place(x=0, y=70)

        self.startkey_var = ctk.StringVar()
        self.startkey_label = ctk.CTkEntry(self.content, textvariable=self.startkey_var, state="readonly", width=70, height=25,
                                           fg_color="light grey")
        self.startkey_var.set("ESC")
        self.startkey_label.place(x=125, y=70)

        self.togglekeybut = ctk.CTkButton(self.content, text="Change", command=self.set_togglekey, width=50, height=25,
                                          fg_color="white", text_color="black")
        self.togglekeybut.place(x=205, y=70)

        self.clicktypelbl = ctk.CTkLabel(self.content, text="Types of clicks:", width=125, height=25, text_color="white")
        self.clicktypelbl.place(x=0, y=120)

        self.clicktypecombo = ctk.CTkComboBox(self.content, values=["Left Click", "Middle Click", "Right Click"],
                                              command=self.changeclicktype, state="readonly")
        self.clicktypecombo.set("Left Click")
        self.clicktypecombo.place(x=125, y=120)

        # self.recordimage = ctk.CTkImage(Image.open("img/record.png"))
        # self.record_button = ctk.CTkButton(self.content, text=" Record", hover=False, fg_color="white", text_color="black",
        #                                    width=100, height=50, command=self.startstop_record, image=self.recordimage)
        # self.record_button.place(x=300, y=50)

        #self.content2 = ctk.CTkFrame(self, fg_color="#58427C")
        #self.content2.pack(side="left",fill="both")

        self.durationlbl = ctk.CTkLabel(self.content, text="Duration:", width=125, height=25, text_color="white")
        self.durationlbl.place(x=275, y=20)

        self.unlimitrad = ctk.CTkRadioButton(self.content, text="Unlimited", fg_color="white", text_color="white", command=self.changedurationtype2,
                                            width=100, height=10)
        self.unlimitrad.select()
        self.unlimitrad.place(x=380, y=45)

        self.repeatrad = ctk.CTkRadioButton(self.content, text="Repeat                        (Seconds)", fg_color="white", 
                                            text_color="white",  command=self.changedurationtype1, width=100, height=10, value=self.repActive)
        self.repeatrad.place(x=380, y=75)

        self.repeatvar = ctk.StringVar()
        self.repeatvar.set("5")
        self.repeatentry = ctk.CTkEntry(self.content, textvariable=self.repeatvar, width=60, height=20, fg_color="light grey", state="readonly")
        self.repeatentry.place(x=460, y=75)

        self.locationlabel = ctk.CTkLabel(self.content, text="Location:", text_color="white", width=125, height=25)
        self.locationlabel.place(x=275, y=110)

        self.clicklocbut = ctk.CTkButton(self.content, text="Choose Click Location\n x: 0  y: 0  ", width=150, height=40, command=self.getcursorpos, fg_color="grey")
        self.clicklocbut.place(x=380, y=130)
        self.folcurbut = ctk.CTkButton(self.content, text="Follow cursor", width=150, height=30, fg_color="purple", command=self.followcur)
        self.folcurbut.place(x=380, y=180)

        self.clickcount_label = ctk.CTkLabel(self.content, text="Click Count:", width=70, height=25, text_color="white")
        self.clickcount_label.place(rely=0.78, relx=0.07, x=0, y=0, anchor="s")

        self.click_count_var = ctk.StringVar()
        self.click_count_var.set(str(click_count))
        self.click_count_entry = ctk.CTkEntry(self.content, textvariable=self.click_count_var, state="readonly", width=70, height=25, fg_color="light grey")
        self.click_count_entry.place(rely=0.78, relx=0.20, x=0, y=0, anchor="s")

        self.run_button = ctk.CTkButton(self.content, hover=False, text="State: Running", fg_color="#2b0e72", width=600, height=50)
        self.run_button.place(rely=1.0, relx=0.5, x=0, y=0, anchor="s")

    def minscr(self):
            self.iconify()

    def followcur(self):
        self.choseloc = False
        self.folcurbut.configure(fg_color="purple")
        self.clicklocbut.configure(fg_color="grey")

    def getcursorpos(self):
        self.cursorpos = True
        self.clicklocbut.configure(text="Click desired area", fg_color="green")
        self.choseloc = True
        self.folcurbut.configure(fg_color="grey")

    def getpos(self, x, y, button, pressed):
        if self.cursorpos:
            if button == self.button and pressed:
                self.setx = x
                self.sety = y
            
                self.cursorpos = False
                self.clicklocbut.configure(text=f"Choose location\n x: {self.setx}  y: {self.sety}  ", fg_color="purple")

    def changedurationtype1(self):
        self.repActive=True
        self.unlimitrad.deselect()
        self.repeatrad.select()
        self.repeatentry.configure(state="normal", fg_color="white")
        self.repeatentry.focus()
    def changedurationtype2(self):
        self.repActive=False
        self.unlimitrad.select()
        self.repeatrad.deselect()
        self.repeatentry.configure(state="disabled", fg_color="light grey")

    def changeclicktype(self, clickchoice):
        self.focus()
        clickchoice = self.clicktypecombo.get()
        if clickchoice == "Left Click":
            self.button = Button.left
        elif clickchoice == "Middle Click":
            self.button = Button.middle
        else:
            self.button = Button.right

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def click_mouse_function(self):
        offset = 0.0
        mouse = Controller()
        while self.program_running:
            while self.running:
                if self.choseloc:
                    mouse.position = (self.setx, self.sety)
                if self.ADactive:
                    offset = uniform(0.01, 0.05)
                else:
                    offset = 0.0
                mouse.click(self.button)
                self.click_count += 1
                time.sleep(self.delay+offset)
            time.sleep(0.1)

    def startstop_record(self):
        global record
        record = not record
        if record:
            self.record_button.configure(text="Recording")
        else:
            self.record_button.configure(text="Record")

    def set_speed(self):
        speed_input = self.speed_var.get()
        if speed_input != "" and speed_input.isnumeric():
            self.delay = 1 / float(speed_input)
        else:
            self.delay = 1
            self.speed_entry.delete(0, ctk.END)
            self.speed_entry.insert(0, "1")
        self.focus()

    def set_togglekey(self):
        hotkey_created = False
        new_hotkey = []
        used_modifiers = []
        self.startkey_var.set('Press any key...')

        def callback(key):
            nonlocal hotkey_created
            if key.name not in keyboard.all_modifiers:
                new_hotkey.append(key.name)
                hotkey_created = True
                return
            if key.name not in used_modifiers:
                new_hotkey.append(key.name)
                used_modifiers.append(key.name)

        keyboard.hook(callback)

        def wait_for_callback():
            while not hotkey_created:
                time.sleep(0.01)
            keyboard.unhook(callback)

            try:
                self.start_stop_key = Key[new_hotkey[0]]
            except:
                self.start_stop_key = KeyCode(char=new_hotkey[0])

            self.startkey_var.set(str(new_hotkey[0]).capitalize())
            messagebox.showinfo('Hotkey Change', "Toggle Key changed to " + str(new_hotkey[0]).capitalize())

        threading.Thread(target=wait_for_callback, daemon=True).start()

    def quit_app(self):
        self.exit()
        self.listener.stop()
        self.quit()

    def opensettings(self):
        if not self.settings_open:
            self.settings_button.configure(fg_color="light blue")
            self.settings_open = True
            self.update()
            self.newWindow = ctk.CTkToplevel(self)
            self.newWindow.title("Settings")
            x = self.winfo_x() + self.winfo_width() + 5
            y = self.winfo_y()
            width, height = 400, 300
            self.newWindow.geometry(f"{width}x{height}+{x}+{y}")
            self.newWindow.resizable(False, False)
            self.newWindow.attributes('-alpha', 0.95)
            #self.newWindow.configure(fg_color="#9E72C3")
            self.newWindow.configure(fg_color="#353190")
            self.newWindow.lift(self)
            self.newWindow.bind_all("<Button-1>", lambda event: event.widget.focus_set())
            self.newWindow.overrideredirect(True)
            # if platform.startswith("win"):
            #     self.newWindow.after(200, lambda: self.newWindow.iconbitmap("img/settings.ico"))
            self.create_settingwidgets()
        else:
            self.newWindow.destroy()
            self.settings_open = False
            self.settings_button.configure(fg_color="#2b0e72")

    def on_settings_close(self):
        self.newWindow.destroy()
        self.settings_open = False

    def create_settingwidgets(self):

        self.title_barN = ctk.CTkFrame(self.newWindow, height=30, width=600, fg_color="#2b0e72")
        self.title_barN.pack(side="top", fill="x")

        self.icoImgN = ctk.CTkImage(Image.open('img/settings.png'))
        self.title_textN = ctk.CTkLabel(self.title_barN, text=" Settings", height=29, width=100, fg_color="#2b0e72", text_color="white",
                                       image=self.icoImgN, compound="left", anchor="w")
        self.title_textN.place(x=5, y=0)

        def get_posN(event):
            xwin = app.newWindow.winfo_x()
            ywin = app.newWindow.winfo_y()
            startx = event.x_root
            starty = event.y_root

            ywin = ywin - starty
            xwin = xwin - startx


            def move_windowN(event):
                app.newWindow.geometry("400x300" + '+{0}+{1}'.format(event.x_root + xwin, event.y_root + ywin))
            startx = event.x_root
            starty = event.y_root

            self.title_barN.bind('<B1-Motion>', move_windowN)
        self.title_barN.bind('<Button-1>', get_posN)

        self.appearanceframe = ctk.CTkFrame(self.newWindow, fg_color="#353190", width=400, height=270)
        self.appearanceframe.place(x=0,y=30)

        self.APPlabel = ctk.CTkLabel(self.appearanceframe, text="Appearance:", width=70, height=30, text_color="white")
        self.APPlabel.place(x=10,y=20)

        self.APPcombobox = ctk.CTkComboBox(self.appearanceframe, values=["Light", "Dark"], state="readonly", command=self.theme_change)
        if self.theme:
            self.APPcombobox.set("Light")
        else: 
            self.APPcombobox.set("Dark")
        self.APPcombobox.place(x=90,y=20)

        self.antiDecLbl = ctk.CTkLabel(self.newWindow, text="Anti-detection:", width=70, height=30, text_color="white")
        self.antiDecLbl.place(x=10,y=90)

        self.antiDecSw = ctk.CTkSwitch(self.newWindow, hover=False, text="", command=self.ADtoggle, fg_color="white", progress_color="light grey")
        if ADactive:
            self.antiDecSw.select()
        else:
            self.antiDecSw.deselect()
        self.antiDecSw.place(x=110,y=95)

        self.antiDecImg = ctk.CTkImage(Image.open("img/info.png"))
        self.antiDecInfo = ctk.CTkLabel(self.newWindow, image=self.antiDecImg, text="", width=20, height=20)
        self.antiDecInfo.place(x=160,y=95)
        self.antiToolTip = CTkToolTip.CTkToolTip(self.antiDecInfo, message="Adds a random short delay between each click", 
                                                 delay=0, alpha=1)
        self.antiToolTip.attributes("-topmost", True)

        self.aotlabel = ctk.CTkLabel(self.newWindow, text="Always on Top:", text_color="white")
        self.aotlabel.place(x=10,y=130)

        self.AOTswitch = ctk.CTkSwitch(self.newWindow, text="", command=self.AOTtoggle, fg_color="white", progress_color="light grey")
        if self.AOTactive:
            self.AOTswitch.select()
        else:
            self.AOTswitch.deselect()
        self.AOTswitch.place(x=110, y=135)
    def theme_change(self, theme_choice):
        self.focus()
        theme_choice = self.APPcombobox.get()
        if theme_choice == "Light":
            self.theme = True
            self.appearance_mode = ctk.set_appearance_mode("light")
        else:
            self.theme = False
            self.appearance_mode = ctk.set_appearance_mode("dark")
        self.newWindow.lift(self)

    def AOTtoggle(self):
        self.focus()
        if self.AOTswitch.get() == 1:
            self.AOTactive = True
            self.attributes('-topmost', True)
            self.newWindow.attributes('-topmost', True)
        else:
            self.AOTactive = False
            self.attributes('-topmost', False)
            self.newWindow.attributes('-topmost', False)

    def ADtoggle(self):
        if self.antiDecSw.get() == 1:
            self.ADactive = True
        else:
            self.ADactive = False

    def on_press(self, key):
        if key == self.start_stop_key:
            if self.running:
                self.stop_clicking()
                self.run_button.configure(fg_color="#2b0e72")
                self.attributes('-disabled' , False)
            else:
                self.start_clicking()
                self.run_button.configure(fg_color="green")
                self.attributes('-disabled' , True)
                if self.repActive:
                    self.x = self.click_count + (int(self.repeatentry.get())*int(self.speed_entry.get()))
                    threading.Thread(target=self.repeat_callback, daemon=True).start()

    def repeat_callback(self):
        while self.click_count != self.x:
            time.sleep(0.01)  
        self.stop_clicking()
        self.run_button.configure(fg_color="#2b0e72")
        self.attributes('-disabled' , False)  

    def update_click_count(self):
        self.click_count_var.set(str(self.click_count))
        self.after(100, self.update_click_count)

if __name__ == "__main__":
    app = App()
    app.mainloop()
