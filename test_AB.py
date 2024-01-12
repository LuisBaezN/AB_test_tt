import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st

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

visits_A = visits[visits['group'] == 'A']
visits_B = visits[visits['group'] == 'B']

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

# Calculamos el número de pedidos y las ganancias por fecha
cumulative_A = orders_A.groupby('date', as_index=False).agg({'transactionId':'nunique', 'visitorId':'nunique', 'revenue':'sum'})
cumulative_B = orders_B.groupby('date', as_index=False).agg({'transactionId':'nunique', 'visitorId':'nunique', 'revenue':'sum'})

visits_A = visits[visits['group'] == 'A']
visits_B = visits[visits['group'] == 'B']

cumulative_A = cumulative_A.merge(visits_A[['date', 'visits']], how='left', on='date')
cumulative_B = cumulative_B.merge(visits_B[['date', 'visits']], how='left', on='date')

cumulative_A.columns = ['date', 'orders', 'buyers', 'revenue', 'visits']
cumulative_B.columns = ['date', 'orders', 'buyers', 'revenue', 'visits']

# Graficamos el ingreso acumulado
plt.plot(cumulative_A['date'], cumulative_A['revenue'], label='A')
plt.plot(cumulative_B['date'], cumulative_B['revenue'], label='B')
plt.xticks(rotation='vertical')
plt.title('Revenue')
plt.legend()
plt.grid()
plt.show()
'''
Observamos que no hay una tendencia positiva en los ingresos y que dentro del grupo B, existe un ingreso muy grande el 19 de agosto.

Graficamos el tamaño del pedido promedio acumulado.
'''

plt.plot(cumulative_A['date'], cumulative_A['revenue']/cumulative_A['orders'], label='A')
plt.plot(cumulative_B['date'], cumulative_B['revenue']/cumulative_B['orders'], label='B')
plt.xticks(rotation='vertical')
plt.title('Average orders')
plt.legend()
plt.grid()
plt.show()
'''
Vemos que el comportamiento en ambos grupos es similar, por lo que número de órdenes por día puede ser homogéneo. También notamos que hay algunos pedidos anómalos en cada grupo.

Observemos la diferencia relativa entre el grupo B y el A.
'''

plt.plot(cumulative_A['date'], (cumulative_B['revenue']/cumulative_B['orders']) / (cumulative_A['revenue']/cumulative_A['orders']) - 1)
plt.axhline(y=0, color='black', linestyle='--')
plt.xticks(rotation='vertical')
plt.title('Relative difference')
plt.grid()
plt.show()
'''
Sin contar los valores atípicos del grupo B, notamos que la diferencia no existe. Más adelante probaremos si esta nula diferencia es estadísticamente significativa.

Calculemos la conversión en compras de cada grupo.
'''

cumulative_A['conversion'] = cumulative_A['orders']/cumulative_A['visits']
cumulative_B['conversion'] = cumulative_B['orders']/cumulative_B['visits']

# Grafiquemos la conversión.
plt.plot(cumulative_A['date'], cumulative_A['conversion'], label='A')
plt.plot(cumulative_B['date'], cumulative_B['conversion'], label='B')
plt.xticks(rotation='vertical')
plt.title('Revenue')
plt.legend()
plt.grid()
plt.show()

plt.plot(cumulative_A['date'], cumulative_B['conversion'] / cumulative_A['conversion'] - 1)
plt.axhline(y=0, color='black', linestyle='--')
plt.xticks(rotation='vertical')
plt.title('Relative difference')
plt.grid()
plt.show()
'''
En ambos grupos se presenta una conversión que fluctúa al rededor del 3%. Ambos grupos presentan un desarrollo similar. Al inspeccionar la diferencia relativa observamos que el 
grupo B es ligeramente superior, pero sin una estabilización evidente.

Como lo vimos en estas gráficas, hay valores atípicos, tanto en las ganancias como en el número de compras. Procedemos entonces, a visualizar estos datos anómalos. 

Comenzamos con graficar el número de pedidos por cliente.
'''
users_A = orders_A.groupby('visitorId', as_index=False).agg({'transactionId':'nunique', 'revenue':'sum'})
users_B = orders_B.groupby('visitorId', as_index=False).agg({'transactionId':'nunique', 'revenue':'sum'})

users_A.columns = ['visitorId', 'orders', 'revenue']
users_B.columns = ['visitorId', 'orders', 'revenue']

x = users_A.index

plt.scatter(x + 1, users_A['orders'])
plt.title('A group')
plt.xlabel('Client')
plt.ylabel('Orders')
plt.show()

x = users_B.index

