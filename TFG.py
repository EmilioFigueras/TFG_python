#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
#-----------------------------------------------------------------------------
# Incluimos los módulos necesarios.
#-----------------------------------------------------------------------------
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import sys
import os.path
import MySQLdb #python3-mysqldb
import xml.etree.cElementTree as ET #XML Test

from unittest import TestCase

#Parametros a recibir por consola
xpath = "info.xml"
time_wait = 0
xmlFile = 0
charset = "utf-8"
db_param = 0
primaryKey = ""
isText = ""
delete_table = False
verbose = False

#Funcion de ayuda
def help():
	print("Web Info Download")
	print("usage: python download_mod.py [-c] [-e] [-h] [-d] [-v] [-x xPath] [-t time_wait]")
	print("Command Summary:")
	print("-c 		create database")
	print("-e 		create database and delete if exists")
	print("-d 		default values")
	print("-v 		verbose mode")
	print("-x 		XML file path")
	#print("-t 		Time wait")
	print("-h 		help")
	sys.exit(0)

#Manipulacion de la base de datos
def run_query(query=''):
	try:
		db = MySQLdb.connect(db_param['host'], db_param['user'], db_param['password'], db_param['db'], charset='utf8') 
		cursor = db.cursor()
		rows_count = cursor.execute(query)
		if(rows_count <= 0):
			data = None
		elif(query.upper().startswith('SELECT')):
			data = cursor.fetchall()
		else:
			db.commit()
			data = None
		db.close()
		return data
	except:
		print("Database error")
		sys.exit(1)
	

#Pruebas a la base de datos
def db_try():
	global xmlFile
	global db_param
	global charset
	if not os.path.exists(xpath): #Buscamos el archivo xml
		print("Error: File not found")
		sys.exit(1)
	xmlFile = BeautifulSoup(open(xpath), "xml") #apt-get install python3-lxml
	db_param = xmlFile.find("database")
	charset = xmlFile.find("charset").get_text()

	#Se comprueba si falta algun parametro
	if not db_param.has_attr('host') or not db_param.has_attr('user') or not db_param.has_attr('password') or not db_param.has_attr('db'):
		print("Not found database attribute definition")
		sys.exit(1)
	#Se comprueba si se ha dejado algun campo vacio
	elif db_param['host'] is "" or db_param['user'] is "" or db_param['password'] is "" or db_param['db'] is "":
		print("Bad path file definition (database)")
		sys.exit(1)
	else:
		pass


#Recoleccion de parametros
def options(param, i):
	global xpath
	global time_wait
	global delete_table
	global verbose
	if param[0] == '-':
		if param[1] == 'd':
			print("XML file path: info.xml")
			print("Time wait: 0 sec")
			print("Verbose mode: disabled")
			xpath = "info.xml"
			time_wait = 0
			verbose = False
			return 1
		elif param[1] == 'x':
			xpath = sys.argv[i+1]
			print("XML file path: %s" %(xpath))
		elif param[1] == 't':
			time_wait = int(sys.argv[i+1])
			print("Time wait: %d sec" %(time_wait))
		elif param[1] == 'c':
			db_try()
			create_database()
		elif param[1] == 'e':
			db_try()
			delete_table = True
			create_database()
		elif param[1] == 'v':
			verbose = True
			print("Verbose mode: enabled")
		elif param[1] == 'h':
			help()

