from suds.client import Client
import hashlib
import re

def validate_variant(variant, mutalyzer_url, mutalyzer_build):
	"""
	Checks whether a variant is valid and gets some information about it \
	from Mutalyzer.

	Input:
	variant = String: A string representing the genomic description of a variant e.g. 'chr17:g.41197732G>A'
	mutalyzer_url = String: A string showing the mutalyzer wdsl URL e.g. 'https://mutalyzer.nl/services/?wsdl'
	mutalyzer_build = String: A string showing the mutalyzer build e.g. 'hg19'

	Returns:

	list of lists showing whether the variant passed validation and information about a valid variant.

	e.g.

	[True, [['NM_007298.3:c.2243C>T', 'BRCA1'], ['NM_007297.3:c.5414C>T', 'BRCA1']]

	or 

	[False, ['Not a valid variant']]

	"""

	# Check that the user has inputted genomic coordinates

	if variant[0:3] != 'chr':

		return [False, ['variant not in right format e.g. chr17:g.41197732G>A']]

	try:

		# Make a connection to Mutalyzer
		client = Client(mutalyzer_url, cache=None)
		wsdl_o = client.service

	except:

		return [False, ['Could not connect to Mutalyzer.']]

	# Convert the position to a number of various locations in the genome i.e. \
	# convert an entered genomic coordinate into transcript hgvs c

	try:
		response_positions = wsdl_o.numberConversion(build=mutalyzer_build, variant=variant)
		response_positions = dict(response_positions)

	except:

		return [False, ['Mutalyzer does not recognise this as a valid variant.']]

	
	# get the first of these and validate that the user has entered a real variant!

	try:

		variant_to_validate = response_positions['string'][0]

	except:

		return [False, ['Mutalyzer does not recognise this as a valid variant.']]

	response_name_check = wsdl_o.runMutalyzerLight(variant_to_validate)

	response_name_check = dict(response_name_check)

	# Check the number of errors - if 0 then we pass

	n_errors = response_name_check['errors']

	if n_errors == 0:

		transcript_and_genes = []

		gene_name = variant_to_validate

		#Now get the gene name for each transcript

		for transcript in response_positions['string']:


			# Only look at NM genes
			if transcript[0:2] == 'NM':

				gene = wsdl_o.getGeneName(build=mutalyzer_build, accno=transcript.split(':')[0])

				transcript_and_genes.append([transcript, gene])

		return [True, transcript_and_genes]

	else:

		return [False, ['Not a valid variant.']]


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


def process_variant(hgvs_g):
	"""
	splits a hgvsg description such as chr17:g.41197732G>A

	into [var_hash, chr, pos, ref, alt]

	where  var_hash is the result of calling get_variant_hash() on the results.


	"""

	chromosome = hgvs_g.split(':')[0]

	position = re.findall('\d+',hgvs_g.split(':')[1])[0]

	ref = re.sub('[0-9]', '', hgvs_g.split('.')[1]).split('>')[0]
	alt = re.sub('[0-9]', '', hgvs_g.split('.')[1]).split('>')[1]

	var_hash = get_variant_hash(chromosome, position,ref, alt)

	key = '{chr}-{pos}-{ref}-{alt}'.format(chr =chromosome, pos=position, ref=ref, alt=alt)

	return [var_hash, chromosome, position, ref, alt, key]







