import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions

from supermercados.supermercado import Supermercado


class Dia(Supermercado):
    def __init__(self):
        super().__init__(
            supermercado='https://diaonline.supermercadosdia.com.ar/',
            categorias=['electro-hogar', 'hogar-y-deco', 'mascotas', 'bebes-y-ninos', 'limpieza', 'congelados', 'bebidas',
                        'frescos', 'desayuno', 'almacen']
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
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
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
        try:
            nombre = producto.find('span',
                                    {'class': 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body'}).text.strip()
        except AttributeError:
            return None
            
        precio = self.extract_price(producto)
        promo = self.extract_promo(producto)
        if 'No tiene promo' not in promo:
            precio_mayorista = self.whosale_price(precio, promo)
            precio_mayorista = precio_mayorista.replace('.', '').replace(',', '.').replace('$', '')
            precio_mayorista = float(precio_mayorista)
        else:
            precio_mayorista = "NULL"
            promo = "NULL"
           
        url = producto.find('a', {'class': 'vtex-product-summary-2-x-clearLink'})['href']
        precio = precio.replace('.', '').replace(',', '.').replace('$', '')
        producto_info_dict = {'precio_unit': float(precio), 'precio_mayorista': precio_mayorista, 'promo': promo, 'nombre': nombre, 'url': supermercado + url}
        
        return producto_info_dict

    def scrape_page(self, driver, supermercado: str, categoria: str, x: int) -> pd.DataFrame:
        driver.get(f'{supermercado}{categoria}?map=category-1&page={x}')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Esperar hasta que el elemento sea visible
        wait = WebDriverWait(driver, 5)
        elemento = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.vtex-product-price-1-x-currencyContainer')))
        productos = soup.find_all('div', 
                                    {'class': 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--default pa4'})[:5]
        
        for producto in productos:
            producto_info_dict = self.parse_product_info(producto)
            if producto_info_dict is None:
                return None
            self.df_productos.loc[len(self.df_productos)] = [producto_info_dict['nombre'], producto_info_dict['url']]
            self.df_precio_mayorista.loc[len(self.df_precio_mayorista)] = [producto_info_dict['precio_mayorista'], producto_info_dict['promo']]
            self.df_precio_unit.loc[len(self.df_precio_unit)] = [producto_info_dict['precio_unit']]
    
        return True

if __name__ == "__main__":
    dia = Dia()
    dia.recorrer_categorias()