def create_database():
	#La base de datos tendra cuatro tablas que son, productos, comentarios, analisis e informes
	#global primaryKey

	#Productos
	#Los productos tendran fijo un id que sera clave primaria y un id autoincremental
	attrProduct_param = xmlFile.findAll("rowsProduct")
	i=0

	#Comprobamos si se quiere sobreescribir
	if(delete_table):
		query = "DROP TABLE IF EXISTS products"
		run_query(query)
		query = "CREATE TABLE products(autoid int NOT NULL AUTO_INCREMENT, id int NOT NULL, PRIMARY KEY (autoid), "
	else:
		query = "CREATE TABLE IF NOT EXISTS products(autoid int NOT NULL AUTO_INCREMENT, id int NOT NULL, PRIMARY KEY (autoid), "
	while(i<len(attrProduct_param)):
		"""if(attrProduct_param[i].has_attr('primaryKey')):
			if(attrProduct_param[i]['primaryKey'] != "" and attrProduct_param[i]['primaryKey'] != "false"):
				primaryKey = attrProduct_param[i]['rowName']"""
		if(attrProduct_param[i]['rowName'] != "id"):
			query = query + attrProduct_param[i]['rowName'] + " " + attrProduct_param[i]['type']
			if(attrProduct_param[i].has_attr('size') and attrProduct_param[i]['size'] != ""):
				query = query + "(" + attrProduct_param[i]['size'] + ")"
			i+=1
			if(i!=len(attrProduct_param)):
				query = query + ", "
			else:
				#query = query + ", PRIMARY KEY (" + primaryKey + ")) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;"
				query = query + ") ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;"
	if(verbose):
		print("Query: " + query)
		print("Start...")
	run_query(query)
	if(verbose):
		print("Query finished")

	#Comentarios
	#Los comentarios tendran fijo un id autoincremental que sera clave primaria y un idProducto que relacionara el comentario con el producto
	attrComment_param = xmlFile.findAll("rowsComment")
	i=0
	if(delete_table):
		query = "DROP TABLE IF EXISTS comments"
		run_query(query)
		query = "CREATE TABLE comments(autoid int NOT NULL AUTO_INCREMENT, PRIMARY KEY (autoid), idProduct int NOT NULL, "
	else:
		query = "CREATE TABLE IF NOT EXISTS comments(autoid int NOT NULL AUTO_INCREMENT, PRIMARY KEY (autoid), idProduct int NOT NULL, "
	while(i<len(attrComment_param)):
		#Las columnas ID e idProduct se crearan y utilizaran por defecto
		if(attrComment_param[i]['rowName'] != "autoid" and attrComment_param[i]['rowName'] != "idProduct"):
			query = query + attrComment_param[i]['rowName'] + " " + attrComment_param[i]['type'] 
			if(attrComment_param[i].has_attr('size') and attrComment_param[i]['size'] != ""):
				query = query + "(" + attrComment_param[i]['size'] + ")"
			i+=1
			#Si queda algun elemento mas ponemos una coma, si es el ultimo finalizamos la query
			if(i!=len(attrComment_param)):
				query = query + ", "
			else:
				#query = query + ", FOREIGN KEY (idProduct) REFERENCES products(" + primaryKey + "));"
				query = query + ") ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;"
	if(verbose):
		print("Query: " + query)
		print("Start...")
	run_query(query)
	if(verbose):
		print("Query finished")

	#Analisis
	#La tabla de analisis siempre sera igual, tendra un id autoincremental que sera clave primaria, un idComment que lo relacionara
	#con el comentario y un varchar personalRating que sera la valoracion que el usuario hara de ese comentario
	if(delete_table):
		query = "DROP TABLE IF EXISTS analysis"
		run_query(query)
	query = "CREATE TABLE IF NOT EXISTS analysis(autoid int NOT NULL AUTO_INCREMENT, PRIMARY KEY (autoid), idComment int NOT NULL, personalRating VARCHAR(32) NOT NULL) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;"
	if(verbose):
		print("Query: " + query)
		print("Start...")
	run_query(query)
	if(verbose):
		print("Query finished")

	#Informes
	#Esta tabla sera siempre igual, tendra el id autoincremental, el titulo del informe, la descripcion, el tipo y la consulta.
	if(delete_table):
		query = "DROP TABLE IF EXISTS reports"
		run_query(query)
	query = "CREATE TABLE IF NOT EXISTS reports(autoid int NOT NULL AUTO_INCREMENT, PRIMARY KEY (autoid), title varchar(256) NOT NULL, description text, type VARCHAR(32) NOT NULL, query_select text NOT NULL, query_where text, query_groupby text, query_orderby text, active int DEFAULT '0') ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;"
	if(verbose):
		print("Query: " + query)
		print("Start...")
	run_query(query)
	if(verbose):
		print("Query finished")

	#Informes
	#Insertamos algunos informes predefinidos, que funcionen en todos los clientes y que les sirva como ejemplo

	#Numero de comentarios por noticia
	query = "INSERT INTO reports VALUES('1', 'Número de comentarios por noticia', 'Muestra el número de comentarios que tienen las noticias que más comentarios tienen.', 'bar', 'count(c.idProduct) as data, p.name as labels', 'count(c.idProduct) > 30', 'c.idProduct', null, '1');"
	if(verbose):
		print("Start default query 1...")
	run_query(query)
	if(verbose):
		print("Query finished")

	#Analisis de comentarios, buenos contra malos
	query = "INSERT INTO reports VALUES('2', 'Bien vs Mal', 'Comparativa entre las apariciones de la palabra \'\'buen\'\' vs la palabra \'\'mal\'\'', 'pie', 'sum(if(comment like \'\'%buen%\'\' or comment like \'\'%bien%\'\', 1, 0)) as bueno, sum(if(comment like \'\'%mal%\'\', 1, 0)) as malo', null, null, null, '1');"
	if(verbose):
		print("Start default query 2...")
	run_query(query)
	if(verbose):
		print("Query finished")

	#Analisis personal, favorables contra desfavorables
	query = "INSERT INTO reports VALUES('3', 'Comentarios favorables vs desfavorables', 'Una comparativa entre los comentarios que son favorables contra los que son desfavorables según el análisis propio.', 'pie', 'SUM(IF(a.personalRating = \'\'Sí\'\', 1, 0)) as SI, SUM(IF(a.personalRating = \'\'No\'\', 1, 0)) as NO', null, null, null, '1');"
	if(verbose):
		print("Start default query 3...")
	run_query(query)
	if(verbose):
		print("Query finished")

	sys.exit(0)


