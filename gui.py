from tkinter import Tk, Frame, StringVar, IntVar, Toplevel, BooleanVar
from tkinter import Button, Label, Radiobutton, Checkbutton
from tkinter.filedialog import askopenfilename
from report import Report
import time
from google_api import *
import re

# it draw the main frame
class MainFrame(Frame):
	def __init__(self):

		Frame.__init__(self)
		self.master.title('CSV Processor')
		self.master.rowconfigure(5, weight=1)
		self.master.columnconfigure(5, weight=1)
		self.grid(sticky='nesw')
		self.windows = []

		choose_file_label = Label(self, text='Choose The Input Data File')
		choose_file_label.grid(row=1,column=0, stick='w')

		button = Button(self, text="Browse Files", command=self.load_file, width=10)
		button.grid(row=1, column=1, stick='w')
		self.file_name ='data.csv'

		self.file_label_string = StringVar()
		self.file_label_string.set('File Not Chosen')
		file_label = Label(self, text='Chosen File : ')
		file_label.grid(row=2,column=0, stick='w')
		file_label1 = Label(self, textvariable=self.file_label_string)
		file_label1.grid(row=2,column=1, stick='w')

		choose_year_radio_label = Label(self, text='Choose A Year')
		choose_year_radio_label.grid(row=3, column=0, stick='w')

		self.year_radio_val = IntVar()
		self.year_radio_val.set(2018)
		year_radio_tuggle2018 = Radiobutton(self, text='2018', variable=self.year_radio_val, value=2018)
		year_radio_tuggle2018.grid(row=4, column=0, stick='w')

		year_radio_tuggle2019 = Radiobutton(self, text='2019', variable=self.year_radio_val, value=2019)
		year_radio_tuggle2019.grid(row=4, column=1, stick='w')


		choose_month_radio_label = Label(self, text='Choose A Month')
		choose_month_radio_label.grid(row=6, column=0, stick='w')

		self.month_radio_val = IntVar()
		self.month_radio_val.set(1)
		month_radio_tiggle_jan = Radiobutton(self, text="Jan", variable=self.month_radio_val, value=1)
		month_radio_tiggle_jan.grid(row=7, column=0, stick='w')

		month_radio_tiggle_jan = Radiobutton(self, text="Feb", variable=self.month_radio_val, value=2)
		month_radio_tiggle_jan.grid(row=7, column=1, stick='w')

		month_radio_tiggle_jan = Radiobutton(self, text="Mar", variable=self.month_radio_val, value=3)
		month_radio_tiggle_jan.grid(row=8, column=0, stick='w')	

		month_radio_tiggle_jan = Radiobutton(self, text="Apr", variable=self.month_radio_val, value=4)
		month_radio_tiggle_jan.grid(row=8, column=1, stick='w')

		month_radio_tiggle_jan = Radiobutton(self, text="May", variable=self.month_radio_val, value=5)
		month_radio_tiggle_jan.grid(row=9, column=0, stick='w')

		month_radio_tiggle_jan = Radiobutton(self, text="Jun", variable=self.month_radio_val, value=6)
		month_radio_tiggle_jan.grid(row=9, column=1, stick='w')	

		month_radio_tiggle_jan = Radiobutton(self, text="Jul", variable=self.month_radio_val, value=7)
		month_radio_tiggle_jan.grid(row=10, column=0, stick='w')

		month_radio_tiggle_jan = Radiobutton(self, text="Aug", variable=self.month_radio_val, value=8)
		month_radio_tiggle_jan.grid(row=10, column=1, stick='w')

		month_radio_tiggle_jan = Radiobutton(self, text="Sep", variable=self.month_radio_val, value=9)
		month_radio_tiggle_jan.grid(row=11, column=0, stick='w')	

		month_radio_tiggle_jan = Radiobutton(self, text="Oct", variable=self.month_radio_val, value=10)
		month_radio_tiggle_jan.grid(row=11, column=1, stick='w')

		month_radio_tiggle_jan = Radiobutton(self, text="Nov", variable=self.month_radio_val, value=11)
		month_radio_tiggle_jan.grid(row=12, column=0, stick='w')

		month_radio_tiggle_jan = Radiobutton(self, text="Dec", variable=self.month_radio_val, value=12)
		month_radio_tiggle_jan.grid(row=12, column=1, stick='w')	

		choose_month_period_radio_label = Label(self, text='Choose A Month Period')
		choose_month_period_radio_label.grid(row=13, column=0, stick='w')
		self.month_period_radio_val = IntVar()	
		self.month_period_radio_val.set(0)		
		month_period_radio_val115 = Radiobutton(self, text="1-15", variable=self.month_period_radio_val, value=0)
		month_period_radio_val115.grid(row=14, column=0, stick='w')

		month_period_radio_val16end = Radiobutton(self, text="16 to the end", variable=self.month_period_radio_val, value=1)
		month_period_radio_val16end.grid(row=14, column=1, stick='w')

		button = Button(self, text="Period Filter", command=self.filter, width=10)
		button.grid(row=20, column=0, stick='e')
	
	def filter(self):
		try:
			self.report = Report(self.file_name)
			self.staff_list = self.report.period_filter(
					self.year_radio_val.get(), 
					self.month_radio_val.get(),
					self.month_period_radio_val.get()
				)

			staff_checkboxes_window = Toplevel()
			staff_checkboxes_window.wm_title("Staff Choose")
			staff_vriable = StringVar()

			self.staff_radio_vals = []
			self.staff_radio_chk_all = BooleanVar()
			self.staff_radio_chk_all.set(False)

			row = 0
			col = 1 

			Label(staff_checkboxes_window, text='Choose The Staff').grid(column=0, row=0)

			for staff_item in self.staff_list:
				self.staff_radio_vals.append(StringVar())
				if self.staff_list.index(staff_item) % 10 == 0:
					row += 1
					col = 0
				else:
					col	+= 1

				Checkbutton(
						staff_checkboxes_window,
						variable=self.staff_radio_vals[self.staff_list.index(staff_item)],
						text=staff_item, 
						onvalue=staff_item, 
						offvalue=''
						
					).grid(row=row, column=col, stick='w')

			Checkbutton(
					staff_checkboxes_window,
					variable=self.staff_radio_chk_all,
					text='Check All Staff', 
					onvalue=True, 
					offvalue=False,
					command=self.check_all_staff
				).grid(row=len(self.staff_list) + 1, column=0, stick='w')


			Button(
					staff_checkboxes_window, 
					text="Apply", 
					command=self.apply_staff
				).grid(row=len(self.staff_list) + 1, column=1)

		except Exception as exc:
			print('cant run calculation {}'.format(exc))	

	def check_all_staff(self):
		if self.staff_radio_chk_all.get():
			[ 
				self.staff_radio_vals[self.staff_radio_vals.index(strv)]
					.set(self.staff_list[self.staff_radio_vals.index(strv)])
			 	for strv in self.staff_radio_vals
			]
		else:
			[strv.set('') for strv in self.staff_radio_vals]	
				
	# it marks all the needed staff in the checkboxes and quit of the gui (after quit it run the main work...)
	# we cant do it in the context of the gui. because the tkinter bloks everything ...
	# so we break from the tkinter context and do main work
	def apply_staff(self):
		self.stringify_staff_radio_vals = [strv.get() for strv in self.staff_radio_vals]
		self.quit()


	# it read the input file
	def load_file(self):
	    self.file_name = askopenfilename(filetypes=(("CSV", "*.csv"),
	                                       ("All files", "*.*") ))
	    try:
	    	print('input file : {}'.format(self.file_name))
	    	self.file_label_string.set(self.file_name)
	    except Exception as exc:
	    	showerror("Open Source File" , "Failed to read file\n {} :: {}".format( self.file_name, exc))
	    return

def main():
	# it runs the job step by step
	MF = MainFrame()
	MF.mainloop()

	# main work begun here
	R = Report(MF.file_name)
	print('FILTER: period')
	R.period_filter(
					MF.year_radio_val.get(), 
					MF.month_radio_val.get(),
					MF.month_period_radio_val.get()
				)
	print('FILTER: staff_filter')
	R.staff_filter(list(filter(lambda a: a != '', MF.stringify_staff_radio_vals)))	
	print('FILTER: general')
	R.run()
	print('FILTER: continius_time')
	R.continius_time_filter()
	print('FILTER: overlaps')
	R.time_overlaps_filter()
	print('SAVE files')
	output_file_names = R.save()
	return output_file_names

if __name__ == '__main__':
	output_file_names = main()
	print('filenames {}'.format(output_file_names))

	# it saves the reports to the google
	for j, output_file_name in output_file_names.items():
		splitted_file_name = re.sub('[^A-Za-z0-9 -]+', '--', output_file_name).split('--')
		to_google_drive(output_file_name, splitted_file_name[-2].replace('  ',':'))