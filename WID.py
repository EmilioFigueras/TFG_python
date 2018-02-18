"""Web Info Download - Create the necessary database and download the information from the target website."""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Incluimos los módulos necesarios.
#-----------------------------------------------------------------------------
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import sys
import os.path
import xml.etree.cElementTree as ET #XML Test
from unittest import TestCase
import MySQLdb #python3-mysqldb
from bs4 import BeautifulSoup

#Parametros a recibir por consola
XPATH = "info.xml"
TIME_WAIT = 0
XMLFILE = 0
CHARSET = "utf-8"
DB_PARAM = 0
#primaryKey = ""
ISTEXT = ""
DELETE_TABLE = False
VERBOSE = False

#Funcion de ayuda
def help_info():
	"""Help menu."""
	print("Web Info Download")
	print("usage: python WID.py [-h] [-v] [-x xPath] [-d] [-c] [-e]")
	print("Command Summary:")
	print("-h 		help")
	print("-v 		verbose mode")
	print("-x 		XML file path")
	print("-d 		default values")
	print("-c 		create database")
	print("-e 		create database and delete if exists")
	#print("-t 		Time wait")
	sys.exit(0)

#Manipulacion de la base de datos
def run_query(query=''):
	"""Database handling."""
	try:
		db_data = MySQLdb.connect(DB_PARAM['host'], DB_PARAM['user'], DB_PARAM['password'], DB_PARAM['db'], charset='utf8')
		cursor = db_data.cursor()
		rows_count = cursor.execute(query)
		if rows_count <= 0:
			data = None
		elif query.upper().startswith('SELECT'):
			data = cursor.fetchall()
		else:
			db_data.commit()
			data = None
		db_data.close()
		return data
	except MySQLdb.Error as error:
		try:
			print("MySQL Error [%d]: %s" % (error.args[0], error.args[1]))
			sys.exit(1)
		except IndexError:
			print("MySQL Error: %s" % str(error))
			sys.exit(1)
	except TypeError as error:
		print(error)
		sys.exit(1)
	except ValueError as error:
		print(error)
		sys.exit(1)

#Pruebas a la base de datos
def db_try():
	"""Initial tests to the database."""
	global XMLFILE
	global DB_PARAM
	global CHARSET
	if not os.path.exists(XPATH): #Buscamos el archivo xml
		print("Error: File not found")
		sys.exit(1)
	xpath_file = open(XPATH)
	XMLFILE = BeautifulSoup(xpath_file, "xml") #apt-get install python3-lxml
	xpath_file.close()
	DB_PARAM = XMLFILE.find("database")
	CHARSET = XMLFILE.find("charset").get_text()

	#Se comprueba si falta algun parametro
	if not DB_PARAM.has_attr('host') or not DB_PARAM.has_attr('user') or not DB_PARAM.has_attr('password') or not DB_PARAM.has_attr('db'):
		print("Not found database attribute definition")
		sys.exit(1)
	#Se comprueba si se ha dejado algun campo vacio
	elif DB_PARAM['host'] == "" or DB_PARAM['user'] == "" or DB_PARAM['password'] == "" or DB_PARAM['db'] == "":
		print("Bad path file definition (database)")
		sys.exit(1)
	else:
		pass

#Recoleccion de parametros
def options(param, i):
	"""Option menu."""
	global XPATH
	global TIME_WAIT
	global DELETE_TABLE
	global VERBOSE
	if param[0] == '-':
		if param[1] == 'd':
			print("XML file path: info.xml")
			print("Time wait: 0 sec")
			print("Verbose mode: disabled")
			XPATH = "info.xml"
			TIME_WAIT = 0
			VERBOSE = False
			return 1
		elif param[1] == 'x':
			XPATH = sys.argv[i+1]
			print("XML file path: %s" %(XPATH))
		elif param[1] == 't':
			TIME_WAIT = int(sys.argv[i+1])
			print("Time wait: %d sec" %(TIME_WAIT))
		elif param[1] == 'c':
			db_try()
			create_database()
		elif param[1] == 'e':
			db_try()
			DELETE_TABLE = True
			create_database()
		elif param[1] == 'v':
			VERBOSE = True
			print("Verbose mode: enabled")
		elif param[1] == 'h':
			help_info()