#Recoleccion de parametros por medio del XML
def initialize():
	#global primaryKey
	global isText
	db_try()

	#Sacamos el elemento que es la clave primaria
	#primaryKey_param = xmlFile.find('rowsProduct', {'primaryKey':'true'})
	#primaryKey = primaryKey_param['rowName']

	#Sacamos la columna donde se almacenara los comentarios
	isText_param = xmlFile.find('rowsComment', {'isText':'true'})

	if isText_param is None:
		print("Not comment row found")
		sys.exit(1)

	isText = isText_param['rowName']


	#Datos de url
	url_param = xmlFile.find("url")

	if not url_param.has_attr('urlProducts') or url_param['urlProducts'] == "" or not url_param.has_attr('urlComments') or url_param['urlComments'] == "" or not url_param.has_attr('urlBase') or url_param['urlBase'] == "":
		print("Not found URL attribute definition")
		sys.exit(1)

	#Preparamos el enlace donde estan todos los productos
	urlProducts_param = xmlFile.find("urlProducts")
	if not urlProducts_param.has_attr('categorypage_max') or urlProducts_param['categorypage_max'] == "":
		cat_max = 2
	else:
		cat_max = int(urlProducts_param['categorypage_max']) + 1

	#Sacamos el camino hacia donde tiene que buscar
	linksProduct_param = xmlFile.findAll("linkProduct")
	linksProductFinal_param = xmlFile.find("linkProductFinal")


	#Obtener enlaces de cada producto
	set_links(url_param['urlProducts'], url_param['urlBase'], cat_max, linksProduct_param, linksProductFinal_param)



#Obtiene los enlaces a los productos
def set_links(urlProducts, urlBase, cat_max, tags, final):
	#req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	#soup = BeautifulSoup(urlopen(req), "html5lib", from_encoding='utf-8').getText()
	urlBase = urlBase.rstrip('/') #Por si acaso tiene barra al final del enlace, la borramos
	for i in range(1, cat_max):
		numPage = 0
		onePage = False
		endPage = False
		while (not endPage):
			if(urlProducts.find("npage_products") == -1): #Comprobamos si tenemos paginas
				onePage = True #Una unica pagina
			url = urlProducts.format(npage_products=str(numPage), categorypage=str(i))
			if(verbose):
				print("URL ini: " + url)
			req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
			soup = BeautifulSoup(urlopen(req), "html5lib", from_encoding=charset)
			j=1
			soup = soup.findAll(tags[0]['tag'], {tags[0]['attr']:tags[0]['valueAttr']})
			
			#Si no encontramos ningun enlace
			if (len(soup) == 0):
				endPage = True
			while (j<len(tags) and not endPage):
				for row in soup:
					row = row.findAll(tags[j]['tag'], {tags[j]['attr']:tags[j]['valueAttr']})
				j+=1

			#Si no encontramos ningun enlace
			if (len(soup) == 0 or onePage):
				endPage = True

			for row in soup:
				res_link = row.find(final['tag'], {final['attr']:final['valueAttr']})
				link = res_link[final['attrGoal']]
				#Se analiza el formato del enlace obtenido
				if (link.find("http://") != -1 or link.find("https://") != -1 or link.find("www.", 0, 6) != -1):
					product_url = link
				elif(link[0] == '/'):
					product_url = urlBase + link
				else:
					product_url = urlBase + "/" + link

				if(verbose):
					print("URL product: " + product_url)
				link_in(product_url)

			numPage+=1 #Pasamos pagina
			#endPage=True #PRUEBAS