plt.scatter(x + 1, users_B['orders'])
plt.title('B group')
plt.xlabel('Client')
plt.ylabel('Orders')
plt.show()
'''
El número depedidos por cliente es usualmente 1. En ambos grupos tenemos clientes que han hecho 2 o 3 pedidos. Veamos qué porcentaje de usuarios presentan este comportamiento.
'''

def percentile_desc(data: object, percentiles: list = [95, 99]) -> None:
    results = np.percentile(data, percentiles)
    for i in range(len(percentiles)):
        print(f'> {100 - percentiles[i]}% of the data is greater than: {results[i]:.2f}')

print('> Group A:')
percentile_desc(users_A['orders'], [96, 97, 99])

print('> Group B:')
percentile_desc(users_B['orders'], [96, 97, 99])

'''
Considerando que la gran mayoría de los clientes solo hicieron una compra al mes, consideraremos anomalías a aquellos usuarios que realizaron 3 compras.

Veamos la dispersión de las ganancias por usuario.
'''

x = users_A.index

plt.scatter(x + 1, users_A['revenue'])
plt.title('A group')
plt.xlabel('Client')
plt.ylabel('Revenue')
plt.show()

x = users_B.index

plt.scatter(x + 1, users_B['revenue'])
plt.title('B group')
plt.xlabel('Client')
plt.ylabel('Revenue')
plt.show()
'''
Observamos que la mayoría de clientes del grupo A gasta menos de 400 por pedido. Lo verificaremos despúes con el análisis de percentiles. En el grupo B es
difícil distinguir con esta gráfica el gasto típico de un usuario dado que hay clientes con gastos de alrededor de 2000 por pedido.

Veamos el porcentaje de los clientes.
'''

print('> Group A:')
percentile_desc(orders_A['revenue'], [95, 97, 99])

print('> Group B:')
percentile_desc(orders_B['revenue'], [95, 97, 99])

'''
Podemos ver que en ambos casos, el 97% de los datos conserva una proporción similar. Ya que tenemos menos usuarios en el grupo A, estableceremos como usuarios anómalos
a aquellos usuarios que hayan gastado más de 670.

Veamos cuál es la significancia estadísitica en la conversión de los datos.
'''

traffic_A = pd.concat([users_A['orders'], pd.Series(0, index=np.arange(visits_A['visits'].sum() - len(users_A)))])
traffic_B = pd.concat([users_B['orders'], pd.Series(0, index=np.arange(visits_B['visits'].sum() - len(users_B)))])

print('> p-value: {0:.5f}'.format(st.mannwhitneyu(traffic_A, traffic_B)[1]))
print('> Relative difference: {0:.5f}'.format(traffic_B.mean()/traffic_A.mean() - 1))
'''
El p-value resultante es menor al 5%, sin embargo, no está muy alejado, por lo que, dado los datos de los usuarios anómalos, nos produce un cierto grado de incertidumbre
a nuestro resultado, aun cuando la diferencia relativa es de aproximadamente un 16%.

Veamos la significancia estadística en el tamaño promedio de pedido.
'''

print(f'> p-value: {st.mannwhitneyu(users_A['revenue'], users_B['revenue'])[1]:.5f}')
'''
De nueva cuenta, la incertidumbre del resultado está presente ya que el p-value está pegado al margen de significacia, 
pero en esta ocasión, favorece la aceptación de la hipótesis nula.

Volvamos a realizar las pruebas, pero en esta ocasión, eliminaremos a los usuarios anómalos.
'''

max_orders = 2
max_revenue = 670.5

users_A = users_A[(users_A['orders'] <= max_orders) & (users_A['revenue'] <= max_revenue)]
users_B = users_B[(users_B['orders'] <= max_orders) & (users_B['revenue'] <= max_revenue)]

traffic_A = pd.concat([users_A['orders'], pd.Series(0, index=np.arange(visits_A['visits'].sum() - len(users_A)))])
traffic_B = pd.concat([users_B['orders'], pd.Series(0, index=np.arange(visits_B['visits'].sum() - len(users_B)))])

print('> p-value: {0:.5f}'.format(st.mannwhitneyu(traffic_A, traffic_B)[1]))
print('> Relative difference: {0:.5f}'.format(traffic_B.mean()/traffic_A.mean() - 1))
'''
Ahora el p-value es menor al 1%, por lo que nuestro resultado previo no estaba del todo mal. También podemos notar que la diferencia
relativa aumentó un 4%.

Pasemos a la diferencia estadísitica del tamaño promedio de pedido.
'''

print(f'> p-value: {st.mannwhitneyu(users_A['revenue'], users_B['revenue'])[1]:.5f}')
'''
Nuestro p-value no cambió mucho, por lo que la hipótesis no es rechazada.
'''