#Creacion de la base de datos
def create_database():
	"""Create database function."""
	#La base de datos tendra cuatro tablas que son, productos, comentarios, analisis e informes
	#global primaryKey

	#Productos
	#Los productos tendran fijo un id que sera clave primaria y un id autoincremental
	attrProduct_param = XMLFILE.findAll("rowsProduct")
	i = 0
	#Comprobamos si se quiere sobreescribir
	if DELETE_TABLE:
		query = "DROP TABLE IF EXISTS products"
		run_query(query)
		query = "CREATE TABLE products(autoid int NOT NULL AUTO_INCREMENT, id VARCHAR(128) NOT NULL, PRIMARY KEY (autoid), "
	else:
		query = "CREATE TABLE IF NOT EXISTS products(autoid int NOT NULL AUTO_INCREMENT, id VARCHAR(128) NOT NULL, PRIMARY KEY (autoid), "
	while i < len(attrProduct_param):
		#if(attrProduct_param[i].has_attr('primaryKey')):
		#	if(attrProduct_param[i]['primaryKey'] != "" and attrProduct_param[i]['primaryKey'] != "false"):
		#		primaryKey = attrProduct_param[i]['rowName']
		if attrProduct_param[i]['rowName'] != "id":
			query = query + attrProduct_param[i]['rowName'] + " " + attrProduct_param[i]['type']
			if attrProduct_param[i].has_attr('size') and attrProduct_param[i]['size'] != "":
				query = query + "(" + attrProduct_param[i]['size'] + ")"
			i += 1
			if i != len(attrProduct_param):
				query = query + ", "
			else:
				#query = query + ", PRIMARY KEY (" + primaryKey + ")) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;"
				query = query + ") ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;"
	if VERBOSE:
		print("Query: " + query)
		print("Start...")
	run_query(query)
	if VERBOSE:
		print("Query finished")

	#Comentarios
	#Los comentarios tendran fijo un id autoincremental que sera clave primaria y un idProducto que relacionara el comentario con el producto
	attrComment_param = XMLFILE.findAll("rowsComment")
	i = 0
	if DELETE_TABLE:
		query = "DROP TABLE IF EXISTS comments"
		run_query(query)
		query = "CREATE TABLE comments(autoid int NOT NULL AUTO_INCREMENT, PRIMARY KEY (autoid), idProduct VARCHAR(128) NOT NULL, "
	else:
		query = "CREATE TABLE IF NOT EXISTS comments(autoid int NOT NULL AUTO_INCREMENT, PRIMARY KEY (autoid), idProduct VARCHAR(128) NOT NULL, "
	while i < len(attrComment_param):
		#Las columnas ID e idProduct se crearan y utilizaran por defecto
		if attrComment_param[i]['rowName'] != "autoid" and attrComment_param[i]['rowName'] != "idProduct":
			query = query + attrComment_param[i]['rowName'] + " " + attrComment_param[i]['type']
			if attrComment_param[i].has_attr('size') and attrComment_param[i]['size'] != "":
				query = query + "(" + attrComment_param[i]['size'] + ")"
			i += 1
			#Si queda algun elemento mas ponemos una coma, si es el ultimo finalizamos la query
			if i != len(attrComment_param):
				query = query + ", "
			else:
				#query = query + ", FOREIGN KEY (idProduct) REFERENCES products(" + primaryKey + "));"
				query = query + ") ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;"
	if VERBOSE:
		print("Query: " + query)
		print("Start...")
	run_query(query)
	if VERBOSE:
		print("Query finished")

	#Analisis
	#La tabla de analisis siempre sera igual, tendra un id autoincremental que sera clave primaria, un idComment que lo relacionara
	#con el comentario y un varchar personalRating que sera la valoracion que el usuario hara de ese comentario
	if DELETE_TABLE:
		query = "DROP TABLE IF EXISTS analysis"
		run_query(query)
	query = "CREATE TABLE IF NOT EXISTS analysis(autoid int NOT NULL AUTO_INCREMENT, PRIMARY KEY (autoid), idComment int NOT NULL, personalRating VARCHAR(32) NOT NULL) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;"
	if VERBOSE:
		print("Query: " + query)
		print("Start...")
	run_query(query)
	if VERBOSE:
		print("Query finished")

	#Informes
	#Esta tabla sera siempre igual, tendra el id autoincremental, el titulo del informe, la descripcion, el tipo y la consulta.
	if DELETE_TABLE:
		query = "DROP TABLE IF EXISTS reports"
		run_query(query)
	query = "CREATE TABLE IF NOT EXISTS reports(autoid int NOT NULL AUTO_INCREMENT, PRIMARY KEY (autoid), title varchar(256) NOT NULL, description text, type VARCHAR(32) NOT NULL, query_select text NOT NULL, query_where text, query_groupby text, query_orderby text, active int DEFAULT '0') ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;"
	if VERBOSE:
		print("Query: " + query)
		print("Start...")
	run_query(query)
	if VERBOSE:
		print("Query finished")

	#Informes
	#Insertamos algunos informes predefinidos, que funcionen en todos los clientes y que les sirva como ejemplo

	#Numero de comentarios por noticia
	query = "INSERT INTO reports VALUES('1', 'Número de comentarios por noticia', 'Muestra el número de comentarios que tienen las noticias que más comentarios tienen.', 'bar', 'count(c.idProduct) as data, p.name as labels', 'count(c.idProduct) > 30', 'c.idProduct', null, '1');"
	if VERBOSE:
		print("Start default query 1...")
	run_query(query)
	if VERBOSE:
		print("Query finished")

	#Analisis de comentarios, buenos contra malos
	query = "INSERT INTO reports VALUES('2', 'Bien vs Mal', 'Comparativa entre las apariciones de la palabra \'\'buen\'\' vs la palabra \'\'mal\'\'', 'pie', 'sum(if(comment like \'\'%buen%\'\' or comment like \'\'%bien%\'\', 1, 0)) as bueno, sum(if(comment like \'\'%mal%\'\', 1, 0)) as malo', null, null, null, '1');"
	if VERBOSE:
		print("Start default query 2...")
	run_query(query)
	if VERBOSE:
		print("Query finished")

	#Analisis personal, favorables contra desfavorables
	query = "INSERT INTO reports VALUES('3', 'Comentarios favorables vs desfavorables', 'Una comparativa entre los comentarios que son favorables contra los que son desfavorables según el análisis propio.', 'pie', 'SUM(IF(a.personalRating = \'\'Sí\'\', 1, 0)) as SI, SUM(IF(a.personalRating = \'\'No\'\', 1, 0)) as NO', null, null, null, '1');"
	if VERBOSE:
		print("Start default query 3...")
	run_query(query)
	if VERBOSE:
		print("Query finished")

	sys.exit(0)

