from suds.client import Client
import hashlib
import re


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

	chromosome = variant_input.split(':')[0]

	position = re.findall('\d+',variant_input.split(':')[1])[0]

	ref = re.sub('[0-9]', '', variant_input.split(':')[1].split('>')[0])

	alt = re.sub('[0-9]', '', variant_input.split(':')[1].split('>')[1])

	var_hash = get_variant_hash(chromosome, position,ref, alt)

	key = '{chr}-{pos}-{ref}-{alt}'.format(chr =chromosome, pos=position, ref=ref, alt=alt)

	return (var_hash, chromosome, position, ref, alt, key)


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

	variant_info = process_variant_input(variant)

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

		return [False, ['Mutalyzer does not recognise this as a valid variant.']]


	#Now check if we have a valid variant description

	try:

		mutalyzer_chrom_response = wsdl_o.chromAccession(build=mutalyzer_build, name = 'chr'+str(chromosome))

		new_variant_description = f'{mutalyzer_chrom_response}:g.{del_start}_{del_end}del{ref}ins{alt}'

		mutalyzer_light_response = wsdl_o.runMutalyzerLight(new_variant_description)

		print (mutalyzer_light_response)

		mutalyzer_light_response = dict(mutalyzer_light_response)

		if mutalyzer_light_response['errors'] > 0:

			return [False, ['Mutalyzer does not recognise this as a valid variant.']]

	except:

		return [False, ['Mutalyzer does not recognise this as a valid variant.']]


	transcript_variant_list = mutalyzer_pos_response['string']

	print (transcript_variant_list)

	try:

		first_variant = transcript_variant_list[0]

	except:

		return [False, ['Mutalyzer does not recognise this as a valid variant.']]


	transcript_variant_info = []

	for transcript_variant in transcript_variant_list:

		if transcript_variant[0:2] != 'NR':

			mutalyzer_light_response =  wsdl_o.runMutalyzerLight(transcript_variant)

			mutalyzer_light_response = dict(mutalyzer_light_response)

			if mutalyzer_light_response['errors'] == 0:

				#Get corrrect hgvs c info

				hgvs_c = mutalyzer_light_response['transcriptDescriptions']

				if hgvs_c != None:

					hgvs_c = dict(hgvs_c)

					hgvs_c = hgvs_c['string'][0]

					if transcript_variant[0:3] != 'LRG':

							hgvsc_start = hgvs_c.split(':')[0]
							hgvsc_end = hgvs_c.split(':')[1]

							open_parentheses_location = hgvsc_start.find('(')

							hgvs_c = hgvsc_start[0:open_parentheses_location]+ ':' + hgvsc_end

				#Get correct hgvs_p info

				hgsv_p = mutalyzer_light_response['proteinDescriptions']

				if hgsv_p != None:

					hgvs_p = dict(hgsv_p)

					hgvs_p = hgvs_p['string'][0]

					if transcript_variant[0:3] != 'LRG':

						hgvs_p_start = hgvs_p.split(':')[0]
						hgvs_p_end = hgvs_p.split(':')[1]

						open_parentheses_location = hgvs_p.find('(')

						hgvs_p = hgvs_p_start[0:open_parentheses_location]+ ':' + hgvs_p_end

				#get gene info

				legend = mutalyzer_light_response['legend']

				if legend != None:

					gene =  dict(legend['LegendRecord'][0])['name']

					gene = gene.split('_')[0]

				else:

					gene = None

				transcript_variant_info.append([variant,hgvs_c, hgvs_p, gene])



			else:

				pass


	print (transcript_variant_info)

	return [True,transcript_variant_info]












