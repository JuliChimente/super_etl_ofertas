import pandas as pd
from tkinter import *
from tkinter import messagebox
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación de Web Scraping")
        
        self.input_frame = Frame(self.root)
        self.input_frame.pack(pady=10)

        self.input_label = Label(self.input_frame, text="Lista de Productos:")
        self.input_label.grid(row=0, column=0)

        self.input_entry = Entry(self.input_frame, width=50)
        self.input_entry.grid(row=0, column=1)

        self.browser_frame = Frame(self.root)
        self.browser_frame.pack(pady=10)

        self.browser_label = Label(self.browser_frame, text="Elige el navegador que tengas instalado:")
        self.browser_label.pack()

        self.chrome_button = Button(self.browser_frame, text="Chrome", command=lambda: self.execute_scraping("Chrome"))
        self.chrome_button.pack(side=LEFT)

        self.edge_button = Button(self.browser_frame, text="Edge", command=lambda: self.execute_scraping("Edge"))
        self.edge_button.pack(side=LEFT)

        self.firefox_button = Button(self.browser_frame, text="Firefox", command=lambda: self.execute_scraping("Firefox"))
        self.firefox_button.pack(side=LEFT)

        self.result_frame = Frame(self.root)
        self.result_frame.pack()

        self.result_label = Label(self.result_frame, text="Resultados:")
        self.result_label.pack()

        self.table_frame = Frame(self.result_frame)
        self.table_frame.pack()

        self.table = Text(self.table_frame, width=80, height=20)
        self.table.pack()

        self.df1_button = Button(self.result_frame, text="Mostrar DF1", command=lambda: self.display_dataframe(df1))
        self.df1_button.pack(side=LEFT)

        self.df2_button = Button(self.result_frame, text="Mostrar DF2", command=lambda: self.display_dataframe(df2))
        self.df2_button.pack(side=LEFT)

        self.current_dataframe = None

    def super_mejores_precios(self, browser):
        lista_productos = self.input_entry.get().split(", ")
        
        ofertas_super = obtener_ofertas(lista_productos, browser)
        
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
        self.current_dataframe = menor_precio_x_supermercado

        self.update_table()

    def lista_mejores_precios(self, browser):
        lista_productos = self.input_entry.get().split(", ")
        
        ofertas_super = obtener_ofertas(lista_productos, browser)
        
        # Obtener el índice del producto más barato para cada producto único
        indices_menor_precio = ofertas_super.groupby(ofertas_super['nombre'].str.split().str[0])['precio'].idxmin()

        # Obtener el DataFrame con los productos más baratos
        productos_mas_baratos = ofertas_super.loc[indices_menor_precio]

        # Función lambda para formatear los valores como moneda
        formato_moneda = lambda x: f'${x:.2f}'

        # Aplicar la función lambda a la columna 'Precio'
        productos_mas_baratos['precio'] = productos_mas_baratos['precio'].map(formato_moneda)
        
        # Guardar el DataFrame seleccionado
        self.current_dataframe = productos_mas_baratos

        self.update_table()

    def clear_input(self):
        self.input_entry.delete(0, 'end')

    def display_dataframe(self, dataframe):
        self.current_dataframe = dataframe
        self.update_table()

    def update_table(self):
        if self.current_dataframe:
            self.table.delete(1.0, 'end')
            self.table.insert('end', f"{'Supermercado':<15}{'Nombre':<15}{'Precio':<10}{'Promo':<10}{'URL':<30}\n")
            self.table.insert('end', '-'*80 + '\n')
            for result in self.current_dataframe:
                self.table.insert('end', f"{result['supermercado']:<15}{result['nombre']:<15}{result['precio']:<10}{result['promo']:<10}{result['url']:<30}\n")
        else:
            self.table.delete(1.0, 'end')
            self.table.insert('end', "No hay datos para mostrar.\n")
        
def obtener_ofertas(lista_productos, browser):
    # URL del supermercados
    supermercados = ['https://www.vea.com.ar/','https://www.disco.com.ar/','https://www.jumbo.com.ar/','https://diaonline.supermercadosdia.com.ar/']
    
    lista_super_prod_baratos = pd.DataFrame(columns=['supermercado','nombre','precio','promo','url'])
    
    for lista in lista_productos:
        lista_productos = []  # Lista para almacenar los precios del supermercado actual
        for super in supermercados:
            # Configurar el driver de Selenium y cargar la página web

            if browser == "Chrome":
                options = ChromeOptions()
                options.add_argument("--start-minimized")
                driver = webdriver.Chrome(options=options)
            elif browser == "Firefox":
                options = FirefoxOptions()
                options.add_argument("--start-minimized")
                driver = webdriver.Firefox(options=options)
            elif browser == "Edge":
                options = EdgeOptions()
                options.add_argument("--start-minimized")
                driver = webdriver.Edge(options=options)
            else:
                raise ValueError("Navegador no soportado")
            
            lista.replace(" ","%20")
            
            driver.get(f'{super}{lista}{"?order=OrderByPriceASC"}')

            super = super.split('.')[1].upper()

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
            
            precio = precio.replace('.', '')
            
            precio = precio.replace(',', '.')
            
            precio = precio.replace('$', '')
            
            precio = float(precio)
            
            producto_dict = {
                'supermercado': super,
                'nombre': nombre,
                'precio': precio,
                'promo': promo,
                'url': url
            }

            # Agregar el diccionario a la lista
            lista_productos.append(producto_dict)

            # Lista de los productos mas baratos por supermercado
            productos_baratos_x_super = pd.DataFrame(lista_productos)
            
            lista_super_prod_baratos = pd.concat([lista_super_prod_baratos, productos_baratos_x_super], ignore_index=True)
        
    # Eliminar filas duplicadas basadas en todas las columnas del DataFrame
    lista_super_prod_baratos = lista_super_prod_baratos.drop_duplicates()
                
    return lista_super_prod_baratos

root = Tk()
app = Application(root)
root.mainloop()