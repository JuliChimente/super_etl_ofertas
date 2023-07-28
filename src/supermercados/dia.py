import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from src.supermercados.supermercado import Supermercado


class Dia(Supermercado):
    def __init__(self):
        super().__init__(
            supermercado='https://diaonline.supermercadosdia.com.ar/',
            categorias=['electro', 'tiempo-libre', 'bebidas', 'carnes', 'frutas-y-verduras', 'lacteos', 'perfumeria',
                        'bebes-y-ninos', 'limpieza', 'quesos-y-fiambres', 'congelados', 'panaderia-y-reposteria',
                        'mascotas', 'hogar-y-textil']
        )
        
    def whosale_price(precio, promo):
        if "x" in promo:
            # Promociones del tipo "NxM"
            promo_parts = promo.split('x')
            cantidad_pagar = int(promo_parts[1])
            cantidad_recibir = int(promo_parts[0])
            precio_total_promo = precio * cantidad_pagar
            precio_mayorista = precio_total_promo / cantidad_recibir
        elif "x" not in promo and "$" in promo:
            # Promociones del tipo "Nx$M"
            promo_parts = promo.split('$')
            cantidad_pagar = int(promo_parts[0])
            precio_promo = int(promo_parts[1])
            precio_mayorista = precio_promo / cantidad_pagar
        elif "2do" in promo:
            # Promociones del tipo "2do 70%"
            match = re.search(r'\d+', promo)
            descuento = int(match.group(0)) / 100
            precio_mayorista = precio * (1 - descuento)
        else:
            # Otros formatos de promociones
            match = re.search(r'Llevás (\d+), (\d+) c/u', promo)
            if match:
                cantidad_comprada = int(match.group(1))
                precio_total = int(match.group(2))
                precio_mayorista = precio_total / cantidad_comprada
            else:
                raise ValueError("Promoción no reconocida")

        return precio_mayorista    

    def init_driver(self, options: ChromeOptions) -> webdriver:
        options.add_argument("--start-minimized")
        return webdriver.Chrome(options=options)

    def extract_price(self, producto) -> str:
        # Precio con/sin % descuento
        precio = producto.find('span',
                                {'class': 'vtex-product-price-1-x-currencyContainer'}).text.strip()
        return precio
    
    def extract_promo(self, producto) -> str:
        try:
            # 4x3
            promo = producto.find('span', 
                                  {'class': 'vtex-product-highlights-2-x-productHighlightText vtex-product-highlights-2-x-productHighlightText--promotions'}).text.strip()
            
        except AttributeError:
                    promo = 'No tiene promo'
                    
        return promo

    def parse_product_info(self, producto, supermercado: str) -> dict:
        nombre = producto.find('span',
                                {'class': 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body'}).text.strip()
        precio = self.extract_price(producto)
        promo = self.extract_promo(producto)
        if 'No tiene promo' not in promo:
            precio_mayorista = self.whosale_price(precio, promo)

        url = producto.find('a', {'class': 'vtex-product-summary-2-x-clearLink'})['href']
        precio = precio.replace('.', '').replace(',', '.').replace('$', '')
        precio_mayorista = precio_mayorista.replace('.', '').replace(',', '.').replace('$', '')
        super_dict = {'supermercado': supermercado.split('.')[1].upper()}
        precio_unit_dict = {'precio': float(precio), 'precio comunidad': float(precio)}
        precio_mayorista_dict = {'precio': float(precio_mayorista), 'promo': promo, 'precio comunidad': float(precio)}
        producto_dict = {'nombre': nombre, 'url': supermercado + url}
        
        return super_dict, precio_unit_dict, precio_mayorista_dict, producto_dict

    def scrape_page(self, driver, supermercado: str, categoria: str, x: int) -> pd.DataFrame:
        driver.get(f'{supermercado}{categoria}?map=category-1&page={x}')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        productos = soup.find_all('div', 
                                    {'class': 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--default pa4'})
        for producto in productos:
            super_dict, precio_unit_dict, precio_mayorista_dict, producto_dict = self.parse_product_info(producto, supermercado.split('.')[1].upper())
            self.df_productos.append(producto_dict)
            self.df_precio_mayorista.append(precio_mayorista_dict)
            self.df_precio_unit.append(precio_unit_dict)
            self.df_super.append(super_dict)