#Entrar en el enlace de un producto
def link_in(url):
	idProduct = "False"

	#Abrimos la web del producto
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	soup = BeautifulSoup(urlopen(req), "html5lib", from_encoding=charset)

	#Buscamos la ID del producto
	idsProduct_param = xmlFile.findAll("idProduct")
	idsProductFinal_param = xmlFile.find("idProductFinal")

	#Profundizamos en las etiquetas de la web tanto como nos indiquen en el archivo XML
	i=1
	soupID = soup.findAll(idsProduct_param[0]['tag'], {idsProduct_param[0]['attr']:idsProduct_param[0]['valueAttr']})
	while (i<len(idsProduct_param)):
		for row in soupID:
			row = row.findAll(idsProduct_param[i]['tag'], {idsProduct_param[i]['attr']:idsProduct_param[i]['valueAttr']})
		i+=1

	#Obtenemos el atributo que estamos buscando
	for row in soupID:
		res_id = row.find(idsProductFinal_param['tag'], {idsProductFinal_param['attr']:idsProductFinal_param['valueAttr']})
		idProduct = res_id[idsProductFinal_param['attrGoal']]

	if(idProduct != "False"): #Si hemos entrado en la pagina correcta
		#Obtenemos la informacion del producto que queremos almacenar
		attrProduct_param = xmlFile.findAll("attributeProducts")
		i=0
		name_row = "id, "
		value_row = "'" + idProduct + "', '" #Empieza con comilla simple
		while(i<len(attrProduct_param)):
			if(verbose):
				print("Attribute: " + attrProduct_param[i]['valueAttr'])
			soupAttr = soup.find(attrProduct_param[i]['tag'], {attrProduct_param[i]['attr']:attrProduct_param[i]['valueAttr']})
			if(attrProduct_param[i]['tagID'] == "false" or attrProduct_param[i]['tagID'] == ""):
				attribute = soupAttr.get_text()
			else:
				attribute = soupAttr[attrProduct_param[i]['tagID']]

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
			i+=1
			if(i==len(attrProduct_param)):
				name_row = name_row + ")"
				value_row = value_row + "')"
			else:
				name_row = name_row + ", "
				value_row = value_row + "', '" #Importante las comillas simples para que los espacios funcionen al insertar

		#Con los string obtenidos creamos la query final
		query = "REPLACE INTO products(" + name_row + " VALUES (" + value_row
		if(verbose):
			print("Query product: " + query)
		run_query(query) #Ejecutamos la consulta

		#Obtenemos los comentarios del producto
		link_comments(idProduct)
	



