def ice_rice_score(data: object, names: list = ['reach', 'impact', 'confidence', 'effort', 'name'], rice: bool = False) -> float:
    '''
    Return the ICE score and the RICE score if indicated. The data structure must be a pandas structure.
    ICE score = (impact * confidence) / effort
    RICE score = (reach * impact * confidence) / effort
    '''
    ice_score = (data[names[1]] * data[names[2]]) / data[names[3]]
    ice_score.name = 'ice_score'
    ice_score = pd.concat([data[names[-1]], ice_score], axis=1)
    ice_score = ice_score.sort_values(by='ice_score', ascending=False)

    if rice:
        rice_score = (data[names[0]] * data[names[1]] * data[names[2]]) / data[names[3]]
        rice_score.name = 'rice_score'
        rice_score = pd.concat([data[names[-1]], rice_score], axis=1)
        rice_score = rice_score.sort_values(by='rice_score', ascending=False)
    else:
        rice_score = pd.Series(0, index=np.arange(len(data)))
        rice_score.name = 'rice_score'

    return [ice_score, rice_score]

if __name__ == '__main__':
    import pandas as pd
    import numpy as np

    # Al inspeccionar los datos obserbamos que los datos están delimitados por punto y coma.
    hyp = pd.read_csv('datasets/hypotheses_us.csv', delimiter=';')

    # Visualizemos los datos
    print(hyp)
    hyp.info()

    # Calculamos el score ICE y RICE
    results = ice_rice_score(hyp, ['Reach', 'Impact', 'Confidence', 'Effort', 'Hypothesis'], True)

    # Mostramos el ICE score
    print(results[0])
    # Las tres hipótesis con mayor prioridad son la novena, la primera y la octava

    # Comparamos con el RICE score
    print(results[1])

    '''
    Notamos que la prioridad de las hipótesis ha cambiado, la secuencia ahora es: la octava, la tercera y la primera. Además, una de las hipótesis
    que no se encontraba entre las primeras tres, subió al segundo lugar.
    
    Veamos la columna de alcance de las hipótesis.
    '''
    print(hyp['Reach'])
    '''
    Observe que la octava hipótesis es la que tiene el mayor alcance, aunado al alto puntaje de las métricas anteriores, se desplazó al primer lugar.
    La tercera hipótesis también tiene un muy alto alcance, por lo que su subida en el ranking es razonable.
    '''

    