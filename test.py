import tkinter

def click_btn_Binance():
    print(btn_Binance['text'])
    btn_Binance.configure(text="Стоп")

window = tkinter.Tk()

frame1 = tkinter.Frame(master=window)
frame1.pack(fill=tkinter.X)

txt_Binance = tkinter.Label(master=frame1, text="Binance", width=10)
txt_Binance.pack(side=tkinter.LEFT)

txt_BinanceJob = tkinter.Label(master=frame1, text="остановлен", width=10)
txt_BinanceJob.pack(side=tkinter.LEFT)

btn_Binance = tkinter.Button(master=frame1, text="Старт", width=10, command=click_btn_Binance)
btn_Binance.pack(side=tkinter.RIGHT)

frame2 = tkinter.Frame(master=window)
frame2.pack(fill=tkinter.X)

txt_Binance2 = tkinter.Label(master=frame2, text="Gate", width=10)
txt_Binance2.pack(side=tkinter.LEFT)

img = tkinter.PhotoImage(file="img/ok_16x16.png")
txt_BinanceJob2 = tkinter.Label(master=frame2, image=img, text="Job", width=18)
txt_BinanceJob2.pack(side=tkinter.LEFT)


btn_Binance2 = tkinter.Button(master=frame2, text="Стоп", width=10)
btn_Binance2.pack(side=tkinter.RIGHT)


window.mainloop()