#Recoleccion de parametros por medio del XML
def initialize():
	"""Obtaining parameters through the XML file and checking errors."""
	#global primaryKey
	global ISTEXT
	db_try()

	#Sacamos el elemento que es la clave primaria
	#primaryKey_param = XMLFILE.find('rowsProduct', {'primaryKey':'true'})
	#primaryKey = primaryKey_param['rowName']

	#Sacamos la columna donde se almacenara los comentarios
	isText_param = XMLFILE.find('rowsComment', {'isText':'true'})

	if isText_param is None:
		print("Not comment row found")
		sys.exit(1)

	ISTEXT = isText_param['rowName']


	#Datos de url
	url_param = XMLFILE.find("url")

	if not url_param.has_attr('urlProducts') or url_param['urlProducts'] == "" or not url_param.has_attr('urlComments') or url_param['urlComments'] == "" or not url_param.has_attr('urlBase') or url_param['urlBase'] == "":
		print("Not found URL attribute definition")
		sys.exit(1)

	#Preparamos el enlace donde estan todos los productos
	urlProducts_param = XMLFILE.find("urlProducts")
	if not urlProducts_param.has_attr('categorypage_max') or urlProducts_param['categorypage_max'] == "":
		cat_max = 2
	else:
		cat_max = int(urlProducts_param['categorypage_max']) + 1

	#Sacamos el camino hacia donde tiene que buscar
	linksProduct_param = XMLFILE.findAll("linkProduct")
	linksProductFinal_param = XMLFILE.find("linkProductFinal")


	#Obtener enlaces de cada producto
	set_links(url_param['urlProducts'], url_param['urlBase'], cat_max, linksProduct_param, linksProductFinal_param)

