# -*- coding: utf-8 -*-
import os
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from django.conf import settings
from app.models import *

####### commented out begin #######

# import logging
# logger = logging.getLogger(__name__)

###### commented out end ######

es_header = settings.ES_HEADER
es = Elasticsearch(es_header)

with open(os.path.join(settings.BASE_DIR, 'app/es_movincart', 'wn_s.pl')) as synfile:
    synonyms_lines = [next(synfile).strip() for x in xrange(212558)]

synonyms_lines = filter(lambda x: x.split(',')[3] == 'n', synonyms_lines)


def CreateProductIndex():

	es.indices.create(

		index = "mc_product-index",
		request_timeout = 1200,
		body = {
					'settings': {
							"number_of_shards"   : 10,
							# by default "number_of_replicas" : 1,
							"analysis": {
										'analyzer': {
													"mc_indexanalyzer": {
																'type'        : "custom",
																'char_filter' : [ "html_strip", "mc_mapping" ],
																'tokenizer'   : "mc_edgeNGram_tokenizer",
																'filter'      : [ "lowercase", "mc_asciifolding", "mc_stop", "mc_synonym", "mc_stemmer", "mc_autocomplete" ]
													},
													"mc_searchanalyzer": {
																'type'        : "custom",
																'char_filter' : "mc_mapping",
																'tokenizer'   : "mc_edgeNGram_tokenizer",
																'filter'      : "lowercase"
													}
										},
										'char_filter': {
													"mc_mapping": {
																'type'     : "mapping",
																'mappings' : [ ".=>", "'=>", "`=>", "?=>", "+=>", "*=>", "|=>", "{=>", "}=>", "[=>", "]=>", "(=>", ")=>", "\"=>","#=>", "@=>", "&=>", "<=>", ">=>", "~=>", "^=>", ":=>", "!=>" ]
													}
										},
										'tokenizer': {
													"mc_edgeNGram_tokenizer": {
																'type'        : "edgeNGram",
																'min_gram'    : "2",
																'max_gram'    : "20",
																'token_chars' : [ "letter", "digit" ]
													}
										},
										'filter': {
													"mc_asciifolding": {
																'type'              : "asciifolding",
																'preserve_original' : True
													},
													"mc_stop": {
																'type'      : "stop",
																'stopwords' : "_english_"
													},
													"mc_synonym": {
																'type'     : "synonym",
																'format'   : "wordnet",
																'synonyms' : synonyms_lines
													},
													"mc_stemmer": {
																'type' : "stemmer",
																'name' : [ "english", "hindi" ]
													},
													"mc_autocomplete": {
																'type'     : "edgeNGram",
																'min_gram' : 2,
																'max_gram' : 20
													}
										}
							}
					},
					'mappings': {
								"mc_product": {
											'properties': {
														"name"            : { "type" : "string", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
														"brandname"       : { "type" : "string", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
														"category"        : { "type" : "string", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
														"productid"       : { "type" : "integer", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
														"categoryid"      : { "type" : "integer", "index" : "not_analyzed" },
														"shopid"          : { "type" : "integer", "index" : "not_analyzed" },
														"productsize"     : { "type" : "string", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
														"productimage"    : { "type" : "string", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
														"displayorder"    : { "type" : "integer", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
														"tags"		      : { "type" : "string", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
														"shop"            : { "type" : "string", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
														"maximumbuy"      : { "type" : "integer", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
														"pricing"         : { "type" : "float", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
														"discountprice"   : { "type" : "float", "index" : "analyzed", "analyzer" : "mc_indexanalyzer" },
											}
								}
					}
		}
	)
	return



# Total products count in Elasticsearch Database

def get_all_products_count():

	count = es.count()['count']

	return count


# The Products list is retrieved from Elasticsearch Database ( ids of Products are retrieved )

def get_all_products_from_es():

    response = es.search( index = "mc_product-index", fields = ["productid"], body={"query": {"match_all": {}}}, size = 1000000 )

    print( response['hits']['total'] )

    products = map( lambda x: x['fields']['productid'][0], response['hits']['hits'] )

    return products



# The Product from Elasticsearch Database is deleted if the Product is deleted from our Primary Data Store ( PostgreSql )

def delete_indexed_product_not_in_db():

	all_products     = StoreProductMapping.objects.values_list( "productid", flat = True )
	indexed_products = get_all_products_from_es()

	extra_products_in_index = list( set( indexed_products ) - set( all_products ) )
	print( len( extra_products_in_index ) )

	for product in extra_products_in_index:
		delete_product( product )



# Product is deleted from Elasticsearch Database

def delete_product( productid ):

	try:
		es.delete( index = "mc_product-index", doc_type = "mc_product", id = productid )
	except:
		pass

	return



# Secondary Data Store ( Elasticsearch Database ) is indexed with Products from Primary Data Store ( PostgreSql )

def refresh_db_to_es_old():

	products_in_db = list( set( map( lambda i: i.id, StoreProductMapping.objects.all() ) ) )
	products_in_es = list( get_all_products_from_es() )

	hence_to_be_added   = list( set( products_in_db) - set( products_in_es ) )
	hence_to_be_deleted = list( set( products_in_es) - set( products_in_db ) )

	for product in hence_to_be_added:
		print( product )
		index_product_document( product )

	for product in hence_to_be_deleted:
		delete_product( product )

	return



# The Updated Product from our Primary Data Store ( PostgreSql ) is retrieved to Secondary Data Store ( Elasticsearch Database )

def refresh_db_to_es():

	updated_list_of_products = list( set( map( lambda i: i.product.id, StoreProductChanged.objects.all() ) ) )
	updated_number_of_products = len(updated_list_of_products)

	for productid in updated_list_of_products:
		print( str( updated_number_of_products ) )
		updated_number_of_products = updated_number_of_products - 1

		get_product = StoreProductMapping.objects.get( pk = productid )

		if get_product:
			delete_product( productid )
			index_product_document( productid )
		else:
			delete_product( productid )

	return



# Indexing the fields to be searched

def index_product_document( productid ):

	doc = { }

	spm = StoreProductMapping.objects.get( pk = productid )

	doc = {
				'name'          : spm.product.product.name,
				'brandname'     : spm.product.product.brand_name,
				'tags'          : ', '.join( map( lambda x: x.name, spm.product.product.tags.all() ) ),
				'shop'          : spm.store.name,
				'pricing'       : spm.price,
				'discountprice' : spm.discount,
				'maximumbuy'    : spm.max_buy,
				'productid'     : spm.id,
				'categoryid'    : spm.product.product.category.id,
				'shopid'        : spm.store.id,
				'productsize'	: str(spm.product.size),
				'productimage'  : str(spm.product.image),
				'displayorder'  : spm.display_order
	}

	es.index( index = "mc_product-index", doc_type = 'mc_product', body = doc, id = spm.id )

	return



# Gettting all the indexed results

def get_index_values( productids, fields = [ 'name', 'brandname', 'tags', 'shop', 'pricing', 'discountprice', 'maximumbuy', 'productid' ] ):

    index_body = { 'ids' : productids }

    products_list = { }

    product_detailing = es.mget( index = "mc_product-index", body = "index_body", doc_type = "mc_product", fields = fields )

    for doc in product_detailing['docs']:
        productid = doc['fields']['productid'][0]
        products_list[productid] = {}
        for field in fields:
            products_list[productid][field] = doc['fields'].get(field)

    return products_list



################################ Search queries ###############################



# Full-text Search Query

def full_productsearch( keywordstr = None, catkey = 0, shopid = 0, fields = [ "name" ,"productid" ,"categoryid" ,"productsize" ,"productimage","displayorder","maximumbuy" ,"pricing" ,"discountprice" ], num=100, threshold=0.25 ):

	fields = list( set( fields + ['productid'] ) )

	if keywordstr:
		keywordstr.lower()

	if keywordstr:
		lenkeywords = len( filter ( lambda x: x, keywordstr.split(' ') ) )
		threshold   = ( ( threshold ) - ( ( 0.04 ) * min( 4, lenkeywords ) ) )

	# 000, 100, 010, 001, 110, 101, 011, 111 ( Totally 8 combinations conditions )

	if( ( keywordstr == None ) and ( catkey == 0 ) and ( shopid == 0 ) ):

		bodyquery = {
			"query": {
				"match_all" : {}
			}
		}

	elif( ( keywordstr != None ) and ( catkey == 0 ) and ( shopid == 0 ) ):

		bodyquery = {
			"query" : {
				"filtered" : {
					"query" : {
						"bool" : {
							"should" : [
								{
									"query_string" : {
										"query" : keywordstr
									}
								}
							]
						}
					}
				}
			}
		}

	elif( ( keywordstr == None ) and ( catkey != 0 ) and ( shopid == 0 ) ):

		bodyquery = {
			"query" : {
				"filtered" : {
					"query" : {
						"match_all" : {}
					},
					"filter" : {
						"bool" : {
							"must" : [
								{ "term" : { "categoryid" : catkey } }
							]
						}
					}
				}
			}
		}


	elif( ( keywordstr == None ) and ( catkey == 0 ) and ( shopid != 0 ) ):

		bodyquery = {
			"query" : {
				"filtered" : {
					"query" : {
						"match_all" : {}
					},
					"filter" : {
						"bool" : {
							"must" : [
								{ "term" : { 'shopid' : shopid } }
							]
						}
					}
				}
			}
		}

	elif( ( keywordstr != None ) and ( catkey != 0 ) and ( shopid == 0 ) ):

		bodyquery = {
			"query" : {
				"filtered" : {
					"query" : {
						"bool": {
							"should" : [
								{
									"query_string" : {
										"query" : keywordstr
									}
								}
							]
						}
					},
					"filter" : {
						"bool" : {
							"must" : {
								{ "term" : { 'categoryid' : catkey } }
							}
						}
					}
				}
			}
		}

	elif( ( keywordstr != None ) and ( catkey == 0 ) and ( shopid != 0 ) ):

		bodyquery = {
			"query" : {
				"filtered" : {
					"query" : {
						"bool" : {
							"should" : [
								{
									"query_string" : {
										"query" : keywordstr
									}
								}
							]
						}
					},
					"filter" : {
						"bool" : {
							"must" : {
								{ "term" : { 'shopid' : shopid } }
							}
						}
					}
				}
			}
		}

	elif( ( keywordstr == None ) and ( catkey != 0 ) and ( shopid != 0 ) ):

		bodyquery = {
			"query" : {
				"filtered" : {
					"query" : {
						"match_all" : {}
					},
					"filter" : {
						"bool" : {
							"must" : [
								{ "term" : { 'categoryid' : catkey } },
								{ "term" : { 'shopid' : shopid } }
							]
						}
					}
				}
			}
		}

	else:

		bodyquery = {
			"query" : {
				"filtered" : {
					"query" : {
						"bool" : {
							"should" : [
								{
									"query_string" : {
										"query" : keywordstr
									}
								}
							]
						}
					},
					"filter" : {
						"bool" : {
							"must" : [
								{ "term" : { 'categoryid' : catkey } },
								{ "term" : { 'shopid' : shopid } }
							]
						}
					}
				}
			}
		}


	response = es.search( index = "mc_product-index", fields = fields, body = bodyquery, size = num )

	# print response['hit']['hit']

	products = []


	for hit in response['hits']['hits']:
		# if hit['_score'] > threshold:
		# 	productid = hit["fields"]["productid"][0]
		fieldelements = {}
		for field in fields:

			fieldelements[field]= hit["fields"].get(field)[0]

		products.append(fieldelements)

		if len(products) == num:
			return { 'products': products, 'numtotal': response['hits']['total'] }

	return { 'products': products, 'numtotal': min( response['hits']['total'], max(num, 200) ) }

















