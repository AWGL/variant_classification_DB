"""
This code implements the ACMG algorithm for classifying variants.

https://www.acmg.net/docs/Standards_Guidelines_for_the_Interpretation_of_Sequence_Variants.pdf

The code consists of two functions:

1) valid_input
2) classify

The classification algorithm has been rewritten from the earlier versions because if didnt always 
call VUS-conflicting evidence if there was only mild evidence on one side. All classification is 
now done within the one function.
"""

# specify guideline version so that record can be made in database
# NOTE: change this variable if you make any changes to the guidelines (max_length 20)

guideline_version = 'ACGS 2019'


def valid_input(input):
	"""
	Input: list
	Output: True or False

	Checks whether the user input is valid.
	The user input should be a list containing the classification codes in the possible_classifications list.
	The user input should contain no duplicates.
	The user input should not be a empty list

	"""
	possible_classifications = [
		'PVS1', 'PS1', 'PS2', 'PS3', 'PS4', 'PS4_M', 'PS4_P', 
		'PM1', 'PM2', 'PM3', 'PM4', 'PM5', 'PM6', 
		'PP1', 'PP2', 'PP3', 'PP4', 'PP5',
		'BA1', 'BS1', 'BS2', 'BS3', 'BS4', 
		'BP1', 'BP2', 'BP3', 'BP4', 'BP5', 'BP6', 'BP7'
	]

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

	#Have PS4, PS4_M, PS4_P been applied together?
	n = 0
	if 'PS4' in input:
		n += 1
	if 'PS4_M' in input:
		n += 1
	if 'PS4_P' in input:
		n += 1
	if n > 1:
		return False

	#Input is a valid list and no invalid classifactions and no duplicates so return True
	return True


def classify(user_classification):
	'''
	Takes a list of ACMG codes and calculates a classification.

	Input: tuple of acmg code followed by the code strength e.g. ('PVS1', 'PV')
	Output: A string of a number corresponding to a classification - 
	    0 - benign
		1 - likely benign
		2 - vus - criteria not met
		3 - vus - conflicting criteria
		4 - likely pathogenic
		5 - pathogenic
	'''
	# make empty dict to count numbers of each code
	classification_dict = {
		'PV': 0,
		'PS': 0,
		'PM': 0,
		'PP': 0,
		'BA': 0,
		'BS': 0,
		'BP': 0
	}

	# count number of each code
	for code in user_classification:
		strength = code[1]
		classification_dict[strength] += 1

	PVS1_count = classification_dict['PV']
	PS_count = classification_dict['PS']
	PM_count = classification_dict['PM']
	PP_count = classification_dict['PP']
	pathogenic_count = PVS1_count + PS_count + PM_count + PP_count

	BA_count = classification_dict['BA']
	BS_count = classification_dict['BS']
	BP_count = classification_dict['BP']
	benign_count = BA_count + BS_count + BP_count

	# apply acmg rules
	# contradictory evidence
	if pathogenic_count > 0 and benign_count > 0:
		return '3'
	
	# benign
	elif BA_count >= 1:
		return '0'

	elif BS_count >= 2:
		return '0'

	# likely benign
	elif BS_count == 1 and BP_count == 1:
		return '1'

	elif BP_count >= 2:
		return '1'

	# pathogenic
	if PVS1_count == 1 and PS_count >= 1:
		return '5'

	elif PVS1_count == 1 and PM_count >= 1:
		return '5'

	elif PVS1_count == 1 and PP_count >= 2:
		return '5'

	elif PS_count >= 3:
		return '5'

	elif PS_count == 1 and PM_count >= 3:
		return '5'

	elif PS_count == 1 and (PM_count == 2 and PP_count >= 2):
		return '5'

	elif PS_count == 1 and (PM_count == 1 and PP_count >= 4):
		return '5'

	# likely pathogenic
	elif PS_count == 2:
		return '4'

	elif PS_count == 1 and (PM_count == 1 or PM_count == 2):
		return '4'

	elif PS_count == 1 and PP_count >= 2:
		return '4'

	elif PM_count >= 3:
		return '4'

	elif PM_count == 2 and PP_count >= 2:
		return '4'

	elif PM_count == 1 and PP_count >= 4:
		return '4'

	# vus - criteria not met
	else:
		return '2'


def main():
	#for debugging
	user_classifications = ['PVS1', 'BS1', 'PS4', 'PS2']
	print(classify(user_classifications))


if __name__ == "__main__":
	main()
