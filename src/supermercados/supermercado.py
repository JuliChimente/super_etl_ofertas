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
        print('Tratamos de cargar precio unit')
        rds = RDS()
        
        # Tamaño del lote
        tamanio_lote = 1000

        # Obtener la longitud (número de filas) del DataFrame
        longitud = self.df_precio_unit.shape[0]

        print("La longitud del DataFrame precio_unit es:", longitud)
        # Iterar sobre el DataFrame en lotes y insertar los datos en la base de datos
        for i in range(0, len(self.df_precio_unit), tamanio_lote):
            print('Entramos al for')
            batch = self.df_precio_unit[i:i + tamanio_lote]
            values = ', '.join([f"({row['precio_unit']}" for _, row in batch.iterrows()])
            
            # Crear la consulta SQL de inserción en lote
            query = f"INSERT INTO precio_unit (precio) VALUES {values}"
            
            # Ejecutar la consulta
            rds.execute_query(query)
        rds.disconnect()
        
    def cargar_precio_mayorista_a_db(self):
        print('Tratamos de cargar precio mayorista')
        rds = RDS()

        # Tamaño del lote
        tamanio_lote = 1000
        
        # Obtener la longitud (número de filas) del DataFrame
        longitud = self.df_precio_mayorista.shape[0]

        print("La longitud del DataFrame precio_mayorista es:", longitud)
        # Iterar sobre el DataFrame en lotes y insertar los datos en la base de datos
        for i in range(0, len(self.df_precio_mayorista), tamanio_lote):
            print('Entramos al for')
            batch = self.df_precio_mayorista[i:i + tamanio_lote]
            values = ', '.join([f"({row['precio_mayorista']}, '{row['promo']}')" for _, row in batch.iterrows()])
            
            # Crear la consulta SQL de inserción en lote
            query = f"INSERT INTO precio_mayorista (precio, promo) VALUES {values}"
            
            # Ejecutar la consulta
            rds.execute_query(query)
        rds.disconnect()
            
        
    def cargar_productos_a_db(self):
        print('Tratamos de cargar productos')
        rds = RDS()

        # Tamaño del lote
        tamanio_lote = 1000

        # Obtener la longitud (número de filas) del DataFrame
        longitud = self.df_productos.shape[0]

        print("La longitud del DataFrame productos es:", longitud)
        # Iterar sobre el DataFrame en lotes y insertar los datos en la base de datos
        for i in range(0, len(self.df_productos), tamanio_lote):
            print('Entramos al for')
            batch = self.df_productos[i:i + tamanio_lote]
            values = ', '.join([f"({row['nombre']}, '{row['url']}')" for _, row in batch.iterrows()])
            
            # Crear la consulta SQL de inserción en lote
            query = f"INSERT INTO producto (producto_nombre, url) VALUES {values}"
            
            # Ejecutar la consulta
            rds.execute_query(query)
        rds.disconnect()

    def recorrer_categorias(self):
        print(f'Recorremos Categoria: {categoria}')
        for categoria in self.categorias:
            self.ejecutar_categoria(categoria)

    def ejecutar_categoria(self, categoria: str):
        print(f'Ejecutamos Categoria: {categoria}')
        x = 1
        while True:
            options = ChromeOptions()
            driver = self.init_driver(options)
        
            if self.scrape_page(driver, self.supermercado, categoria, x) is None:
                break
            
            x += 1

        print('Cargamos precio_unit_a_db')
        self.cargar_precio_unit_a_db()
        print('Cargamos precio_mayorista_a_db')
        self.cargar_precio_mayorista_a_db()
        print('Cargamos productos_a_db')
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
