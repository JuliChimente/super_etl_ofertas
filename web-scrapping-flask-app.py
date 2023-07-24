import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from flask import Flask, render_template, request
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['GET','POST'])
def scrape():
    request_productos = request.form['productos_lista']
    navegador = request.form['navegador']
    
    # Convertir la cadena de productos en una lista
    productos_lista = [producto.strip() for producto in request_productos.split(',')]

    def obtener_ofertas(productos_lista, navegador):
        # URL del supermercados
        supermercados = ['https://www.vea.com.ar/','https://www.disco.com.ar/','https://www.jumbo.com.ar/','https://diaonline.supermercadosdia.com.ar/']
        
        lista_super_prod_baratos = pd.DataFrame(columns=['supermercado','nombre','precio','promo','url'])
        
        for lista in productos_lista:
            lista_productos = []  # Lista para almacenar los precios del supermercado actual
            for supermercado in supermercados:
                # Configurar el driver de Selenium y cargar la página web

                if navegador == "Chrome":
                    options = ChromeOptions()
                    options.add_argument("--start-minimized")
                    driver = webdriver.Chrome(options=options)
                elif navegador == "Firefox":
                    options = FirefoxOptions()
                    options.add_argument("--start-minimized")
                    driver = webdriver.Firefox(options=options)
                elif navegador == "Edge":
                    options = EdgeOptions()
                    options.add_argument("--start-minimized")
                    driver = webdriver.Edge(options=options)
                else:
                    raise ValueError("Navegador no soportado")
                
                lista.replace(" ","%20")
                
                driver.get(f'{supermercado}{lista}{"?order=OrderByPriceASC"}')

                super = supermercado.split('.')[1].upper()

                # Esperar hasta que el elemento sea visible
                wait = WebDriverWait(driver, 7)
                
                if "SUPERMERCADOSDIA" in super:
                    elemento = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.vtex-product-price-1-x-currencyContainer')))
                else:
                    elemento = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.contenedor-precio')))
        
                # Obtener el contenido de la página web con BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Obtenemos todos los elementos contenedores de productos
                if "SUPERMERCADOSDIA" in super:
                    productos = soup.find('div', {'class': 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--default pa4'})
                else:
                    productos = soup.find('div', {'class': 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4'})

                # Guardamos el nombre de los productos
                nombre = productos.find('span', {'class': 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body'}).text.strip()
            
                # Su precio
                
                if "JUMBO" in super or "VEA" in super or "DISCO" in super:
                    try:
                        precio = productos.find('div', {'class': 'contenedor-precio'}).span.text
                    except AttributeError:
                        precio = productos.find('p', {'class': 'jumboargentinaio-store-theme-2HGAKpUDWMGu8a66aeeQ56'}).text.strip()
                        partes = precio.split('$')
                        precio = f'${partes[1]}'
                else:   
                    precio = productos.find('span', {'class': 'vtex-product-price-1-x-currencyContainer'}).text.strip()
                    
                if "VEA" in super:
                    try:
                        # Promo Vea %OFF
                        promo = productos.find('span', {'class': 'veaargentina-store-theme-2Vrhf80fWpMRRgLq5y0ZoI'}).text.strip()
                    except AttributeError:
                        try:
                            # Promo Vea 2x1, 50% Off 2da U, etc.
                            tipo_promo = productos.find('span', {'class': 'veaargentina-store-theme-1vId-Z5l1K6K82ho-1PHy6'}).text.strip()
                            precio_promo = productos.find('p', {'class': 'veaargentina-store-theme-2_zxmjIkZPLRBSyGn8OWpv vtex-promotionDisclaimerText'}).text.strip()
                            promo = f'{tipo_promo} {precio_promo}'
                        except AttributeError:
                            promo = 'No tiene promo'
                        
                elif "JUMBO" in super:       
                    try:
                        # Promo Jumbo %OFF
                        promo = productos.find('span', {'class': 'jumboargentinaio-store-theme-2Vrhf80fWpMRRgLq5y0ZoI'}).text.strip()
                    except AttributeError:
                        try:
                            # Promo Jumbo 2x1, 50% Off 2da U, etc.
                            tipo_promo = productos.find('span', {'class': 'jumboargentinaio-store-theme-1fq_v5Ru2hmjMCzmx6XC_E'}).text.strip()
                            precio_promo = productos.find('p', {'class': 'jumboargentinaio-store-theme-2_zxmjIkZPLRBSyGn8OWpv vtex-promotionDisclaimerText'}).text.strip()
                            promo = f'{tipo_promo} {precio_promo}'
                        except AttributeError:
                            try:
                                # 35% OFF con PRIME
                                promo = productos.find('span', {'class': 'jumboargentinaio-store-theme-2tHhEXdEDr-Nq08rzYO7i2'}).text.strip()
                            except AttributeError:
                                promo = 'No tiene promo'
                elif "DISCO" in super:
                    try:
                        # Promo Disco %OFF
                        promo = productos.find('span', {'class': 'discoargentina-store-theme-tha9pV36seWfdnuHGKz68'}).text.strip()
                    except AttributeError:
                        try:
                            # Promo Dia 2x1, 50% Off 2da U, etc.
                            tipo_promo = productos.find('span', {'class': 'discoargentina-store-theme-1fq_v5Ru2hmjMCzmx6XC_E'}).text.strip()
                            precio_promo = productos.find('p', {'class': 'discoargentina-store-theme-2_zxmjIkZPLRBSyGn8OWpv vtex-promotionDisclaimerText'}).text.strip()
                            promo = f'{tipo_promo} {precio_promo}'
                        except AttributeError:
                            try:
                                # 35% OFF con PRIME
                                promo = productos.find('span', {'class': 'discoargentina-store-theme-2tHhEXdEDr-Nq08rzYO7i2'}).text.strip()
                            except AttributeError:
                                    promo = 'No tiene promo'
                elif "SUPERMERCADOSDIA" in super:
                    try:
                        # Promo Dia %OFF
                        promo = productos.find('span', {'class': 'vtex-product-price-1-x-savingsPercentage vtex-product-price-1-x-savingsPercentage--pdp'}).text.strip()
                    except AttributeError:
                        try:
                            # Promo Dia 2x1, 50% Off 2da U, etc.
                            promo = productos.find('span', {'class': 'vtex-product-highlights-2-x-productHighlightText vtex-product-highlights-2-x-productHighlightText--promotions'}).text.strip()
                        except AttributeError:
                            promo = 'No tiene promo'
                
                url = productos.find('a', {'class': 'vtex-product-summary-2-x-clearLink'})['href']
                
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
                    'url': supermercado+url
                }

                # Agregar el diccionario a la lista
                lista_productos.append(producto_dict)

                # Lista de los productos mas baratos por supermercado
                productos_baratos_x_super = pd.DataFrame(lista_productos)
                
                lista_super_prod_baratos = pd.concat([lista_super_prod_baratos, productos_baratos_x_super], ignore_index=True)
            
                # Eliminar filas duplicadas basadas en todas las columnas del DataFrame
                lista_super_prod_baratos = lista_super_prod_baratos.drop_duplicates()
            
        mejores_precios_super = super_mejores_precios(lista_super_prod_baratos)
        
        mejores_precios_lista = lista_mejores_precios(lista_super_prod_baratos)
                    
        return mejores_precios_super, mejores_precios_lista

    mejores_precios_super, mejores_precios_lista = obtener_ofertas(productos_lista, navegador)

    # Devuelve los resultados a la plantilla
    return render_template('results.html', 
                           mejores_precios_super=mejores_precios_super, 
                           mejores_precios_lista=mejores_precios_lista)
    

def lista_mejores_precios(ofertas):
    ofertas_super = ofertas
    
    # Obtener el índice del producto más barato para cada producto único
    indices_menor_precio = ofertas_super.groupby(ofertas_super['nombre'].str.split().str[0])['precio'].idxmin()

    # Obtener el DataFrame con los productos más baratos
    productos_mas_baratos = ofertas_super.loc[indices_menor_precio]

    # Función lambda para formatear los valores como moneda
    formato_moneda = lambda x: f'${x:.2f}'

    # Aplicar la función lambda a la columna 'Precio'
    productos_mas_baratos['precio'] = productos_mas_baratos['precio'].map(formato_moneda)
    
    # Guardar el DataFrame seleccionado
    current_dataframe = productos_mas_baratos
    
    return current_dataframe
        
        
def super_mejores_precios(ofertas):    
    ofertas_super = ofertas
    
    # Calcular la suma de los precios por cada supermercado
    df_suma_precios = ofertas_super.groupby('supermercado')['precio'].sum().reset_index()

    # Encontrar el supermercado con el menor precio total
    supermercado_menor_precio = df_suma_precios.loc[df_suma_precios['precio'].idxmin(), 'supermercado']

    # Filtrar el DataFrame original para obtener las filas del supermercado con el menor precio total
    df_filtrado = ofertas_super[ofertas_super['supermercado'] == supermercado_menor_precio]

    # Crear un nuevo DataFrame con las filas filtradas
    menor_precio_x_supermercado = pd.DataFrame(df_filtrado)

    # Función lambda para formatear los valores como moneda
    formato_moneda = lambda x: f'${x:.2f}'

    # Aplicar la función lambda a la columna 'Precio'
    menor_precio_x_supermercado['precio'] = menor_precio_x_supermercado['precio'].map(formato_moneda)
    
    # Guardar el DataFrame seleccionado
    current_dataframe = menor_precio_x_supermercado
    
    return current_dataframe

if __name__ == '__main__':
    app.run()