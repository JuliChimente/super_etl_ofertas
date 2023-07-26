from bs4 import BeautifulSoup
from selenium import webdriver
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

    def init_driver(self, options: ChromeOptions) -> webdriver:
        options.add_argument("--start-minimized")
        return webdriver.Chrome(options=options)

    def extract_price(self, producto) -> str:
        try:
            precio = producto.find('div', {'class': 'contenedor-precio'}).span.text
        except AttributeError:
            precio = producto.find('p', {'class': 'jumboargentinaio-store-theme-2HGAKpUDWMGu8a66aeeQ56'}).text.strip()
            partes = precio.split('$')
            precio = f'${partes[1]}'
        return precio

    def extract_promo(self, producto) -> str:
        try:
            promo = producto.find('span', {'class': 'jumboargentinaio-store-theme-2Vrhf80fWpMRRgLq5y0ZoI'}).text.strip()
        except AttributeError:
            try:
                tipo_promo = producto.find('span', {
                    'class': 'jumboargentinaio-store-theme-1fq_v5Ru2hmjMCzmx6XC_E'}).text.strip()
                precio_promo = producto.find('p', {
                    'class': 'jumboargentinaio-store-theme-2_zxmjIkZPLRBSyGn8OWpv vtex-promotionDisclaimerText'}).text.strip()
                promo = f'{tipo_promo} {precio_promo}'
            except AttributeError:
                try:
                    promo = producto.find('span',
                                          {'class': 'jumboargentinaio-store-theme-2tHhEXdEDr-Nq08rzYO7i2'}).text.strip()
                except AttributeError:
                    promo = 'No tiene promo'
        return promo

    def parse_product_info(self, producto, supermercado: str) -> dict:
        nombre = producto.find('span', {
            'class': 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body'}).text.strip()
        precio = self.extract_price(producto)
        promo = self.extract_promo(producto)
        url = producto.find('a', {'class': 'vtex-product-summary-2-x-clearLink'})['href']
        precio = precio.replace('.', '').replace(',', '.').replace('$', '')
        producto_dict = {'supermercado': supermercado, 'nombre': nombre, 'precio': float(precio), 'promo': promo,
                         'url': supermercado + url}
        return producto_dict

    def scrape_page(self, driver, supermercado: str, categoria: str, x: int) -> list[dict]:
        lista_productos_categoria = []
        driver.get(f'{supermercado}{categoria}?map=category-1&page={x}')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        productos = soup.find('div', {
            'class': 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4'})
        for producto in productos:
            producto_dict = self.parse_product_info(producto, supermercado.split('.')[1].upper())
            lista_productos_categoria.append(producto_dict)
        return lista_productos_categoria
