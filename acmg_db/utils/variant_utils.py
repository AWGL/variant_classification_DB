from suds.client import Client
import hashlib
import re

"""
Various functions for dealing with variants inputted by the user.

"""


def get_variant_hash(chromosome, pos, ref,alt):
	"""
	Generates a sha256 hash of the variant. Used as promary key in Variant model.
	Input: chromosome, pos, ref,alt - self explanatory
	Output:
	hash_id = The sha256 hash of the chromosome + " " + pos + " " + ref + " " + alt
	Note The space between the 4 inputs. This stops problem of Chr1 12 A G and Chr11 2 A G being same hash e.g. hash(Chr112AG)
	"""

	hash_string = bytes('{chr}-{pos}-{ref}-{alt}'.format(chr =chromosome, pos=pos, ref=ref, alt=alt), 'utf-8')

	hash_id = hashlib.sha256(hash_string).hexdigest()

	return hash_id


def process_variant_input(variant_input):
	"""
	Split the inputted variant e.g. 17:41197732G>A into it's components.

	"""

	chromosome = variant_input.split(':')[0]

	position = re.findall('\d+',variant_input.split(':')[1])[0]

	ref = re.sub('[0-9]', '', variant_input.split(':')[1].split('>')[0])

	alt = re.sub('[0-9]', '', variant_input.split(':')[1].split('>')[1])

	var_hash = get_variant_hash(chromosome, position,ref, alt)

	key = '{chr}-{pos}-{ref}-{alt}'.format(chr =chromosome, pos=position, ref=ref, alt=alt)

	return ([var_hash, chromosome, position, ref, alt, key])


def get_variant_info_mutalzer(variant, mutalyzer_url, mutalyzer_build):
	"""
	Checks whether a variant is valid and gets some information about it \
	from Mutalyzer.

	Input:
	variant = String: A string representing the genomic description of a variant e.g. '17:41197732G>A'
	mutalyzer_url = String: A string showing the mutalyzer wdsl URL e.g. 'https://mutalyzer.nl/services/?wsdl'
	mutalyzer_build = String: A string showing the mutalyzer build e.g. 'hg19'

	Returns:

	list of lists showing whether the variant passed validation and information about a valid variant.

	"""

	try:

		# Make a connection to Mutalyzer
		client = Client(mutalyzer_url, cache=None)
		wsdl_o = client.service

	except:

		return [False, ['Could not connect to Mutalyzer website - Please contact Bioinformatics Department.']]

	# Convert the position to a number of various locations in the genome i.e. \
	# convert an entered genomic coordinate into transcript hgvs c


	# Build a variant for input to Mutalyzer 

	try:

		variant_info = process_variant_input(variant)

	except:

		return [False, ['process_variant_input() Error']]

	chromosome = variant_info[1]

	del_start = variant_info[2]

	ref = variant_info[3]

	alt = variant_info[4]

	del_end = int(del_start) + len(ref)-1

	variant_desc = f'chr{chromosome}:g.{del_start}_{del_end}del{ref}ins{alt}'

	try:

		mutalyzer_pos_response = wsdl_o.numberConversion(build=mutalyzer_build, variant=variant_desc)
		mutalyzer_pos_response = dict(mutalyzer_pos_response)

	except:

		return [False, ['Mutalyzer numberConversion Error: Mutalyzer does not recognise this as a valid variant.']]


	#Now check if we have a valid variant description

	try:

		mutalyzer_chrom_response = wsdl_o.chromAccession(build=mutalyzer_build, name = 'chr'+str(chromosome))

		new_variant_description = f'{mutalyzer_chrom_response}:g.{del_start}_{del_end}del{ref}ins{alt}'

		mutalyzer_light_response = wsdl_o.runMutalyzerLight(new_variant_description)

		mutalyzer_light_response = dict(mutalyzer_light_response)

		if mutalyzer_light_response['errors'] > 0:

			return [False, ['Mutalyzer Light Error: Error returned in response.']]

	except:

		return [False, ['Mutalyzer Light Error: Not a valid Variant.']]


	transcript_variant_list = mutalyzer_pos_response['string']

	try:

		first_variant = transcript_variant_list[0]

	except:

		return [False, ['Mutalyzer numberConversion Error: Not results']]


	return [True,[True]]












