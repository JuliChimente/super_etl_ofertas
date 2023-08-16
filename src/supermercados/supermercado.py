from services.rds import RDS
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions

from abc import ABC, abstractmethod


class Supermercado(ABC):
    def __init__(self, supermercado: str, categorias: list):
        self.supermercado = supermercado
        self.categorias = categorias
        self.df_productos = pd.DataFrame({'nombre': [], 'url': []})
        self.df_precio_mayorista = pd.DataFrame({'precio_mayorista': [], 'promo': []})
        self.df_precio_unit = pd.DataFrame({'precio_unit': []})

    def cargar_precio_unit_a_db(self):
        rds = RDS()

        # Ejecutar una consulta para insertar los productos en la tabla
        consulta = 'INSERT INTO precio_unit (precio) VALUES '

        for producto in self.df_precio_unit:
            consulta += str(
                (producto['precio_unit']))
        rds.execute_query(consulta)
        rds.disconnect()
        
    def cargar_precio_mayorista_a_db(self):
        rds = RDS()

        # Ejecutar una consulta para insertar los productos en la tabla
        consulta = 'INSERT INTO precio_mayorista (precio, promo) VALUES '

        for producto in self.df_precio_mayorista:
            consulta += str(
                (producto['precio_mayorista'], producto['promo']))
        rds.execute_query(consulta)
        rds.disconnect()
            
        
    def cargar_productos_a_db(self):
        rds = RDS()

        # Ejecutar una consulta para insertar los productos en la tabla
        consulta = 'INSERT INTO producto (producto_nombre, url) VALUES '

        for producto in self.df_productos:
            consulta += str(
                (producto['nombre'], producto['url']))
        rds.execute_query(consulta)
        rds.disconnect()

    def recorrer_categorias(self):
        for categoria in self.categorias:
            self.ejecutar_categoria(categoria)

    def ejecutar_categoria(self, categoria: str):
        x = 1
        while True:
            options = ChromeOptions()
            driver = self.init_driver(options)
        
            if self.scrape_page(driver, self.supermercado, categoria, x) is None:
                break
            
            x += 1

        self.cargar_precio_unit_a_db()
        self.cargar_precio_mayorista_a_db()
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