#Obtiene los enlaces a los productos
def set_links(urlProducts, urlBase, cat_max, tags, final):
	"""Get the links of the products."""
	#req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	#soup = BeautifulSoup(urlopen(req), "html5lib", from_encoding='utf-8').getText()
	urlBase = urlBase.rstrip('/') #Por si acaso tiene barra al final del enlace, la borramos
	for i in range(1, cat_max):
		numPage = 0
		onePage = False
		endPage = False
		while not endPage:
			if urlProducts.find("npage_products") == -1: #Comprobamos si tenemos paginas
				onePage = True #Una unica pagina
			url = urlProducts.format(npage_products=str(numPage), categorypage=str(i))
			if VERBOSE:
				print("URL ini: " + url)
			req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

			try:
				soup = BeautifulSoup(urlopen(req), "html5lib", from_encoding=CHARSET)
			except HTTPError as e:
				print('The server couldn\'t fulfill the request.')
				print('Error code: ', e.code)
				numPage += 1 #Pasamos pagina
			except URLError as e:
			 	print('We failed to reach a server.')
			 	print('Reason: ', e.reason)
			 	numPage += 1 #Pasamos pagina
			else:
				j = 1
				soup = soup.findAll(tags[0]['tag'], {tags[0]['attr']:tags[0]['valueAttr']})
				#Si no encontramos ningun enlace
				if not soup:
					endPage = True
				while j < len(tags) and not endPage:
					for row in soup:
						row = row.findAll(tags[j]['tag'], {tags[j]['attr']:tags[j]['valueAttr']})
					j += 1

				#Si no encontramos ningun enlace
				if not soup or onePage:
					endPage = True

				for row in soup:
					res_link = row.find(final['tag'], {final['attr']:final['valueAttr']})
					link = res_link[final['attrGoal']]
					#Se analiza el formato del enlace obtenido
					if link.find("http://") != -1 or link.find("https://") != -1 or link.find("www.", 0, 6) != -1:
						product_url = link
					elif link[0] == '/':
						product_url = urlBase + link
					else:
						product_url = urlBase + "/" + link

					if VERBOSE:
						print("URL product: " + product_url)
					link_in(product_url)

				numPage += 1 #Pasamos pagina
				#endPage=True #PRUEBAS

