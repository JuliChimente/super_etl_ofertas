from src.services.rds import RDS

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions

from abc import ABC, abstractmethod


class Supermercado(ABC):
    def __init__(self, supermercado: str, categorias: list):
        self.supermercado = supermercado
        self.categorias = categorias
        self.lista_productos = []

    def cargar_productos_a_db(self):
        rds = RDS()

        # Ejecutar una consulta para insertar los productos en la tabla
        consulta = 'INSERT INTO productos (supermercado, nombre_producto, precio_producto, promocion_producto, url_producto) VALUES '

        for producto in self.lista_productos:
            consulta += str(
                (producto['supermercado'], producto['nombre'], producto['precio'], producto['promo'], producto['url']))
        rds.execute_query(consulta)
        rds.disconnect()

    def recorrer_categorias(self):
        for categoria in self.categorias:
            self.ejecutar_categoria(categoria)

    def ejecutar_categoria(self, categoria: str):
        encontrado = False
        x = 1
        while not encontrado:
            options = ChromeOptions()
            driver = self.init_driver(options)
            try:
                lista_productos_categoria = self.scrape_page(driver, self.supermercado, categoria, x)
                self.lista_productos.extend(lista_productos_categoria)
                x += 1
            except:
                elemento = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'div.vtex-search-result-3-x-searchNotFound')))
                encontrado = True

        self.cargar_productos_a_db()

    @abstractmethod
    def scrape_page(self, driver, supermercado, categoria, x):
        pass

    @abstractmethod
    def init_driver(self, options):
        pass

    @abstractmethod
    def extract_price(self, producto):
        pass

    @abstractmethod
    def extract_promo(self, producto):
        pass
