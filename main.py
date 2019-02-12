#!usr/bin/env

'''
Python module to generate aggregate data from resolution bot 2019 study.

author: Abhijeet Agnihotri
'''

import csv
import re
import json
import matplotlib.pyplot as plt

ALL_DATES = ['2019-01-14', '2019-01-16', '2019-01-18', '2019-01-23', '2019-01-25', '2019-01-28', '2019-01-30', '2019-02-01']
STARTING_DATE = ALL_DATES[0]
CSV_FILE = 'UPDATED_ResoBot_chat_history.csv'
JSON_FILE = 'speech.json'


def read_from_json(string, json_file_name):
	with open(json_file_name) as json_file:
		data = json.load(json_file)
	for x in data:
		if data[x]["name"] == string:
			return data[x]["data"]
	return 0


def search_string_in_json(string, json_file_name):
	with open(json_file_name) as json_file:
		data = json.load(json_file)
	for i in data:
		for elem in data[i]["data"]:
			if elem == string:
				return True
	return False


def chat_history_parsing(all_dates, csv_file_name, json_file_name):

	list_of_speech_commands = ["START", "END"]

	overall_commands = {"START":0, "END":0, "USER_TYPED_COMMANDS": 0, "BUTTON_COMMANDS": 0}
	interstitial_commands =  {"USER_TYPED_COMMANDS": 0, "BUTTON_COMMANDS": 0}
	all_dates_data = dict()
	all_interactions = []
	loop = 0
	
	for date in all_dates:
		total_commands_for_this_date = {"START":0, "END":0, "USER_TYPED_COMMANDS": 0, "BUTTON_COMMANDS": 0}
	
		# Open the chat history
		with open(csv_file_name) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			
			interaction_in_progress = False
			interaction_length = 0
			current_interaction_id = 'D0T0P0'

			user_typed_commands_in_this_interaction = 0
			button_commands_in_this_interaction = 0

			for row in csv_reader:

				if date == row[0][:10]:
					last = row
					speech_data = row[1]

					#  interaction has 'STARTED'
					if speech_data == list_of_speech_commands[0]:
						overall_commands[speech_data] += 1
						total_commands_for_this_date[speech_data] +=1
						interaction_in_progress = True
						current_interaction_id = row[2]

					# interaction has 'ENDED'
					elif speech_data == list_of_speech_commands[1]:
						overall_commands[speech_data] += 1
						total_commands_for_this_date[speech_data] +=1

						# making sure the end of the same participant
						if current_interaction_id == row[2]:
							interaction_in_progress = False
							all_interactions.append({'ID': current_interaction_id, 'INTERACTON_LENGTH': 
								interaction_length, 'USER_TYPED_COMMANDS': user_typed_commands_in_this_interaction, 
								'BUTTON_COMMANDS': button_commands_in_this_interaction})
							interaction_length = 0
							user_typed_commands_in_this_interaction = 0
							button_commands_in_this_interaction = 0

					if row[2] != '':
						speech_data += row[2]

					# within an ongoing interaction
					if interaction_in_progress:
						interaction_length += 1

						if search_string_in_json(speech_data, json_file_name):
							# found the speech command as a button
							overall_commands["BUTTON_COMMANDS"] += 1
							total_commands_for_this_date["BUTTON_COMMANDS"] +=1
							button_commands_in_this_interaction += 1
						elif speech_data.isdigit():
							pass
						elif speech_data[:12] == "User Pressed":
							pass
						else:
							# had typed the following command
							overall_commands["USER_TYPED_COMMANDS"] += 1
							total_commands_for_this_date["USER_TYPED_COMMANDS"] +=1
							user_typed_commands_in_this_interaction += 1
					else:
						if search_string_in_json(speech_data, json_file_name):
							# found the speech command as a button
							interstitial_commands["BUTTON_COMMANDS"] += 1
						elif speech_data.isdigit():
							pass
						# elif speech_data[:12] == "User Pressed":
						# 	pass
						else:
							# had typed the following command
							interstitial_commands["USER_TYPED_COMMANDS"] += 1


		all_dates_data[date] = total_commands_for_this_date

	return overall_commands, interstitial_commands, all_dates_data, all_interactions


if __name__ == '__main__':

	overall_commands, interstitial_commands, all_dates_data, all_interactions = chat_history_parsing(ALL_DATES, CSV_FILE, JSON_FILE)
	user_typed_commands = overall_commands['USER_TYPED_COMMANDS']
	button_commands = overall_commands['BUTTON_COMMANDS']
	print('OVERALL: {}\n\t%_USER_TYPED: {}\n\t%_BUTTON: {}'.format(overall_commands, round(100.0*user_typed_commands/(user_typed_commands + button_commands), 3), round(100.0*button_commands/(user_typed_commands + button_commands), 3)))

	user_typed_commands = interstitial_commands['USER_TYPED_COMMANDS']
	button_commands = interstitial_commands['BUTTON_COMMANDS']
	print('\nINTERSTITIALS: {}\n\t%_USER_TYPED: {}\n\t%_BUTTON: {}'.format(interstitial_commands, round(100.0*user_typed_commands/(user_typed_commands + button_commands), 3), round(100.0*button_commands/(user_typed_commands + button_commands), 3)))

	for i, date in all_dates_data.items():
		print('\nDATE: {} and DATA: {}'.format(i, date))
		user_typed_commands = all_dates_data[i]['USER_TYPED_COMMANDS']
		button_commands = all_dates_data[i]['BUTTON_COMMANDS']
		print('\t%_USER_TYPED: {}\n\t%_BUTTON: {}'.format(round(100.0*user_typed_commands/(user_typed_commands + button_commands), 3), round(100.0*button_commands/(user_typed_commands + button_commands), 3)))

	with open('python_deviation_data.csv', mode='w') as file:
		file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		file_writer.writerow(['Day', 'Trial', 'Participant', '# User-typed commands', '# Button commands', '% User_typed_commands', '% Button commands'])

	for interaction in all_interactions:
		interaction_id = interaction['ID']
		day, trial, participant = (re.findall('\d+', interaction_id ))
		# print(day, trial, participant)
		user_typed_commands = interaction['USER_TYPED_COMMANDS']
		button_commands = interaction['BUTTON_COMMANDS']
		print('\t%_USER_TYPED: {}\n\t%_BUTTON: {}'.format(round(100.0*user_typed_commands/(user_typed_commands + button_commands), 3), round(100.0*button_commands/(user_typed_commands + button_commands), 3)))

		with open('python_deviation_data.csv', mode='a') as file:
			file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			file_writer.writerow([day, trial, participant, user_typed_commands, button_commands, round((100.0*user_typed_commands/(user_typed_commands + button_commands)), 3), round((100.0*button_commands/(user_typed_commands + button_commands)), 3)])