#Entrar en el enlace de un producto
def link_in(url):
	"""It is entered into the information of each product."""
	idProduct = "False"

	#Abrimos la web del producto
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	try:
		soup = BeautifulSoup(urlopen(req), "html5lib", from_encoding=CHARSET)
	except HTTPError as e:
		print('The server couldn\'t fulfill the request.')
		print('Error code: ', e.code)
	except URLError as e:
	 	print('We failed to reach a server.')
	 	print('Reason: ', e.reason)
	else:
		#Buscamos la ID del producto
		idsProduct_param = XMLFILE.findAll("idProduct")
		idsProductFinal_param = XMLFILE.find("idProductFinal")

		#Profundizamos en las etiquetas de la web tanto como nos indiquen en el archivo XML
		i = 1
		soupID = soup.findAll(idsProduct_param[0]['tag'], {idsProduct_param[0]['attr']:idsProduct_param[0]['valueAttr']})
		while i < len(idsProduct_param):
			for row in soupID:
				row = row.findAll(idsProduct_param[i]['tag'], {idsProduct_param[i]['attr']:idsProduct_param[i]['valueAttr']})
			i += 1

		#Obtenemos el atributo que estamos buscando
		for row in soupID:
			res_id = row.find(idsProductFinal_param['tag'], {idsProductFinal_param['attr']:idsProductFinal_param['valueAttr']})
			idProduct = res_id[idsProductFinal_param['attrGoal']]

		if idProduct != "False": #Si hemos entrado en la pagina correcta
			#Obtenemos la informacion del producto que queremos almacenar
			attrProduct_param = XMLFILE.findAll("attributeProducts")
			i = 0
			name_row = "id, "
			value_row = "'" + idProduct + "', '" #Empieza con comilla simple
			while i < len(attrProduct_param):
				if VERBOSE:
					print("Attribute: " + attrProduct_param[i]['valueAttr'])
				soupAttr = soup.find(attrProduct_param[i]['tag'], {attrProduct_param[i]['attr']:attrProduct_param[i]['valueAttr']})
				if attrProduct_param[i]['tagID'] == "false" or attrProduct_param[i]['tagID'] == "":
					try:
						attribute = soupAttr.get_text()
					except AttributeError:
						attribute = "0"
						print("Attribute Error with " + attrProduct_param[i]['valueAttr'])
				else:
					try:
						attribute = soupAttr[attrProduct_param[i]['tagID']]
					except AttributeError:
						attribute = "0"
						print("Attribute Error with " + attrProduct_param[i]['valueAttr'])

				attribute = attribute.replace(",", ".") #Cambiamos las comas por los puntos si las hubiera
				attribute = attribute.replace("'", "") #Eliminamos las comillas simples
				attribute = attribute.strip() #Eliminamos espacios en blancos a la derecha e izquierda

				#Si es la clave primaria, la guardamos
				#if(attrProduct_param[i]['rowName'] == primaryKey):
				#	idPrimaryKey = attribute

				#Ahora insertamos el atributo en la base de datos
				#Buscamos el nombre de la columna a insertar
				name_row = name_row + attrProduct_param[i]['rowName']
				#Buscamos el valor a insertar en esa columna
				value_row = value_row + attribute
				i += 1
				if i == len(attrProduct_param):
					name_row = name_row + ")"
					value_row = value_row + "')"
				else:
					name_row = name_row + ", "
					value_row = value_row + "', '" #Importante las comillas simples para que los espacios funcionen al insertar

			#Buscamos si ya se ha introducido este producto
			query_search = "SELECT autoid FROM products WHERE id = '" + idProduct + "'"
			res_search = run_query(query_search)
			if res_search is None:
				#Con los string obtenidos creamos la query final en caso de que se introduzca por primera vez
				query = "REPLACE INTO products(" + name_row + " VALUES (" + value_row
			else:
				for row in res_search:
					#Con los string obtenidos creamos la query final en caso de que haya que actualizar
					query = "REPLACE INTO products(autoid, " + name_row + " VALUES ('" + str(row[0]) + "', " + value_row

			if VERBOSE:
				print("Query product: " + query)
			run_query(query) #Ejecutamos la consulta

			#Obtenemos los comentarios del producto
			link_comments(idProduct)

