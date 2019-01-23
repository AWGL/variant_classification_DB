"""
This code implements the ACMG algorithm for classifying variants.

https://www.acmg.net/docs/Standards_Guidelines_for_the_Interpretation_of_Sequence_Variants.pdf

The code consists of five functions:

1) valid_input
2) get_pathogenicity_classification
3) get_benign_classification
4) get_final_classification
5) classify

The get_pathogenicity_classification and get_benign_classification each take a list as input e.g. ['PVS1', 'PS1', 'PP1', 'BS'].

This list contains the classifications that the user has made. These are then combined using the ACMG algorithm to compute a pathogenicity and benign classification.

The pathogencity and benign classifications are then combined to produce a final classification using the get_final_classification function.

The valid input function ensures that the user has entered valid data.

The final classify wraps functions 1-4 in a simpler interface.

"""

def valid_input(input):

	"""
	Input: list
	Output: True or False

	Checks whether the user input is valid.

	The user input should be a list containing the classification codes in the possible_classifications list.

	The user input should contain no duplicates.

	The user input should not be a empty list

	"""

	possible_classifications = ['PVS1', 'PS1', 'PS2', 'PS3', 'PS4', 'PM1', 'PM2', 'PM3', 'PM4', 'PM5', 'PM6', 'PP1', 'PP2', 'PP3', 'PP4', 'PP5',

								'BA1', 'BS1', 'BS2', 'BS3', 'BS4', 'BP1', 'BP2', 'BP3', 'BP4', 'BP5', 'BP6', 'BP7']

	
	#Have we got a list?
	if type(input) is not list:

		return False

	#Have we got an empty list?
	if len(input) ==0:

		return False


	#Have we got any classifications that are not valid e.g. BP8?
	for classification in input:

		if classification not in possible_classifications:

			return False

	#Have we got any duplicates?

	if len(input) != len(set(input)):

		return False


	#Input is a valid list and no invalid classifactions and no duplicates so return True
	return True





def get_pathogenicity_classification(user_classifications):

	"""
	This function calculates the pathogencity classifcation given the user input
	
	Output is a string containing the classification.

	"""

	middle_classifications = {'PV' :0, 'PS':0, 'PM':0,'PP' :0}

	#go through each of the classifcations that the user has provided and update the middle_classifcations dictionary

	for classification in user_classifications: 

		if classification[:2] in middle_classifications: #only look at first two chars as user classifications are longer

			middle_classifications[classification[:2]] +=1

	PVS1_count = middle_classifications['PV']
	PS_count = middle_classifications['PS']
	PM_count = middle_classifications['PM']
	PP_count = middle_classifications['PP']

	if PVS1_count ==1 and PS_count >=1:

		return "Pathogenic (Ia)" 

	elif PVS1_count ==1 and PM_count >=2:

		return "Pathogenic (Ib)"

	elif PVS1_count ==1 and (PM_count ==1 and PP_count ==1):		

		return "Pathogenic (Ic)"

	elif PVS1_count ==1 and PP_count >=2:		

		return "Pathogenic (Id)"

	elif PS_count >=2:

		return "Pathogenic (II)"

	elif PS_count ==1 and PM_count >=3:

		return "Pathogenic (IIIa)"

	elif PS_count ==1 and (PM_count ==2 and PP_count >=2):

		return "Pathogenic (IIIb)"

	elif PS_count ==1 and (PM_count ==1 and PP_count >=4):

		return "Pathogenic (IIIc)"

	elif PVS1_count ==1 and PM_count ==1:

		return "Likely Pathogenic (I)"

	elif PS_count ==1 and (PM_count ==1 or PM_count ==2):

		return "Likely Pathogenic (II)"

	elif PS_count ==1 and PP_count >=2:

		return "Likely Pathogenic (III)"

	elif PM_count >=3:

		return "Likely Pathogenic (IV)"

	elif PM_count ==2 and PP_count >=2:

		return "Likely Pathogenic (V)"

	elif PM_count ==1 and PP_count >=4:

		return "Likely Pathogenic (VI)"

	else:

		return "VUS"





def get_benign_classification(user_classifications):

	"""
	This function calculates the benign classifcation given the user input
	
	Output is a string containing the classification.

	"""

	middle_classifications = {'BA' :0, 'BS':0, 'BP':0}

	#go through each of the classifcations that the user has provided and update the middle_classifcations dictionary

	for classification in user_classifications:

		if classification[:2] in middle_classifications:

			middle_classifications[classification[:2]] +=1

	BA_count = middle_classifications['BA']
	BS_count = middle_classifications['BS']
	BP_count = middle_classifications['BP']


	if BA_count ==1:

		return "Benign (I)"

	elif BS_count >=2:

		return "Benign (II)"

	elif BS_count ==1 and BP_count ==1:

		return "Likely Benign (I)"

	elif BP_count >=2:

		return "Likely Benign (II)"

	else:

		return "VUS"



def get_final_classification(path_classification, benign_classification):

	"""
	This function combines the pathogencity and benign classifcations to produce a final classifcation


	Output is a string containing the final classification

	"""


	if path_classification != "VUS" and benign_classification == "VUS": #if the pathogenicity rating has been given and there is no benign classification then final = pathogenicity classification

		return path_classification

	elif path_classification == "VUS" and benign_classification != "VUS": #if the benign rating has been given and there is no pathogenicity classification then final = benign classification

		return benign_classification

	elif path_classification != "VUS" and benign_classification != "VUS": #if both the pathogenicity and benign classifcation have been given then there is conflicting evidence.

		return "VUS - contradictory evidence provided"

	else:

		return "VUS - criteria not met" #neither have been set so we return VUS

def adjust_strength(user_classifications):

	"""
	Takes a user list of classifications such as [('PVS1', 'PS'), ('PS1', 'PS')]] \
	where the first item in the tuple is the ACMG tag and the second is the strength.
	and adjusts the strength of the ACMG tags if needed.

	Input:

	user_classifications: list: e.g. [('PVS1', 'PS'), ('PS1', 'PS')]]

	Output:

	updated_classifications: list:  e.g. [PSS1, PS1]

	"""

	updated_classifications = []

	for classification in user_classifications:


		acmg_code = classification[0]
		strength = classification[1]
				 
		# if the furst two letters do not match the strength.
		if strength != acmg_code[:2]:

			new_acmg_code = strength + acmg_code[2:]

			updated_classifications.append(new_acmg_code)

		else:

			updated_classifications.append(acmg_code)

	return updated_classifications





def classify(user_classifications):
	"""
	Combine the functions and calculate final class

	"""

	pathogenic_class = get_pathogenicity_classification(user_classifications)
	benign_class = get_benign_classification(user_classifications)

	final_class = get_final_classification(pathogenic_class, benign_class)

	return final_class



def main():

	#for debugging
	user_classifications = ['PVS1', 'BS1', 'PS4', 'PS2']

	path_rating = get_pathogenicity_classification(user_classifications)
	benign_rating = get_benign_classification(user_classifications)

	print (classify(user_classifications))


if __name__ == "__main__":

	main()
