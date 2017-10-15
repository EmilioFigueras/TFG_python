import TFG
import xml.etree.cElementTree as ET #XML Test

from unittest import TestCase
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