#Obtiene la informacion de cada comentario
def link_comments(idProduct):
	"""Obtain and store the information of the comments."""
	#Obtenemos la URL de los comentarios
	urlComments = XMLFILE.find("url")['urlComments']
	i = 0
	endPage = False
	while not endPage:
		if urlComments.find("{npage_comments}") == -1:
			endPage = True
		url = urlComments.format(npage_comments=str(i), numberproduct=str(idProduct))
		#Abrimos la web del comentario
		req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
		try:
			soup = BeautifulSoup(urlopen(req), "html5lib", from_encoding=CHARSET)
		except HTTPError as e:
			print('The server couldn\'t fulfill the request.')
			print('Error code: ', e.code)
		except URLError as e:
		 	print('We failed to reach a server.')
		 	print('Reason: ', e.reason)
		else:
			attrComment_param = XMLFILE.findAll("attributeComments")

			if VERBOSE:
				print("URL comments: " + url)

			#Inicializamos las listas donde iran las querys
			name_row = [] #Aqui iran los nombres de las columnas
			value_row = [] #Aqui iran el valor de cada columna
			inserts = [] #Aqui se indicara si el dato ya esta en la base de datos
			num_comments = len(soup.findAll(attrComment_param[0]['tag'], {attrComment_param[0]['attr']:attrComment_param[0]['valueAttr']}))

			#Si no hay comentarios salimos
			if num_comments < 1:
				break

			#Inicializamos los vectores a utilizar
			q = 0
			while q < num_comments:
			#for q in range(num_comments):
				name_row.append("idProduct, ")
				value_row.append("'" + idProduct + "', '")
				inserts.append("Insert")
				q += 1

			j = 0
			while j < len(attrComment_param):
				soupAttr = soup.findAll(attrComment_param[j]['tag'], {attrComment_param[j]['attr']:attrComment_param[j]['valueAttr']})
				for (k, row) in enumerate(soupAttr):
					if attrComment_param[j]['tagID'] == "false" or attrComment_param[j]['tagID'] == "":
						try:
							attribute = row.get_text()
						except AttributeError:
							attribute = "0"
							print("Attribute Error with " + attrComment_param[j]['valueAttr'])
					else:
						try:
							attribute = row[attrComment_param[j]['tagID']]
						except AttributeError:
							attribute = "0"
							print("Attribute Error with " + attrComment_param[j]['valueAttr'])
					attribute = attribute.replace(",", ".") #Cambiamos las comas por los puntos si las hubiera
					attribute = attribute.replace("'", "") #Cambiamos las comillas simples por nada
					attribute = attribute.strip() #Eliminamos espacios en blancos a la derecha e izquierda

					#Ahora insertamos el atributo en la base de datos
					#Buscamos el nombre de la columna a insertar
					name_row[k] = name_row[k] + attrComment_param[j]['rowName']
					#Buscamos el valor a insertar en esa columna
					value_row[k] = value_row[k] + attribute
					if attrComment_param[j]['rowName'] == ISTEXT:
						if is_repit(attribute, idProduct):
							inserts[k] = "No insert"

				j += 1
				if j == len(attrComment_param):
					for (k, row) in enumerate(name_row):
						name_row[k] = name_row[k] + ")"
						value_row[k] = value_row[k] + "')"
				else:
					for (k, row) in enumerate(name_row):
						name_row[k] = name_row[k] + ", "
						value_row[k] = value_row[k] + "', '" #Importante las comillas simples para que los espacios funcionen al insertar

			#Con los string obtenidos creamos la query final
			for (k, row) in enumerate(name_row):
				#Si no estan repetidos, insertamos
				if inserts[k] == "Insert":
					query = "REPLACE INTO comments(" + name_row[k] + " VALUES (" + value_row[k]
					if VERBOSE:
						print("Query comment: " + query)
					run_query(query) #Ejecutamos la consulta

			i += 1 #Pasamos pagina

#Comprueba si un comentario ya esta repetido
def is_repit(comment, idProduct):
	"""Check if a comment is repeated."""
	query = "SELECT autoid FROM comments WHERE idProduct = '" + idProduct + "' and " + ISTEXT + " LIKE '" + comment + "'"
	res = run_query(query)
	if res is None:
		return False
	return True

#Funcion inicial
def main():
	"""Main function."""
	#Parametros por consola
	i = 0
	#print(sys.argv)
	if len(sys.argv) > 1:
		for param in sys.argv:
			ret = options(param, i)
			if ret == 1:
				break
			i += 1
	else:
		help_info()
	initialize()

if __name__ == '__main__':
	main()

#Pruebas
#Argumentos basicos
class ArgTest(TestCase):
	"""Testing input arguments."""

	def setUp(self):
		sys.argv = ['TFG.py', '-x', 'prueba.xml', '-v']

	#Prueba del modo VERBOSE, de la lectura de ficheros y del modo por defecto
	def test_params(self):
		"""Testing verbose mode, reading files and default mode."""
		i = 0
		for param in sys.argv:
			ret = options(param, i)
			if ret == 1:
				break
			i += 1
		self.assertTrue(VERBOSE)
		self.assertEqual(XPATH, 'prueba.xml')
		sys.argv = ['TFG.py', '-d']
		i = 0
		for param in sys.argv:
			ret = options(param, i)
			if ret == 1:
				break
			i += 1
		self.assertFalse(VERBOSE)
		self.assertEqual(XPATH, 'info.xml')

	#Se ejecuta despues de cada prueba
	def tearDown(self):
		sys.argv = []