def link_comments(idProduct):
	#Obtenemos la URL de los comentarios
	urlComments = xmlFile.find("url")['urlComments']
	i=0
	endPage=False
	while(not endPage):
		url = urlComments.format(npage_comments=str(i), numberproduct=str(idProduct))
		#Abrimos la web del comentario
		req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
		soup = BeautifulSoup(urlopen(req), "html5lib", from_encoding=charset)
		attrComment_param = xmlFile.findAll("attributeComments")

		if(verbose):
			print("URL comments: " + url)

		#Inicializamos las listas donde iran las querys
		name_row = [] #Aqui iran los nombres de las columnas
		value_row = [] #Aqui iran el valor de cada columna
		inserts = [] #Aqui se indicara si el dato ya esta en la base de datos
		num_comments = len(soup.findAll(attrComment_param[0]['tag'], {attrComment_param[0]['attr']:attrComment_param[0]['valueAttr']}))

		#Si no hay comentarios salimos
		if(num_comments<1):
			break

		#Inicializamos los vectores a utilizar
		for q in range(num_comments):
			name_row.append("idProduct, ")
			value_row.append("'" + idProduct + "', '")
			inserts.append("Insert")
		
		
		j=0
		while(j<len(attrComment_param)):
			soupAttr = soup.findAll(attrComment_param[j]['tag'], {attrComment_param[j]['attr']:attrComment_param[j]['valueAttr']})
			for (k, row) in enumerate(soupAttr):
				if(attrComment_param[j]['tagID'] == "false" or attrComment_param[j]['tagID'] == ""):
					attribute = row.get_text()
				else:
					attribute = row[attrComment_param[j]['tagID']]

				attribute = attribute.replace(",", ".") #Cambiamos las comas por los puntos si las hubiera
				attribute = attribute.replace("'", "") #Cambiamos las comillas simples por nada
				attribute = attribute.strip() #Eliminamos espacios en blancos a la derecha e izquierda

				#Ahora insertamos el atributo en la base de datos
				#Buscamos el nombre de la columna a insertar
				name_row[k] = name_row[k] + attrComment_param[j]['rowName']
				#Buscamos el valor a insertar en esa columna
				value_row[k] = value_row[k] + attribute
				if(attrComment_param[j]['rowName'] == isText):
					if(is_repit(attribute, idProduct)):
						inserts[k] = "No insert"


			j+=1
			if(j==len(attrComment_param)):
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
			if(inserts[k] == "Insert"):
				query = "REPLACE INTO comments(" + name_row[k] + " VALUES (" + value_row[k]
				if(verbose):
					print("Query comment: " + query)
				run_query(query) #Ejecutamos la consulta

		i+=1 #Pasamos pagina


#Comprueba si un comentario ya esta repetido
def is_repit(comment, idProduct):
	query = "SELECT autoid FROM comments WHERE idProduct = " + idProduct + " and " + isText + " LIKE '" + comment + "'"
	res = run_query(query)
	if res is None:
		return False
	else:
		return True



def main():
	#Parametros por consola
	i=0
	#print(sys.argv)
	if len(sys.argv)>1:
		for param in sys.argv:
			ret = options(param, i)
			if(ret == 1):
				break
			i+=1
	else:
		help()
	print()
	initialize()

if __name__ == '__main__':
	main()

#Pruebas

#Argumentos basicos
class ArgTest(TestCase):

	def setUp(self):
		sys.argv = ['TFG.py', '-x', 'prueba.xml', '-v']

	#Prueba del modo verbose, de la lectura de ficheros y del modo por defecto
	def test_params(self):
		i=0
		for param in sys.argv:
			ret = options(param, i)
			if(ret == 1):
				break
			i+=1
		self.assertTrue(verbose)
		self.assertEqual(xpath, 'prueba.xml')
		sys.argv = ['TFG.py', '-d']
		i=0
		for param in sys.argv:
			ret = options(param, i)
			if(ret == 1):
				break
			i+=1
		self.assertFalse(verbose)
		self.assertEqual(xpath, 'info.xml')

	def tearDown(self):
		sys.argv = []


#Base de datos
class Arg_DatabaseTest(TestCase):

	#Creacion de base de datos con datos correctos
	def test_db_ok(self):
		#Preparacion de prueba
		sys.argv = ['TFG.py', '-x', 'test.xml','-c']
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		t_rowsProduct1 = ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		t_rowsProduct2 = ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		t_rowsComment1 = ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		t_rowsComment2 = ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="true")
		t_rowsComment3 = ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")	


		i=0
		with self.assertRaises(SystemExit) as cm:
			for param in sys.argv:
				ret = options(param, i)
				if(ret == 1):
					break
				i+=1
		self.assertEqual(cm.exception.code, 0)

		os.remove("test.xml")
		query = "DROP TABLE analysis, comments, products, reports"
		run_query(query)

	#Datos de creacion de base de datos incorrectos y archivo XML no encontrado
	def test_db_fail(self):
		sys.argv = ['TFG.py', '-x', 'test_exist.xml','-c']

		#Archivo no encontrado		
		i=0
		with self.assertRaises(SystemExit) as cm:
			for param in sys.argv:
				ret = options(param, i)
				if(ret == 1):
					break
				i+=1
		self.assertEqual(cm.exception.code, 1)


		sys.argv = ['TFG.py', '-x', 'test_2.xml','-c']


		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="", user="admin", password="admin")


		arbol = ET.ElementTree(t_info)
		arbol.write("test_2.xml")

		#Dato en blanco		
		i=0
		with self.assertRaises(SystemExit) as cm:
			for param in sys.argv:
				ret = options(param, i)
				if(ret == 1):
					break
				i+=1
		self.assertEqual(cm.exception.code, 1)
		os.remove("test_2.xml")

	def tearDown(self):
		sys.argv = []
		

