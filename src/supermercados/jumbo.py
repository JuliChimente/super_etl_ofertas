from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions

from src.supermercados.supermercado import Supermercado


class Jumbo(Supermercado):
    def __init__(self):
        super().__init__(
            supermercado='https://www.jumbo.com.ar/',
            categorias=['electro', 'tiempo-libre', 'bebidas', 'carnes', 'frutas-y-verduras', 'lacteos', 'perfumeria',
                        'bebes-y-ninos', 'limpieza', 'quesos-y-fiambres', 'congelados', 'panaderia-y-reposteria',
                        'mascotas', 'hogar-y-textil']
        )

    def execute_all(self):

        for categoria in self.categorias:
            encontrado = False
            x = 1  # Variable para controlar las páginas

            while not encontrado:
                try:
                    lista_productos_categoria = []  # Lista para almacenar los productos más baratos del supermercado actual

                    # Configurar el driver de Selenium y cargar la página web
                    options = ChromeOptions()
                    options.add_argument("--start-minimized")
                    driver = webdriver.Chrome(options=options)

                    driver.get(f'{self.supermercado}{categoria}?map=category-1&page={x}')

                    super = self.supermercado.split('.')[1].upper()

                    # Esperar hasta que el elemento sea visible
                    wait = WebDriverWait(driver, 7)

                    elemento = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.contenedor-precio')))

                    # Obtener el contenido de la página web con BeautifulSoup
                    soup = BeautifulSoup(driver.page_source, 'html.parser')

                    # Obtenemos todos los elementos contenedores de productos
                    productos = soup.find('div',
                                          {
                                              'class': 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4'})

                    for producto in productos:
                        # Guardamos el nombre de los productos
                        nombre = producto.find('span',
                                               {
                                                   'class': 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body'}).text.strip()

                        # Su precio
                        try:
                            precio = producto.find('div',
                                                   {'class': 'contenedor-precio'}).span.text
                        except AttributeError:
                            precio = producto.find('p',
                                                   {
                                                       'class': 'jumboargentinaio-store-theme-2HGAKpUDWMGu8a66aeeQ56'}).text.strip()
                            partes = precio.split('$')
                            precio = f'${partes[1]}'

                        try:
                            # Promo Jumbo %OFF
                            promo = producto.find('span',
                                                  {
                                                      'class': 'jumboargentinaio-store-theme-2Vrhf80fWpMRRgLq5y0ZoI'}).text.strip()
                        except AttributeError:
                            try:
                                # Promo Jumbo 2x1, 50% Off 2da U, etc.
                                tipo_promo = producto.find('span',
                                                           {
                                                               'class': 'jumboargentinaio-store-theme-1fq_v5Ru2hmjMCzmx6XC_E'}).text.strip()
                                precio_promo = producto.find('p',
                                                             {
                                                                 'class': 'jumboargentinaio-store-theme-2_zxmjIkZPLRBSyGn8OWpv vtex-promotionDisclaimerText'}).text.strip()
                                promo = f'{tipo_promo} {precio_promo}'
                            except AttributeError:
                                try:
                                    # 35% OFF con PRIME
                                    promo = producto.find('span',
                                                          {
                                                              'class': 'jumboargentinaio-store-theme-2tHhEXdEDr-Nq08rzYO7i2'}).text.strip()
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
                            'url': self.supermercado + url
                        }

                        lista_productos_categoria.append(producto_dict)

                    self.lista_productos.extend(lista_productos_categoria)

                    x += 1

                except:
                    elemento = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, 'div.vtex-search-result-3-x-searchNotFound')))
                    encontrado = True

        self.cargar_productos_a_db()
