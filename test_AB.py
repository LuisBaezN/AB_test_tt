import numpy as np
import pandas as pd

orders = pd.read_csv('datasets/orders_us.csv')
visits = pd.read_csv('datasets/visits_us.csv')

print(orders.head())
print(visits.head())

orders.info()
visits.info()

# Notamos que las columnas grupo y date se han cargado como un tipo objeto. Cambiamos las columnas group al tipo a categórico y las columnas date a tipo fecha.

orders['group'] = orders['group'].astype('category')
visits['group'] = visits['group'].astype('category')

orders['date'] = pd.to_datetime(orders['date'], format="%Y-%m-%d")
visits['date'] = pd.to_datetime(visits['date'], format="%Y-%m-%d")

# Verificamos

# Separamos los grupos de prueba

orders_A = orders[orders['group'] == 'A']
orders_B = orders[orders['group'] == 'B']

# Identificamos a los usuarios que estuvieron en ambos grupos

users_in_both = pd.concat(
    [
        orders_A[orders_A['visitorId'].isin(orders_B['visitorId'])]['visitorId'], 
        orders_B[orders_B['visitorId'].isin(orders_A['visitorId'])]['visitorId']
    ]
    ).drop_duplicates()

# Filtramos los grupos para eliminar a los usarios presentes en ambas pruebas

orders_A = orders_A[~orders_A['visitorId'].isin(users_in_both)]
orders_B = orders_B[~orders_B['visitorId'].isin(users_in_both)]