#Errores en el fichero
class FailTest(TestCase):

	#Prueba que XML contiene isText
	def test_isText(self):
		#Preparacion de prueba
		sys.argv = ['TFG.py', '-x', 'test.xml']
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		t_rowsProduct1 = ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		t_rowsProduct2 = ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		t_rowsComment1 = ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		t_rowsComment2 = ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="") #No ponemos a true isText
		t_rowsComment3 = ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")	

		i=0
		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 1)

		os.remove("test.xml")

	#Prueba que el XML contiene urlBase
	def test_urlBase(self):
		#Preparacion de prueba
		sys.argv = ['TFG.py', '-x', 'test.xml']
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		t_rowsProduct1 = ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		t_rowsProduct2 = ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		t_rowsComment1 = ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		t_rowsComment2 = ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="true") #No ponemos a true isText
		t_rowsComment3 = ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		t_url = ET.SubElement(t_info, "url", urlBase="", urlProducts="http://www.marca.com/futbol/cadiz.html", urlComments="http://www.marca.com/servicios/noticias/comentarios/comunidad/listar.html?noticia={numberproduct}&amp;portal=5&amp;pagina={npage_comments}")

		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")	

		i=0
		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 1)

		os.remove("test.xml")

	#Prueba que el XML contiene urlProducts
	def test_urlProducts(self):
		#Preparacion de prueba
		sys.argv = ['TFG.py', '-x', 'test.xml']
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		t_rowsProduct1 = ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		t_rowsProduct2 = ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		t_rowsComment1 = ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		t_rowsComment2 = ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="true") #No ponemos a true isText
		t_rowsComment3 = ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		t_url = ET.SubElement(t_info, "url", urlBase="http://www.marca.com", urlComments="http://www.marca.com/servicios/noticias/comentarios/comunidad/listar.html?noticia={numberproduct}&amp;portal=5&amp;pagina={npage_comments}")

		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")	

		i=0
		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 1)

		os.remove("test.xml")

	#Prueba que el XML contiene urlCommments
	def test_urlComments(self):
		#Preparacion de prueba
		sys.argv = ['TFG.py', '-x', 'test.xml']
		t_info = ET.Element("info")
		t_charset = ET.SubElement(t_info, "charset")
		t_charset.text = "utf-8"
		t_database = ET.SubElement(t_info, "database", host="localhost", db="tfg_test", user="admin", password="admin")
		t_rowsProduct1 = ET.SubElement(t_database, "rowsProduct", rowName="name", type="VARCHAR", size="128")
		t_rowsProduct2 = ET.SubElement(t_database, "rowsProduct", rowName="price", type="FLOAT", size="10")
		t_rowsComment1 = ET.SubElement(t_database, "rowsComment", rowName="nick", type="VARCHAR", size="32")
		t_rowsComment2 = ET.SubElement(t_database, "rowsComment", rowName="comment", type="TEXT", size="", isText="true") #No ponemos a true isText
		t_rowsComment3 = ET.SubElement(t_database, "rowsComment", rowName="date", type="VARCHAR", size="32")

		t_url = ET.SubElement(t_info, "url", urlBase="http://www.marca.com", urlProducts="http://www.marca.com/futbol/cadiz.html", urlComments="")

		arbol = ET.ElementTree(t_info)
		arbol.write("test.xml")	

		i=0
		with self.assertRaises(SystemExit) as cm:
			main()
		self.assertEqual(cm.exception.code, 1)

		os.remove("test.xml")
