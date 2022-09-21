import tkinter

def p():
    print(var.get())

window = tkinter.Tk()
var = tkinter.BooleanVar()
var.set(True)
chk = tkinter.Checkbutton(window, text='foo', variable=var, command=p)
chk.pack(side=tkinter.LEFT)

#txt_check = tkinter.Label(master=window, text="Имя", width=7).pack(side=tkinter.LEFT)
window.mainloop()