#Base de datos
class Arg_DatabaseTest(TestCase):
	"""Testing database."""

	#Creacion de base de datos con datos correctos y sobreescritura de base de datos
	def test_db_ok(self):
		"""Creating and overwriting database with correct data."""
		#Preparacion de prueba
		sys.argv = ['TFG.py', '-x', 'test.xml', '-c']
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="true")
		ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")

		#Creacion inicial de la base de datos
		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 0)

		#Sobreescritura de la base de datos
		sys.argv = ['TFG.py', '-x', 'test.xml', '-e']
		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 0)

		os.remove("test.xml")
		query = "DROP TABLE analysis, comments, products, reports"
		run_query(query)

	#Datos de creacion de base de datos incorrectos y archivo XML no encontrado
	def test_db_fail(self):
		"""Creating and overwriting database with wrong data and XML file not found."""
		sys.argv = ['TFG.py', '-x', 'test_exist.xml', '-c']

		#Archivo no encontrado
		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 1)


		sys.argv = ['TFG.py', '-x', 'test_2.xml', '-c']


		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		ET.SubElement(t_info, "database", host="localhost", db="", user="admin", password="admin")


		arbol = ET.ElementTree(t_info)
		arbol.write("test_2.xml")

		#Dato en blanco
		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 1)
		os.remove("test_2.xml")

	#Se ejecuta despues de cada prueba
	def tearDown(self):
		sys.argv = []

#Errores en el fichero
class FailTest(TestCase):
	"""Testing XML file."""

	#Prueba que XML contiene ISTEXT
	def test_isText(self):
		"""Test that XML file contains isText variable."""
		#Preparacion de prueba
		sys.argv = ['TFG.py', '-x', 'test.xml']
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="") #No ponemos a true isText
		ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")

		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 1)

	#Prueba que el XML contiene urlBase
	def test_urlBase(self):
		"""Test that XML file contains urlBase variable."""
		#Preparacion de prueba
		sys.argv = ['TFG.py', '-x', 'test.xml']
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="true") #No ponemos a true isText
		ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		ET.SubElement(t_info, "url", urlBase="", urlProducts="http://www.marca.com/futbol/cadiz.html", urlComments="http://www.marca.com/servicios/noticias/comentarios/comunidad/listar.html?noticia={numberproduct}&portal=5&pagina={npage_comments}")

		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")

		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 1)

	#Prueba que el XML contiene urlProducts
	def test_urlProducts(self):
		"""Test that XML file contains urlProducts variable."""
		#Preparacion de prueba
		sys.argv = ['TFG.py', '-x', 'test.xml']
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="true") #No ponemos a true isText
		ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		ET.SubElement(t_info, "url", urlBase="http://www.marca.com", urlComments="http://www.marca.com/servicios/noticias/comentarios/comunidad/listar.html?noticia={numberproduct}&portal=5&pagina={npage_comments}")

		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")

		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 1)

	#Prueba que el XML contiene urlComments
	def test_urlComments(self):
		"""Test that XML file contains urlComments variable."""
		#Preparacion de prueba
		sys.argv = ['TFG.py', '-x', 'test.xml']
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="true") #No ponemos a true isText
		ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		ET.SubElement(t_info, "url", urlBase="http://www.marca.com", urlProducts="http://www.marca.com/futbol/cadiz.html", urlComments="")

		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")

		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 1)

	#Se ejecuta despues de cada prueba
	def tearDown(self):
		os.remove("test.xml")
		sys.argv = []

#Comprueba el funcionamiento de la funcion is_repit
class RepitTest(TestCase):
	"""Testing is_repit function."""
	def setUp(self):
		#Creamos el fichero XML de entrada
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="true") #No ponemos a true isText
		ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")

		#Creamos la base de datos
		sys.argv = ['TFG.py', '-x', 'test.xml', "-e"]
		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 0)

		#Insertamos un producto
		query = "INSERT INTO products VALUES('1', '123456', 'Producto de prueba', '0.0');"
		run_query(query)

		#Insertamo el comentario que se utilizara para probar
		query = "INSERT INTO comments VALUES('1', '123456', 'nick_prueba', 'Este comentario es una prueba de verificación para el método que comprueba si hay comentarios repetidos.', '09/05/1945');"
		run_query(query)

		#Definimos que los comentarios se guardaran en el atributo comment
		global ISTEXT
		ISTEXT = "comment"

	def test_repit(self):
		"""Testing is_repit function."""
		#Debe dar verdadero
		repit = is_repit('Este comentario es una prueba de verificación para el método que comprueba si hay comentarios repetidos.', '123456')
		self.assertTrue(repit)

		#Debe dar falso por el id del product
		repit = is_repit('Este comentario es una prueba de verificación para el método que comprueba si hay comentarios repetidos.', '213456')
		self.assertFalse(repit)

		#Debe dar falso por el comentario
		repit = is_repit('Este comentario es una prueba de verificacion para el metodo que comprueba si hay comentarios repetidos.', '123456')
		self.assertFalse(repit)

	#Se ejecuta despues de cada prueba
	def tearDown(self):
		os.remove("test.xml")
		query = "DROP TABLE analysis, comments, products, reports"
		run_query(query)
		sys.argv = []

