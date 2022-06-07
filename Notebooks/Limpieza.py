def Limpiar_Textos(textos,stopwords=True,colname='Texto_limpio'):
    import pandas as pd
    import re
    import datetime
    # Importar stopwords con nltk
    from nltk.corpus import stopwords
    import es_core_news_sm
    
    #==========================Input Datos==========================
    if isinstance(textos, pd.DataFrame):
        datos = textos
    elif isinstance(textos, pd.Series):
        datos = pd.DataFrame(textos,columns=[textos.name])
    else:
        datos = pd.DataFrame([])
        datos['RESPUESTA'] = textos
        #Transformar todo a string
        datos['RESPUESTA'] = datos['RESPUESTA'].astype(str)
    textos_col_name = datos.columns.values[0]
    #print(textos_col_name)
    #==========================Limpieza General==========================
    print('Limpiando Texto...',end='    ')
    t0 = datetime.datetime.now()
    # Poner en minúsculas
    datos.loc[:,colname] = datos.loc[:,textos_col_name].str.lower()
    # Quitar Puntuaciones, etc...
    datos.loc[:,colname] = datos.loc[:,colname].str.replace('[^\w\s]',' ',regex=True)
    # Quitar dígitos (O será mejor transformarlos a texto??)
    datos.loc[:,colname] = datos.loc[:,colname].replace('\d+','',regex=True)
    # Quitar espacios extra
    datos.loc[:,colname] = datos.loc[:,colname].replace('\s\s+',' ',regex=True)
    datos.loc[:,colname] = datos.loc[:,colname].str.strip()
    t1 = datetime.datetime.now()
    print('Tiempo de Procesamiento: {}'.format(t1 - t0))
    
    #==========================Stopwords==========================
    #print('Cargando Stopwords...',end=' ')
    t0 = datetime.datetime.now()
    # Número de stopwords en nltk
    stop_nltk = stopwords.words('spanish')
    # Número de stopwords en spacy
    nlp = es_core_news_sm.load()
    stop_spacy = nlp.Defaults.stop_words
    # Sacar lo mejor de todas las librerías (sin duplicados)
    stop_todas = list(stop_spacy.union(set(stop_nltk)))
    print('Quitando Stopwords...',end=' ')
    # Quitar stopwords
    datos[f'{colname}_sin_stopwords'] = datos[colname].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_todas)]))
    t1 = datetime.datetime.now()
    print('Tiempo de Procesamiento: {}'.format(t1 - t0))
    return datos