try:
	import tkinter
except Exception:
	import os
	os.system("python -m pip install tkinter")
	import tkinter

master = tkinter.Tk()
master.title('Minesweeper Menu')
master.geometry('280x100')

tkinter.Label(master, text = 'width').grid(row=0, column=0, padx=10)
tkinter.Label(master, text = 'height').grid(row=1, column=0)
tkinter.Label(master, text = 'mines').grid(row=2, column=0)

errortext = tkinter.Label(master, text = 'invalid input', fg='#ff0000')

input1 = tkinter.Entry(master, width=30)
input2 = tkinter.Entry(master, width=30)
input3 = tkinter.Entry(master, width=30)

input1.grid(row=0, column=1)
input2.grid(row=1, column=1)
input3.grid(row=2, column=1)

def proceed():
	global BOARD_WIDTH, BOARD_HEIGHT, MINES
	
	try:
		BOARD_WIDTH = int(input1.get())
		BOARD_HEIGHT = int(input2.get())
		MINES = int(input3.get())
		
		if BOARD_WIDTH<=5 or BOARD_HEIGHT<=5 or MINES<=5:
			raise Exception
		if BOARD_WIDTH*BOARD_HEIGHT - 9 < MINES:
			raise Exception
		if BOARD_WIDTH>=100 or BOARD_HEIGHT>=100:
			raise Exception
			
		master.destroy()
		
	except Exception:
		input1.delete(0, tkinter.END)
		input2.delete(0, tkinter.END)
		input3.delete(0, tkinter.END)
		master.geometry('280x125')
		errortext.grid(row=4, column=0, columnspan=2)

tkinter.Button(master, text='proceed', width=15, command=proceed).grid(row=3, column=0, columnspan=2, pady=5)

master.mainloop()

with open("comms.txt", "w") as filename:
	filename.write(str(BOARD_WIDTH) + ' ' + str(BOARD_HEIGHT) + ' ' + str(MINES))
