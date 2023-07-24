import pandas as pd
import mysql.connector
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions

def vea():
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_contraseña",
        database="nombre_de_la_base_de_datos"
    )

    lista_productos = []  # Lista para almacenar los productos más baratos de todos los supermercados

    categorias = ['electro', 'tiempo-libre', 'bebidas', 'carnes', 'frutas-y-verduras', 'lacteos', 'perfumeria',
                  'bebes-y-ninos', 'limpieza', 'quesos-y-fiambres', 'congelados', 'panaderia-y-reposteria',
                  'mascotas', 'hogar-y-textil']

    for categoria in categorias:
        encontrado = False
        x = 1  # Variable para controlar las páginas

        while not encontrado:
            try:
                lista_productos_categoria = []  # Lista para almacenar los productos más baratos del supermercado actual

                options = ChromeOptions()
                options.add_argument("--start-minimized")
                driver = webdriver.Chrome(options=options)

                supermercado = 'https://www.vea.com.ar/'

                driver.get(f'{supermercado}{categoria}?map=category-1&page={x}')

                super = supermercado.split('.')[1].upper()

                wait = WebDriverWait(driver, 7)
                elemento = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.contenedor-precio')))

                soup = BeautifulSoup(driver.page_source, 'html.parser')

                productos = soup.find_all('div', 
                                          {'class': 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4'})

                for producto in productos:
                    nombre = producto.find('span',
                                           {'class': 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body'}).text.strip()
                    precio = producto.find('div', 
                                           {'class': 'contenedor-precio'}).span.text

                    try:
                        promo = producto.find('span', 
                                              {'class': 'veaargentina-store-theme-2Vrhf80fWpMRRgLq5y0ZoI'}).text.strip()
                    except AttributeError:
                        try:
                            tipo_promo = producto.find('span',
                                                       {'class': 'veaargentina-store-theme-1vId-Z5l1K6K82ho-1PHy6'}).text.strip()
                            precio_promo = producto.find('p',
                                                         {'class': 'veaargentina-store-theme-2_zxmjIkZPLRBSyGn8OWpv vtex-promotionDisclaimerText'}).text.strip()
                            promo = f'{tipo_promo} {precio_promo}'
                        except AttributeError:
                            promo = 'No tiene promo'

                    url = producto.find('a', {'class': 'vtex-product-summary-2-x-clearLink'})['href']

                    url.split('/')[1]

                    precio = precio.replace('.', '')
                    precio = precio.replace(',', '.')
                    precio = precio.replace('$', '')
                    precio = float(precio)

                    producto_dict = {
                        'supermercado': super,
                        'nombre': nombre,
                        'precio': precio,
                        'promo': promo,
                        'url': supermercado + url
                    }

                    lista_productos_categoria.append(producto_dict)

                lista_productos.extend(lista_productos_categoria)

                x += 1

            except:
                elemento = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'div.vtex-search-result-3-x-searchNotFound')))
                encontrado = True

    # Crear un cursor para ejecutar consultas
    cursor = conexion.cursor()

    # Ejecutar una consulta para insertar los productos en la tabla
    consulta = "INSERT INTO productos (supermercado, nombre_producto, precio_producto, promocion_producto, url_producto) VALUES (%s, %s, %s, %s, %s)"
    productos_tuples = [(producto['supermercado'], producto['nombre'], producto['precio'], producto['promo'],
                         producto['url']) for producto in lista_productos]
    cursor.executemany(consulta, productos_tuples)

    # Confirmar los cambios en la base de datos
    conexion.commit()

    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()

        
def jumbo(productos_lista):
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_contraseña",
        database="nombre_de_la_base_de_datos"
    )

    lista_productos = []  # Lista para almacenar los productos más baratos de todos los supermercados

    categorias = ['electro', 'tiempo-libre', 'bebidas', 'carnes', 'frutas-y-verduras', 'lacteos', 'perfumeria',
                  'bebes-y-ninos', 'limpieza', 'quesos-y-fiambres', 'congelados', 'panaderia-y-reposteria',
                  'mascotas', 'hogar-y-textil']

    for categoria in categorias:
        encontrado = False
        x = 1  # Variable para controlar las páginas

        while not encontrado:
            try:
                lista_productos_categoria = []  # Lista para almacenar los productos más baratos del supermercado actual

                # Configurar el driver de Selenium y cargar la página web
                options = ChromeOptions()
                options.add_argument("--start-minimized")
                driver = webdriver.Chrome(options=options)
                
                supermercado = 'https://www.jumbo.com.ar/'
                
                driver.get(f'{supermercado}{categoria}?map=category-1&page={x}')

                super = supermercado.split('.')[1].upper()

                # Esperar hasta que el elemento sea visible
                wait = WebDriverWait(driver, 7)
                
                elemento = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.contenedor-precio')))

                # Obtener el contenido de la página web con BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Obtenemos todos los elementos contenedores de productos
                productos = soup.find('div', 
                                      {'class': 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4'})

                for producto in productos:
                    # Guardamos el nombre de los productos
                    nombre = producto.find('span', 
                                           {'class': 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body'}).text.strip()
                
                    # Su precio
                    try:
                        precio = producto.find('div', 
                                               {'class': 'contenedor-precio'}).span.text
                    except AttributeError:
                        precio = producto.find('p', 
                                               {'class': 'jumboargentinaio-store-theme-2HGAKpUDWMGu8a66aeeQ56'}).text.strip()
                        partes = precio.split('$')
                        precio = f'${partes[1]}'
            
                    try:
                        # Promo Jumbo %OFF
                        promo = producto.find('span', 
                                              {'class': 'jumboargentinaio-store-theme-2Vrhf80fWpMRRgLq5y0ZoI'}).text.strip()
                    except AttributeError:
                        try:
                            # Promo Jumbo 2x1, 50% Off 2da U, etc.
                            tipo_promo = producto.find('span', 
                                                       {'class': 'jumboargentinaio-store-theme-1fq_v5Ru2hmjMCzmx6XC_E'}).text.strip()
                            precio_promo = producto.find('p', 
                                                         {'class': 'jumboargentinaio-store-theme-2_zxmjIkZPLRBSyGn8OWpv vtex-promotionDisclaimerText'}).text.strip()
                            promo = f'{tipo_promo} {precio_promo}'
                        except AttributeError:
                            try:
                                # 35% OFF con PRIME
                                promo = producto.find('span', 
                                                      {'class': 'jumboargentinaio-store-theme-2tHhEXdEDr-Nq08rzYO7i2'}).text.strip()
                            except AttributeError:
                                promo = 'No tiene promo'
                    
                    url = producto.find('a', 
                                        {'class': 'vtex-product-summary-2-x-clearLink'})['href']

                    url.split('/')[1]

                    precio = precio.replace('.', '')
                    precio = precio.replace(',', '.')
                    precio = precio.replace('$', '')
                    precio = float(precio)

                    producto_dict = {
                        'supermercado': super,
                        'nombre': nombre,
                        'precio': precio,
                        'promo': promo,
                        'url': supermercado + url
                    }

                    lista_productos_categoria.append(producto_dict)

                lista_productos.extend(lista_productos_categoria)

                x += 1

            except:
                elemento = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'div.vtex-search-result-3-x-searchNotFound')))
                encontrado = True
    
    # Crear un cursor para ejecutar consultas
    cursor = conexion.cursor()

    # Ejecutar una consulta para insertar los productos en la tabla
    consulta = "INSERT INTO productos (supermercado, nombre_producto, precio_producto, promocion_producto, url_producto) VALUES (%s, %s, %s, %s, %s)"
    productos_tuples = [(producto['supermercado'], producto['nombre'], producto['precio'], producto['promo'],
                         producto['url']) for producto in lista_productos]
    cursor.executemany(consulta, productos_tuples)

    # Confirmar los cambios en la base de datos
    conexion.commit()

    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
        
def dia(productos_lista):
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_contraseña",
        database="nombre_de_la_base_de_datos"
    )

    lista_productos = []  # Lista para almacenar los productos más baratos de todos los supermercados

    categorias = ['electro', 'tiempo-libre', 'bebidas', 'carnes', 'frutas-y-verduras', 'lacteos', 'perfumeria',
                  'bebes-y-ninos', 'limpieza', 'quesos-y-fiambres', 'congelados', 'panaderia-y-reposteria',
                  'mascotas', 'hogar-y-textil']

    for categoria in categorias:
        encontrado = False
        x = 1  # Variable para controlar las páginas

        while not encontrado:
            try:
                lista_productos_categoria = []  # Lista para almacenar los productos más baratos del supermercado actual

                # Configurar el driver de Selenium y cargar la página web
                options = ChromeOptions()
                options.add_argument("--start-minimized")
                driver = webdriver.Chrome(options=options)
                
                supermercado = 'https://diaonline.supermercadosdia.com.ar/'
        
                driver.get(f'{supermercado}{categoria}?map=category-1&page={x}')

                super = supermercado.split('.')[1].upper()

                # Esperar hasta que el elemento sea visible
                wait = WebDriverWait(driver, 7)
                
                elemento = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.vtex-product-price-1-x-currencyContainer')))
                
                # Obtener el contenido de la página web con BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Obtenemos todos los elementos contenedores de productos
                productos = soup.find('div', 
                                      {'class': 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--default pa4'})
                
                for producto in productos:
                    # Guardamos el nombre de los productos
                    nombre = producto.find('span', 
                                            {'class': 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body'}).text.strip()
                
                    # Su precio
                    precio = producto.find('span', 
                                            {'class': 'vtex-product-price-1-x-currencyContainer'}).text.strip()
                        
                    try:
                        # Promo Dia %OFF
                        promo = producto.find('span', 
                                               {'class': 'vtex-product-price-1-x-savingsPercentage vtex-product-price-1-x-savingsPercentage--pdp'}).text.strip()
                    except AttributeError:
                        try:
                            # Promo Dia 2x1, 50% Off 2da U, etc.
                            promo = producto.find('span', 
                                                   {'class': 'vtex-product-highlights-2-x-productHighlightText vtex-product-highlights-2-x-productHighlightText--promotions'}).text.strip()
                        except AttributeError:
                            promo = 'No tiene promo'
                    
                    url = producto.find('a', 
                                         {'class': 'vtex-product-summary-2-x-clearLink'})['href']

                    url.split('/')[1]

                    precio = precio.replace('.', '')
                    precio = precio.replace(',', '.')
                    precio = precio.replace('$', '')
                    precio = float(precio)

                    producto_dict = {
                        'supermercado': super,
                        'nombre': nombre,
                        'precio': precio,
                        'promo': promo,
                        'url': supermercado + url
                    }

                    lista_productos_categoria.append(producto_dict)

                lista_productos.extend(lista_productos_categoria)

                x += 1

            except:
                elemento = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'div.vtex-search-result-3-x-searchNotFound')))
                encontrado = True
    
    # Crear un cursor para ejecutar consultas
    cursor = conexion.cursor()

    # Ejecutar una consulta para insertar los productos en la tabla
    consulta = "INSERT INTO productos (supermercado, nombre_producto, precio_producto, promocion_producto, url_producto) VALUES (%s, %s, %s, %s, %s)"
    productos_tuples = [(producto['supermercado'], producto['nombre'], producto['precio'], producto['promo'],
                         producto['url']) for producto in lista_productos]
    cursor.executemany(consulta, productos_tuples)

    # Confirmar los cambios en la base de datos
    conexion.commit()

    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
        
def disco():
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_contraseña",
        database="nombre_de_la_base_de_datos"
    )

    lista_productos = []  # Lista para almacenar los productos más baratos de todos los supermercados

    categorias = ['electro', 'tiempo-libre', 'bebidas', 'carnes', 'frutas-y-verduras', 'lacteos', 'perfumeria',
                  'bebes-y-ninos', 'limpieza', 'quesos-y-fiambres', 'congelados', 'panaderia-y-reposteria',
                  'mascotas', 'hogar-y-textil']

    for categoria in categorias:
        encontrado = False
        x = 1  # Variable para controlar las páginas

        while not encontrado:
            try:
                lista_productos_categoria = []  # Lista para almacenar los productos más baratos del supermercado actual

                # Configurar el driver de Selenium y cargar la página web
                options = ChromeOptions()
                options.add_argument("--start-minimized")
                driver = webdriver.Chrome(options=options)
                
                supermercado = 'https://www.disco.com.ar/'
        
                driver.get(f'{supermercado}{categoria}?map=category-1&page={x}')

                super = supermercado.split('.')[1].upper()

                # Esperar hasta que el elemento sea visible
                wait = WebDriverWait(driver, 7)
                
                elemento = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.contenedor-precio')))

                # Obtener el contenido de la página web con BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Obtenemos todos los elementos contenedores de productos
                productos = soup.find_all('div', 
                                          {'class': 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4'})

                for producto in productos:
                    # Guardamos el nombre de los productos
                    nombre = producto.find('span', 
                                           {'class': 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body'}).text.strip()
                
                    # Su precio
                    precio = producto.find('div', 
                                           {'class': 'contenedor-precio'}).span.text
                
                    try:
                        # Promo Disco %OFF
                        promo = producto.find('span', 
                                              {'class': 'discoargentina-store-theme-tha9pV36seWfdnuHGKz68'}).text.strip()
                    except AttributeError:
                        try:
                            # Promo Dia 2x1, 50% Off 2da U, etc.
                            tipo_promo = producto.find('span', 
                                                       {'class': 'discoargentina-store-theme-1fq_v5Ru2hmjMCzmx6XC_E'}).text.strip()
                            precio_promo = producto.find('p', 
                                                         {'class': 'discoargentina-store-theme-2_zxmjIkZPLRBSyGn8OWpv vtex-promotionDisclaimerText'}).text.strip()
                            promo = f'{tipo_promo} {precio_promo}'
                        except AttributeError:
                            try:
                                # 35% OFF con PRIME
                                promo = producto.find('span', 
                                                      {'class': 'discoargentina-store-theme-2tHhEXdEDr-Nq08rzYO7i2'}).text.strip()
                            except AttributeError:
                                    promo = 'No tiene promo'
                    
                    url = producto.find('a', 
                                        {'class': 'vtex-product-summary-2-x-clearLink'})['href']

                    url.split('/')[1]

                    precio = precio.replace('.', '')
                    precio = precio.replace(',', '.')
                    precio = precio.replace('$', '')
                    precio = float(precio)

                    producto_dict = {
                        'supermercado': super,
                        'nombre': nombre,
                        'precio': precio,
                        'promo': promo,
                        'url': supermercado + url
                    }

                    lista_productos_categoria.append(producto_dict)

                lista_productos.extend(lista_productos_categoria)

                x += 1

            except:
                elemento = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'div.vtex-search-result-3-x-searchNotFound')))
                encontrado = True
    
    # Crear un cursor para ejecutar consultas
    cursor = conexion.cursor()

    # Ejecutar una consulta para insertar los productos en la tabla
    consulta = "INSERT INTO productos (supermercado, nombre_producto, precio_producto, promocion_producto, url_producto) VALUES (%s, %s, %s, %s, %s)"
    productos_tuples = [(producto['supermercado'], producto['nombre'], producto['precio'], producto['promo'],
                         producto['url']) for producto in lista_productos]
    cursor.executemany(consulta, productos_tuples)

    # Confirmar los cambios en la base de datos
    conexion.commit()

    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
def carrefour():
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_contraseña",
        database="nombre_de_la_base_de_datos"
    )

    lista_productos = []  # Lista para almacenar los productos más baratos de todos los supermercados

    categorias = ['Electro-y-tecnologia', 'Bazar-y-textil', 'Desayuno-y-merienda', 'Bebidas', 'Lacteos-y-productos-frescos', 
                    'Carnes-y-Pescados', 'Frutas-y-Verduras', 'Panaderia', 'Congelados', 'Limpieza', 'Perfumeria', 'Mundo-Bebe', 'Mascotas']

    for categoria in categorias:
        encontrado = False
        x = 1  # Variable para controlar las páginas

        while not encontrado:
            try:
                lista_productos_categoria = []  # Lista para almacenar los productos más baratos del supermercado actual

                # Configurar el driver de Selenium y cargar la página web
                options = ChromeOptions()
                options.add_argument("--start-minimized")
                driver = webdriver.Chrome(options=options)
                
                supermercado = 'https://www.carrefour.com.ar/'
        
                driver.get(f'{supermercado}{categoria}{"?map=category-1&page="}{x}')

                super = supermercado.split('.')[1].upper()

                # Esperar hasta que el elemento sea visible
                wait = WebDriverWait(driver, 7)
                
                try:
                    elemento = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.valtech-carrefourar-product-price-0-x-currencyContainer')))
                except:
                    continue

                # Obtener el contenido de la página web con BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Obtenemos todos los elementos contenedores de productos
                productos = soup.find_all('div', 
                                            {'class': 'valtech-carrefourar-product-summary-status-0-x-container valtech-carrefourar-product-summary-status-0-x-productNotAdded flex flex-column h-100'})

                for producto in productos:
                    try:
                        # Precio con Tarjeta Carrefour
                        precio = producto.find('span', 
                                            {'class': 'valtech-carrefourar-product-price-0-x-currencyContainer'}).text

                        # Precio sin Tarjeta Carrefour
                        #precio = producto.find('span', 
                                            #{'class': 'valtech-carrefourar-product-price-0-x-listPriceValue strike'}).text
                    except AttributeError:
                        continue
                    
                    # Guardamos el nombre de los productos
                    nombre = producto.find('h3', 
                                            {'class': 'vtex-product-summary-2-x-productNameContainer mv0 vtex-product-summary-2-x-nameWrapper overflow-hidden c-on-base f5'}).span.text
                    
                    try:
                        # Promo Carrefour %OFF
                        promo = producto.find('span', 
                                                {'class': 'valtech-carrefourar-product-price-0-x-discountPercentage f6 lh-copy'}).text.strip()
                    except AttributeError:
                        try:
                            # Promo Carrefour con tarjeta Carrefour
                            promo = producto.find('span', 
                                                    {'class': 'valtech-carrefourar-product-highlights-0-x-productHighlightText'}).text
                        
                            # A revisar, agregar una nueva columna de precio sin promocion, en caso de que se necesite usar tarjeta para la misma.
                        
                        except AttributeError:
                            try:
                                # Promo Carrefour con tarjeta Carrefour
                                promo = producto.find('span', 
                                                        {'class': 'valtech-carrefourar-product-highlights-0-x-productHighlightText'}).text
                                
                                # Promo Carrefour Adicional
                                promo2 = producto.find('span', 
                                                        {'class': 'valtech-carrefourar-product-highlights-0-x-productHighlightText'}).span.text

                                promo += promo2
                                
                            except AttributeError:
                                try:
                                    # Promo Carrefour Adicional
                                    promo = producto.find('span', 
                                                            {'class': 'valtech-carrefourar-product-highlights-0-x-productHighlightText'}).span.text
                                except AttributeError:
                                        promo = 'No tiene promo'
                                        
                    if 'MI CRF' in promo:
                        precio_sin_promo = producto.find('span', 
                                                    {'class': 'valtech-carrefourar-product-price-0-x-listPriceValue strike'}).text
                    else:
                        precio_sin_promo = precio
                    
                    url = producto.find('a', 
                                        {'class': 'vtex-product-summary-2-x-clearLink'})['href']

                    url.split('/')[1]

                    precios = [precio, precio_sin_promo]

                    for precios_int in precios:
                        precios_int = precios_int.replace('.', '')
                        precios_int = precios_int.replace(',', '.')
                        precios_int = precios_int.replace('$', '')
                        precios_int = float(precios_int)

                    producto_dict = {
                        'supermercado': super,
                        'nombre': nombre,
                        'precio': precio,
                        'promo': promo,
                        'url': supermercado + url,
                        'precio sin promo': precio_sin_promo
                    }

                    lista_productos_categoria.append(producto_dict)

                lista_productos.extend(lista_productos_categoria)

                x += 1

            except:
                elemento = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'div.valtech-carrefourar-search-result-0-x-searchNotFound')))
                encontrado = True
    
    # Crear un cursor para ejecutar consultas
    cursor = conexion.cursor()

    # Ejecutar una consulta para insertar los productos en la tabla
    consulta = "INSERT INTO productos (supermercado, nombre_producto, precio_producto, promocion_producto, url_producto) VALUES (%s, %s, %s, %s, %s)"
    productos_tuples = [(producto['supermercado'], producto['nombre'], producto['precio'], producto['promo'],
                         producto['url']) for producto in lista_productos]
    cursor.executemany(consulta, productos_tuples)

    # Confirmar los cambios en la base de datos
    conexion.commit()

    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
def coto():
    