#Test completo para el dia 9 de diciembre de 2017
class CompleteTest(TestCase):
	"""Complete Test on December 9, 2017."""
	#Preparamos el entorno
	def setUp(self):
		#Creamos el fichero XML de entrada
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="true") #No ponemos a true isText
		ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		ET.SubElement(t_info, "url", urlBase="http://www.marca.com", urlProducts="http://www.marca.com/futbol/cadiz.html", urlComments="http://www.marca.com/servicios/noticias/comentarios/comunidad/listar.html?noticia={numberproduct}&portal=5&pagina={npage_comments}")
		t_urlProducts = ET.SubElement(t_info, "urlProducts", categorypage_max="")
		ET.SubElement(t_urlProducts, "linkProduct", tag="header", attr="class", valueAttr="mod-header")
		ET.SubElement(t_urlProducts, "linkProduct", tag="h3", attr="class", valueAttr="mod-title")
		ET.SubElement(t_urlProducts, "linkProductFinal", tag="a", attr="itemprop", valueAttr="url", attrGoal="href")

		ET.SubElement(t_urlProducts, "attributeProducts", tag="meta", attr="name", valueAttr="twitter:title", tagID="false", rowName="name")

		ET.SubElement(t_urlProducts, "idProduct", tag="aside", attr="class", valueAttr="aside-comments right-panel comments-panel")
		ET.SubElement(t_urlProducts, "idProduct", tag="div", attr="class", valueAttr="no-visible comentarios comentarios-retro")
		ET.SubElement(t_urlProducts, "idProductFinal", tag="div", attr="class", valueAttr="js-comments-container", attrGoal="data-commentid")


		t_urlComments = ET.SubElement(t_info, "urlComments")
		ET.SubElement(t_urlComments, "attributeComments", tag="span", attr="class", valueAttr="nombre_usuario", tagID="false", rowName="nick")
		ET.SubElement(t_urlComments, "attributeComments", tag="span", attr="class", valueAttr="fecha", tagID="false", rowName="date")
		ET.SubElement(t_urlComments, "attributeComments", tag="div", attr="class", valueAttr="comentario", tagID="false", rowName="comment")
		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")

		#Creamos la base de datos
		sys.argv = ['TFG.py', '-x', 'test.xml', "-e"]
		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 0)

	#Dado un archivo de entrada completo debe rellenar la base de datos
	def test_complete_ok(self):
		"""Given a complete input file you must fill in the database."""
		#Comprobamos que la base de datos esta vacia
		query = "Select count(c.autoid), count(p.autoid) from comments as c join products as p on c.idProduct = p.id"
		result = run_query(query)
		for row in result:
			count_comment = row[0]
			count_product = row[1]

		#Comprobamos que no hay comentarios ni productos antes de comenzar la pruebas
		self.assertEqual(count_comment, 0)
		self.assertEqual(count_product, 0)

		#Ejecutamos el programa con el fichero recien creado y activando el modo detallado
		sys.argv = ['TFG.py', '-v', '-x', 'test.xml']
		main()

		#Volvemos a comprobar el numero de comentarios y productos ahora
		query = "Select count(c.autoid), count(p.autoid) from comments as c join products as p on c.idProduct = p.id"
		result = run_query(query)
		for row in result:
			count_comment = row[0]
			count_product = row[1]

		#Comprobamos que se ha introducido correctamente comentarios y productos
		self.assertGreater(count_comment, 0)
		self.assertGreater(count_product, 0)

	#Se ejecuta despues de cada prueba
	def tearDown(self):
		os.remove("test.xml")
		query = "DROP TABLE analysis, comments, products, reports"
		run_query(query)
		sys.argv = []
