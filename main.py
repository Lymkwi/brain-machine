#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
##########################
## 

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog
import sys
import queue
import asyncio

class window(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Brainfucking Machine")
    
        #self.geometry("800x600")
        self.mframe = tk.Frame(self)
        self.mframe.pack()
        self.mframe.grid_configure(columnspan = 1, rowspan = 1)
        self.lframe = tk.Frame(self.mframe)
        self.lframe.grid(row = 0, column = 0)
        self.code_entry = tk.Text(self.lframe,
                bg = "white", fg = "green",
                width = 80, height = 30,
                cursor = "xterm",
                selectbackground = "blue",
                selectforeground = "black"
        )
        self.code_entry.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = "nsew")
        self.output_entry = tk.Text(self.lframe,
                cursor = "xterm",
                state = tk.DISABLED,
                width = 80,
                height = 2,
        )
        self.output_entry.grid(row = 2, column = 0, padx = 2)

        self.MemoryBar = tk.Frame(self.mframe, bg = "grey", cursor = "tcross")
        self.MemoryBar.grid(row = 0, column = 1, sticky = "snew")
        self.MemoryBar.Label = tk.Label(self.MemoryBar, text = "Memory Tape", bg = "grey")
        self.MemoryBar.Label.grid(row = 0, column = 0, pady = 2, sticky = "snew")

        self.MemoryBar.indicator = tk.Text(self.MemoryBar, bg = "white",
                    state = tk.DISABLED,
                    width = 20,
        )
        self.MemoryBar.indicator.grid(row = 1, column = 0, sticky = "snew", pady = 2, padx = 3)
        self.MemoryBar.bframe = tk.Frame(self.MemoryBar)
        self.MemoryBar.bframe.grid(row = 2, column = 0, sticky = "snew")
        self.MemoryBar.bframe.grid_configure(columnspan = 1, rowspan = 1)
        self.MemoryBar.runButton = tk.Button(self.MemoryBar.bframe, text= "RUN", command = self.run_code)
        self.MemoryBar.runButton.grid(row = 0, column = 0, sticky = "snew")
        self.bind_all("<KeyPress-F5>", self._get_event_wrapper(self.run_code))
        self.MemoryBar.stepButton = tk.Button(self.MemoryBar.bframe, text = "STEP", command = self.step_code)
        self.MemoryBar.stepButton.grid(row = 1, column = 0, sticky = "snew")
        self.MemoryBar.resetButton = tk.Button(self.MemoryBar.bframe, text = "RESET", command = self.stop_code)
        self.MemoryBar.resetButton.grid(row = 0, column = 1, sticky = "snew")
        self.MemoryBar.debugButton = tk.Button(self.MemoryBar.bframe, text = "DEBUG")
        self.MemoryBar.debugButton.grid(row = 1, column = 1, sticky = "snew")

        self.machine = FuckingMachine()
        self.curfile = ""
        self.running = False

	# Menus
        self.mainmenu = tk.Menu(self)

        # File
        filem = tk.Menu(self.mainmenu)
        filem.add_command(label = "Open File", command = self.open_file, accelerator = 'CTRL+O')
        self.bind_all("<Control-KeyPress-o>", self._get_event_wrapper(self.open_file))
        filem.add_command(label = "Save File", command = self.save_file, accelerator = 'CTRL+S')
        self.bind_all("<Control-KeyPress-s>", self._get_event_wrapper(self.save_file))
        filem.add_command(label = "Save File As", command = self.saveasfile, accelerator = 'CTRL+SHIFT+S')
        self.bind_all("<Control-Shift-KeyPress-s>", self._get_event_wrapper(self.saveasfile))
        filem.add_command(label = "Close File", command = self.close_file, accelerator = 'CTRL+W')
        self.bind_all("<Control-KeyPress-w>", self._get_event_wrapper(self.close_file))
        filem.add_separator()
        filem.add_command(label = "Quit", command = self.quit, accelerator = 'CTRL+Q')
        self.bind_all("<Control-KeyPress-q>", self._get_event_wrapper(self.quit))
        self.mainmenu.add_cascade(label = "File", menu = filem)

        self.config(menu=self.mainmenu)
        self.init_indic()

        self.running_code, self.step, self.debug = False, False, False

    def _get_event_wrapper(self, func):
        def _wrapper(event):
            func()

        return _wrapper

    def close_file(self):
        data = self.code_entry.get('0.0', 'end')
        if len(data.replace('\n', '')) > 0:
            res = tkinter.messagebox.askyesnocancel("Closing", "Do you want to save?", icon = 'question')
            if res == None:
                return
            elif res:
                self.save_file()

        self.code_entry.delete('0.0', 'end')
        self.curfile = ""

    def quit(self):
        self.destroy()

    def save_file(self):
        if self.curfile == "":
            self.saveasfile()
        else:
            fptr = open(self.curfile, 'w')
            fptr.write(self.code_entry.get('0.0', 'end'))
            fptr.close()
        print("Saved to " + self.curfile)

    def saveasfile(self):
        fname = tkinter.filedialog.asksaveasfilename()
        if not fname or len(fname) == 0:
            return
        fptr = open(fname, "w")
        fptr.write(self.code_entry.get('0.0', 'end'))
        fptr.close()
        self.curfile = fname

    def open_file(self):
        newfile = tkinter.filedialog.askopenfilename(filetypes = [
                ("BrainFuck Source Code", '.b'),
                ("BrainFuck Source Code", '.bf'),
                ("All Files", '*')
            ], title = "Open File..."
        )
        if not newfile or len(newfile) == 0:
            return
        if self.code_entry.get('0.0', 'end').replace('\n', '') != "":
            result = tkinter.messagebox.askyesnocancel("Delete", "Save?", icon='warning')
            if result == "cancel":
                return
            elif result == "yes":
                self.save_file()
        
        self.code_entry.delete('0.0', 'end')

        nfptr = open(newfile, "r")
        newdata = nfptr.read()
        nfptr.close()

        self.code_entry.insert('0.1', newdata)
        self.curfile = newfile

    def init_indic(self):
        self.MemoryBar.indicator.configure(state=tk.NORMAL)
        self.MemoryBar.indicator.delete('0.0', 'end')
        position = self.machine.position
        
        lrange, mrange = 0, 32
        if position > 16:
            lrange = position-16
            mrange = position+16
       
        for index in range(lrange, mrange):
            self.MemoryBar.indicator.insert('end', "   {0} {1}\n".format(index, self.machine.memory[index]))
            if (self.machine.memory[index]) != 0:
                print(index)
                print(self.machine.memory[index])

        k,m = self.MemoryBar.indicator.winfo_height(), self.MemoryBar.indicator.winfo_width()
        self.MemoryBar.indicator.configure(state = tk.DISABLED)

    def break_code(self):
        self.running = False
        self.init_indic()

    def run_code(self):
        self.running_code = True
        self.init_run_code()
        self.single_code_step()
        self.stop_code()

    def step_code(self):
        self.step = True
        self.init_run_code()
        self.single_code_step()
        self.step = True
        if self.machine.eof():
            self.stop_code()

    def init_run_code(self):
        self.running = True
        self.code_entry.configure(state = tk.DISABLED)
        self.output_entry.configure(state = tk.NORMAL)
        self.output_entry.delete('0.0', 'end')
        self.output_entry.configure(state = tk.DISABLED)
        self.MemoryBar.runButton.configure(state = tk.DISABLED)
        self.MemoryBar.debugButton.configure(state = tk.DISABLED)
        self.MemoryBar.stepButton.configure(state = tk.DISABLED)
        d = self.code_entry.get('0.0', 'end')
        self.machine.feed(d)
        r, m = self.machine.start()

    def single_code_step(self):
        while (self.running_code or self.step or self.debug) and not self.machine.eof():
            self.machine.step()
            pos = self.machine.getposition()
            d = self.machine.extract()
            if d:
                self.output_entry.configure(state=tk.NORMAL)
                self.output_entry.insert('end', d)
                self.output_entry.configure(state=tk.DISABLED)
            
            if self.machine.awaiting_input:
                query = tkinter.simpledialog.askstring("Input Required", "An input is required by the program")
                self.machine.inject((query or "") + '\0')
            self.init_indic()
            self.step = False

    def stop_code(self):
        self.machine.stop()
        self.unlock_buttons()
        self.running_code, self.step, self.debug = False, False, False

    def unlock_buttons(self):
        self.MemoryBar.runButton.configure(state = tk.NORMAL)
        self.MemoryBar.debugButton.configure(state = tk.NORMAL)
        self.MemoryBar.stepButton.configure(state = tk.NORMAL)
        self.code_entry.configure(state = tk.NORMAL)

