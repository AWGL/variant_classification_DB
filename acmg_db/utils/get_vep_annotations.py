import requests
import json


def get_vep_info_api(variant, vep_url):
	"""
	Access the VEP REST API and get the annotations for that variant.

	"""

	query = "https://grch37.rest.ensembl.org/vep/human/hgvs/2:g.179579025C>T?content-type=application/json&refseq=1&hgvs=1&numbers=1&xref_refseq=0"

 
	server = "https://grch37.rest.ensembl.org/vep/human/hgvs/2:g.179579025C>T?refseq=1&hgvs=1&numbers=1&xref_refseq=0"
 
	r = requests.get(server, headers={ "Content-Type" : "application/json"})
 
	if not r.ok:
  		r.raise_for_status()
  		sys.exit()
 
	decoded = r.json()
	for i in decoded[0]['transcript_consequences']:

		print (i)
		print ('')

	print (decoded[0]['transcript_consequences'])


get_vep_info_api('test', 'test')