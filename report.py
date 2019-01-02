import pandas as pd
import numpy as np
import datetime
from datetime import timedelta, date
import os
import calendar

class Report():

	# it sets the input file, current time and output folder
	def __init__(self, input_file):
		self.input_file = input_file
		self.output_path = 'reports'
		self.curr_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

	# it just make a folder
	def create_folder(self, directory):
		if not os.path.exists(directory):
			os.makedirs(directory)

	# it filter our data by time 
	def period_filter(self, year, month, month_period):
		self.filter_year = year
		self.filter_month = month
		
		# read the input file
		data = pd.read_csv(self.input_file)

		# if we have the MatRef instead of MatterRef - we need to copy it and do the work with the copied column
		try:
			# try to copy bad named column to 
			data['MatterRef'] = data['MatRef']
		except Exception as exc:
			print('can not rename MatRef to MatterRef. Maybe the column already with MatterRef name. err: {}'.format(exc))

		# change the type of it to the datetime  and index all the data by Bill Date column (ascend)
		data['Bill Date'] = pd.to_datetime(data['Bill Date'])
		data.index = data['Bill Date']

		# make the common columns End time and Time_1 with start datetime and end datetime
		data['Time'] = data['Time'].astype('str')
		data['End Time'] = data['End Time'].astype('str')
		data['Bill Date'] = data['Bill Date'].astype('str')
		data['Time_1'] = pd.to_datetime(data['Bill Date'] + ' ' + data['Time'])
		data = data.sort_values('Time_1')
		data['End Time_1'] = pd.to_datetime(data['Bill Date'] + ' ' + data['End Time'])

		# make the error column (initialize it by blank)
		data['Error Type'] = ' '

		# this is the magic: we fill the blank cell as '0', make the type as string. 
		# do something like this with the MatterCode column
		data['POS #'].fillna('0', inplace=True)
		data['POS #'] = data['POS #'].astype('str')
		
		data['MatterCode'].fillna('Null', inplace=True)
		data['MatterCode'] = data['MatterCode'].astype('str')
		data['MatterCode'].replace('Null', '', inplace=True)

		# replace the comma symbol to point symbol and change the format as float 
		try:
			data['Dur/Qty'] = data['Dur/Qty'].apply(lambda x : x.replace(",", '.')).astype('float')
		except Exception as exc:
			print('err when convert Dur/Qty to float {}'.format(exc))	

		# name of the time period
		self.per_name=''

		# gets the month range
		(_, month_range) =  calendar.monthrange(self.filter_year, self.filter_month)

		# init the program name
		if month_period == 0:
			self.program_type = 'CMH'
		elif (month_period == 1) and (month_range == 30):
			self.program_type = 'RC'
		elif (month_period == 1) and (month_range == 31):
			self.program_type = 'HC'	

		# filter the input data by the period year, month and the part of the month
		if month_period == 0:
			self.per_name='01-15'
			data_time_filtered = data['{}-{}-1'.format(self.filter_year, self.filter_month):'{}-{}-15'.format(self.filter_year, self.filter_month)]

		if month_period == 1: 
			self.per_name='16-{}'.format(month_range)
			data_time_filtered = data['{}-{}-16'.format(self.filter_year, self.filter_month):'{}-{}'.format(self.filter_year, self.filter_month)]
	
		self.data = data_time_filtered

		# we return the only unique Staff of this filtered data (it needed to gui for make the staff checkboxes) 
		return data_time_filtered['Staff'].drop_duplicates().tolist() 

	# devide the data by staff (it makes the few arrays with the staff name labeled)
	def staff_filter(self, chosen_staff):
		self.chosen_staff = chosen_staff

		self.data_staff_divided = []

		for ch_s in self.chosen_staff:

			self.data_staff_divided.append(
					self.data[
						self.data['Staff'] == ch_s
					]
				)

	# apply the time overlaps filter
	def time_overlaps_filter(self):
		for d in self.data_staff_divided:
			for time, end_time, pos in zip(d['Time_1'],d['End Time_1'], d['POS #']):

				d.loc[
					(
						(((time < d['Time_1']) & (end_time > d['Time_1']) & (end_time < d['End Time_1'])) 
						| ((time > d['Time_1']) & (time < d['End Time_1']) & (end_time > d['End Time_1']))
						| ((time < d['Time_1']) & (end_time > d['End Time_1'] ))
						# | (time == d['Time_1']) 
						| ((time == d['Time_1']) & (d['POS #'] != pos))
						| ((end_time == d['End Time_1']) & (d['POS #'] != pos))
						# | (end_time == )
						| ((time == d['Time_1']) & (end_time == d['End Time_1']) & (d['POS #'] != pos))
						)

					),'Error Type'			
				] += '[Time Overlaps] '

	# make the continius time filter
	def continius_time_filter(self):
		for d in self.data_staff_divided:
			d.loc[
				(~d['Time_1'].isin(d['End Time_1']))
				& (d['Bill Date'] == d.shift(1)['Bill Date']) 
				,'Error Type'
			] += '[Time Not Continuous] '

			d.loc[
				(~d['End Time_1'].isin(d['Time_1']))
				& (d['Bill Date'] == d.shift(-1)['Bill Date']) 
				,'Error Type'
			] += '[Time Not Continuous] '			

	def daterange(self, date1, date2):
		for n in range(int ((date2 - date1).days)+1):
			yield date1 + timedelta(n)	

	# save the reports
	def save(self):
		# make the name pattern of the reports
		name_pattern = '{}-{:02d}   {} '.format(self.filter_year,self.filter_month, self.per_name)
		# self.create_folder(os.path.join(self.output_path,self.curr_time))
		# create the folders for the reports
		self.create_folder(os.path.join(self.output_path,'{} {}'.format(name_pattern, self.program_type)))
		self.create_folder(os.path.join(self.output_path,'dirty',self.curr_time))

		output_files = {}
		self.writers = {}
		
		# make the excel writers for all staff
		for staff_name in self.data_staff_divided:
			output_files[staff_name['Staff'][0]] = os.path.join(self.output_path,'{} {}'.format(name_pattern, self.program_type),'{} {}.xlsx'.format(name_pattern, staff_name['Staff'][0]))
			self.writers[staff_name['Staff'][0]] = pd.ExcelWriter(output_files[staff_name['Staff'][0]], engine='xlsxwriter') 

		output_files['ALL'] = os.path.join(self.output_path,'{} {}'.format(name_pattern, self.program_type),'{} ALL.xlsx'.format(name_pattern, self.per_name))		
		self.all_writer = pd.ExcelWriter(output_files['ALL'], engine='xlsxwriter')

		# save the reports and return the file names to the gui
		# the gui will launch the google drive saver for this files
		self.save_error_reports()
		self.save_result_reports()	
		return output_files			

	# save
	def save_result_reports(self):
		# make the dummies for all formatted columns in the result reports
		all_result_sheet_name = 'result ALL'

		bill_codes = [
			'HCP', 'RCP', 'CMHP', 
			'-PTO', '-LCH', '-HOL', 
			'-BRK', '-SCK', '-VAC', 
			'-JDY', '-BVM', 'MNG', 
			'DEVH', '$HC', '$RC', 
			'$CMH', '$FS', '$NDV'
		]

		bill_codes_pd = pd.DataFrame({'Work Activity': bill_codes})

		properties_list = [
			'Archstone Apartments', 'Briarwood Co-op', 'Camden Co-op',	
			'Casa Feliz Studios', 'De La Cruz Co-op', 'Edenvale Apartments',
			'Fourth Street Apartments',	'Gish Apartments','Jasmine Square', 
			'Japantown','Monterey Villa', 'Rivertown Apartments',
			'San Antonio Place', 'Villa Esperanza', '1585 Studios'
		]	

		properties_list_pd = pd.DataFrame({'Properties List': properties_list})	

		bill_codes_pd.to_excel(self.all_writer, sheet_name=all_result_sheet_name, index=False, columns=['Work Activity'])
		properties_list_pd.to_excel(self.all_writer, sheet_name=all_result_sheet_name, startrow=23, index=False, header=None, columns=['Properties List'])
		staff_counter = 1

		# for all staff
		for d in self.data_staff_divided:
			# make additional dummies for the each staff to formattted columns in the result reports
			work_activity = pd.DataFrame({'Work Activity': bill_codes, 'Hours': [0] * len(bill_codes) })
			work_activity['Hours'] = work_activity['Hours'].astype('float')

			for bc in range(len(bill_codes)):
				work_activity['Hours'][bc] = d[d['Bill Code'] == work_activity['Work Activity'][bc] ]['Dur/Qty'].sum()


			total_reg_hrs = {
				'TOTAL REG HRS':['TOTAL REG HRS'],
				'total': [work_activity[~work_activity['Work Activity'].isin( ['-LCH']) ]['Hours'].sum()], 
				}

			total_reg_hrs_pd = pd.DataFrame(total_reg_hrs)	
			total_billing_pers_pd = pd.DataFrame(
				{
					'Billing Percentage':['Billing Percentage'],
					'persent' : ['{0:.0f}%'.format(
					((work_activity[work_activity['Work Activity'].isin(['$HC','$RC','$CMH','$FS', '$NDV']) ]['Hours'].sum()) 
						/ (work_activity[work_activity['Work Activity'].isin(['$HC','$RC','$CMH','$FS', '$NDV']) ]['Hours'].sum() 
							+ work_activity[work_activity['Work Activity'].isin(['HCP', 'RCP', 'CMHP']) ]['Hours'].sum())).item() * 100 )]
					}
				)

			start_date = datetime.datetime.strptime(d['Bill Date'].head(1).item(), '%Y-%m-%d')	
			end_date = datetime.datetime.strptime(d['Bill Date'].tail(1).item(), '%Y-%m-%d')	

			date_list = [d.strftime("%Y-%m-%d") for d in self.daterange(start_date, end_date)]
			pd_end_date = pd.DataFrame({'end_date': [date_list[-1]]})
			date_period = pd.DataFrame({'date': date_list, 'hours':  [0] * len(date_list) })

			for bc in range(len(date_list)):
				date_period['hours'][bc] = d[ 
					(d['Bill Date'] == date_period['date'][bc]) 
					& (d['Bill Code'] != '-LCH') 
				]['Dur/Qty'].sum()  



			prop_hours_list = [0] * len(properties_list)
			

			for i, prop in enumerate(properties_list):
				prop_hours_list[i]  = '{0:.2f}'.format( d[(d['Property'] == prop) & (d['Bill Code'] == '$RC') ]['Dur/Qty'].sum())
	
			properties = pd.DataFrame({'properties': properties_list, 'hours': prop_hours_list})
			properties['hours'] = properties['hours'].astype(float)

			properties_total = properties['hours'].sum()
			properties_total_pd = pd.DataFrame({'properties_total':[properties_total]})

			work_activity_total_list = ['Reg. Hours', 'Sick', 'Vacation', 'Holiday', 'Total:']
			work_activity_total_list_vals = [0] * len(work_activity_total_list)

			work_activity_total_list_vals[0] = work_activity[
						~work_activity['Work Activity'].isin(['-LCH', 'PTO', 'HOL', '-SCK', '-VAC']) 
						]['Hours'].sum()

			work_activity_total_list_vals[1] = work_activity[work_activity['Work Activity'] == '-SCK' ]['Hours'].item()
			work_activity_total_list_vals[2] = work_activity[work_activity['Work Activity'] == '-VAC' ]['Hours'].item()		
			work_activity_total_list_vals[3] = work_activity[work_activity['Work Activity'] == '-HOL' ]['Hours'].item()
			work_activity_total_list_vals[4] = sum(work_activity_total_list_vals)

			work_activity_total = pd.DataFrame({'name': work_activity_total_list, 'val': work_activity_total_list_vals})

			summ_sheet_name = 'summary_{}'.format(d['Staff'][0])

			law_statement = pd.DataFrame({'law_statement': ['I declare, under the penalty of law, that the facts \n on this sheet are true and correct.']})
			emploee_date = pd.DataFrame({'emploee_date': ['Employee'], 'empty': [''], 'empty1': [''], 'date': ['Date']})
			managing_supervisor = pd.DataFrame({'Managing_Supervisor': ['Managing Supervisor'],'empty': [''], 'empty1': [''], 'date': ['Date']})

			# save the formatted columns to the result report lists
			work_activity.to_excel(self.writers[d['Staff'][0]], sheet_name=summ_sheet_name, index=False, columns=['Work Activity', 'Hours'])
			date_period.to_excel(self.writers[d['Staff'][0]], sheet_name=summ_sheet_name, startrow=2, startcol=3, index=False, header=None, columns=['date', 'hours'])
			pd_end_date.to_excel(self.writers[d['Staff'][0]], sheet_name=summ_sheet_name, startcol=4, index=False, header=None)
			total_reg_hrs_pd.to_excel(self.writers[d['Staff'][0]], sheet_name=summ_sheet_name, startrow=20, index=False, header=None )
			total_billing_pers_pd.to_excel(self.writers[d['Staff'][0]], sheet_name=summ_sheet_name, startrow=21, index=False, header=None )
			properties.to_excel(self.writers[d['Staff'][0]], sheet_name=summ_sheet_name, startrow=23, index=False, header=None, columns=['properties', 'hours'])
			work_activity_total.to_excel(self.writers[d['Staff'][0]], sheet_name=summ_sheet_name, startrow=23, startcol=3, index=False, header=None, columns=['name', 'val'])
			# properties_total_pd.to_excel(self.writers[d['Staff'][0]], sheet_name=summ_sheet_name, startrow=38, startcol=2, index=False, header=None, columns=['properties_total'])
			law_statement.to_excel(self.writers[d['Staff'][0]], sheet_name=summ_sheet_name, startrow=40, startcol=0, index=False, header=None, columns=['law_statement'])
			emploee_date.to_excel(self.writers[d['Staff'][0]], sheet_name=summ_sheet_name, startrow=45, startcol=0, index=False, header=None, columns=['emploee_date', 'empty', 'empty1', 'date'])
			managing_supervisor.to_excel(self.writers[d['Staff'][0]], sheet_name=summ_sheet_name, startrow=49, startcol=0, index=False, header=None, columns=['Managing_Supervisor', 'empty', 'empty1', 'date'])
			# except Exception as exc:
			# 	print('save results with dataframe : {}, \n {}'.format(d, exc))
			# properties_list_pd.to_excel(self.all_writer, sheet_name=all_result_sheet_name, startrow=23, index=False, header=None, columns=['Properties List'])
			staff_name_pd = pd.DataFrame({'Staff Name': [d['Staff'][0]]})
			staff_name_pd.to_excel(self.all_writer, sheet_name=all_result_sheet_name, startrow=0, startcol=staff_counter, index=False, header=None, columns=['Staff Name'])
			work_activity.to_excel(self.all_writer, sheet_name=all_result_sheet_name, startrow=1, startcol=staff_counter, index=False, header=None, columns=['Hours'])


			total_reg_hrs_pd.to_excel(self.all_writer, sheet_name=all_result_sheet_name, startrow=20, index=False, header=None, columns=['TOTAL REG HRS'] )
			total_billing_pers_pd.to_excel(self.all_writer, sheet_name=all_result_sheet_name, startrow=21, index=False, header=None, columns=['Billing Percentage'] )
			total_reg_hrs_pd.to_excel(self.all_writer, sheet_name=all_result_sheet_name, startrow=20, startcol=staff_counter, index=False, header=None, columns=['total'])
			total_billing_pers_pd.to_excel(self.all_writer, sheet_name=all_result_sheet_name, startrow=21, startcol=staff_counter, index=False, header=None, columns=['persent'])

			properties.to_excel(self.all_writer, sheet_name=all_result_sheet_name, startrow=23, startcol=staff_counter, index=False, header=None, columns=['hours'])
		
			staff_counter += 1

	# save the errors
	def save_error_reports(self): 
		
		columns = [
				'Error Type','Staff','Description','Code','Bill Code','Bill Date','Time','End Time','Dur/Qty',
				'First Name','Last Name','UCI #','MatterRef','POS #','Property','MatterCode']
		
		err_log_all = []
		
		# for each stuff . make the dirty file (get all the data and marks the error rows)
		# and make the error result for each stuff
		for d in self.data_staff_divided:
			try:
				output_file = os.path.join(
					self.output_path, 'dirty', self.curr_time, 
					'{} result_dirty_{}.csv'.format(
							self.per_name,
							d['Staff'][0]
						)
					)
				d.to_csv(output_file, index=False, columns=columns)
				err_sh = d[d['Error Type'] != ' ']

				err_log_all.append(err_sh)

				err_sheet_name = 'errlog_{}'.format(d['Staff'][0])
				err_sh.to_excel(self.writers[d['Staff'][0]], sheet_name=err_sheet_name, index=False, columns=columns)
			except Exception as exc:	
				print('save err log with df : {} , \n {}'.format(d, exc))

		err_log_all_pd = pd.concat(err_log_all)	

		# make the error report for all stuff
		all_err_sheet_name = 'errlog ALL'
		
		err_log_all_pd.to_excel(self.all_writer, sheet_name=all_err_sheet_name, index=False, columns=columns)

	def run(self):
		# run the all conditions for the each stuff
		for d in self.data_staff_divided:
			# check each stuff for all of the conditions 
			try:
				d.loc[
						(
							(
							# (d['POS #'].isnull())
								(d['POS #'] == '0') 
								# & (d['Bill Code'].str.contains("\$"))
								 & (
								 	(d['Bill Code'].str.contains("$HC"))
								 	| (d['Bill Code'].str.contains("$RC"))
								 	| (d['Bill Code'].str.contains("$CMH"))
								 	)
							),'Error Type')
					] += '[POS missing] '

				d.loc[
						(
							(
								# (d['Bill Code'].str.contains("\$")) 
								(
									(d['Bill Code'].str.contains("$HC"))
									| (d['Bill Code'].str.contains("$RC"))
									| (d['Bill Code'].str.contains("$CMH"))   
									)
								& ((d['POS #'].str.len() !=8) 
									| (~d['POS #'].str.match(r'^(18|19).*')) 
									| (~d['POS #'].str.isnumeric()))
							),'Error Type')
					] += '[POS wrong format] '

				d.loc[
					(
						(
							d['Bill Code'] == '$RC') & 
							(d['Property'].isnull()
						)
					), 'Error Type'] += '[RC missing property] '

				d.loc[
					(
						( d['Code'] != d['Bill Code'] ) | 
						 (( d['Code'] == '$HC') & (d['MatterCode'].str.contains('HC') == False ) & (d['MatterRef'].str.contains('HC Matter') == False)) |
						 (( d['Code'] == '$RC') & (d['MatterCode'].str.contains('RC') == False) & ( d['MatterRef'].str.contains('RC Matter') == False )) |
						 (( d['Code'] == '$CMH') & (d['MatterCode'].str.contains('CMH') == False ) & ( d['MatterRef'].str.contains('CMH Matter') == False )) 


					) , 'Error Type'] += "[code/billcode/matcode/matref don't match] "		

				D = d.groupby('MatterRef')['POS #'].apply(lambda x: x.unique()).reset_index()
				D.loc[D['POS #'].str.len() > 1, 'err'] ='err'
				D = D.drop(D[(D['POS #'].str.len() <= 1)].index)

				d.loc[
					d['MatterRef'].isin(D['MatterRef']) 
					& (
						(d['Bill Code'] == '$HC') 
						| (d['Bill Code'] =='$RC') 
						| (d['Bill Code'] == '$CMH')
						) 
					& (d['Bill Code'] != '$FS'), 'Error Type'
					] += '[POS used by two+ clients] '

				D1 = d.groupby('POS #')['MatterRef'].apply(lambda x: x.unique()).reset_index()
				D1.loc[D1['MatterRef'].str.len() > 1, 'err'] ='err'
				D1 = D1.drop(D1[(D1['MatterRef'].str.len() <= 1)].index)

				d.loc[
					d['POS #'].isin(D1['POS #']) 
					& (
						(d['Bill Code'] == '$HC') 
						| (d['Bill Code'] =='$RC') 
						| (d['Bill Code'] == '$CMH')
						) 
					& (d['Bill Code'] != '$FS'), 'Error Type'
					] += '[Client has two+ POS] '
			except Exception as exc:	
				print('run error with dataframe : {} \n {}'.format(d, exc))

# this is a test of main staff
def main():
	# It gets the input file 
	R = Report('newdata2.csv')
	# sets a perios - YYY M (0:  1-15 days, 1: 16-to the end of month)
	R.period_filter(2018, 6, 0)
	# sets the STUFF names list 
	R.staff_filter([ 'RWR', 'RBG', 'RJL','RAS'])
	# runs the main work
	R.run()
	# apply the additional time filters
	R.continius_time_filter()
	R.time_overlaps_filter()
	# save the tresult
	R.save()

if __name__ == '__main__':
	main()	