class FuckingMachine:
    def __init__(self):
        self.init()

    def init(self):
        self.buffer = ""
        self.memory = [0] * 65536
        self.cursor = 0
        self.running = False
        self.loop_register = []
        self.position = 0
        self.awaiting_input = False
        self.istream = queue.Queue()
        self.ostream = queue.Queue()

    def extract(self):
        ret = ""
        while not self.ostream.empty():
            ret += self.ostream.get()

        return ret

    def inject(self, data):
        for c in data:
            self.istream.put(c)

    def feed(self, content):
        self.buffer += content

    def getposition(self):
        return self.position

    def assertion(self):
        n = 0
        for c in self.buffer:
            if c == '[':
                n+=1
            elif c == ']':
                n-=1
            if n < 0:
                return False, "One too many ']'"
        if n > 0:
            return False, "One too many '['"
        return True, ""

    def start(self):
        state, mes = self.assertion()
        if not state:
            return False, mes

        self.running = True
        return True, mes

    def stop(self):
        self.running = False
        self.buffer = ""
        self.init()

    def step(self):
        if self.running:
            c = self.buffer[self.position]
            if c == '+':
                self.memory[self.cursor] += 1
            elif c == '-':
                self.memory[self.cursor] -= 1 #(self.memory[self.cursor] - 1)%255
            elif c == '>':
                self.cursor = (self.cursor + 1)%65535
            elif c == '<':
                self.cursor = (self.cursor - 1)%65535
            elif c == '.':
                self.ostream.put(chr(self.memory[self.cursor]))
            elif c == ',':
                if not self.istream.empty():
                    inp = self.istream.get()
                    self.memory[self.cursor] = ord(inp)
                    self.awaiting_input = False
                else:
                    self.awaiting_input = True
                    return

            elif c == '[':
                if self.memory[self.cursor]:
                    self.loop_register.append(self.position)
                else:
                    depth = 1
                    while depth > 0:
                        self.position += 1
                        chara = self.buffer[self.position]
                        if chara == '[':
                            depth += 1
                        elif chara == ']':
                            depth -= 1
                   
            elif c == ']':
                if self.memory[self.cursor]:
                    self.position = self.loop_register[-1]
                else:
                    self.loop_register.pop()
            self.position += 1

    def eof(self):
        return self.position == len(self.buffer)

if __name__ == "__main__":
    win = window()
    win.mainloop()
