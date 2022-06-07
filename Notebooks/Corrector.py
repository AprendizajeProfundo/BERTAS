def Cargar_Corrector(idioma):
    import language_tool_python
    # Para evitar costo computacional, cargar el corrector sólo una vez
    tool = language_tool_python.LanguageTool(idioma)
    return tool

def Corregir_Textos(textos,tool):
    
    import language_tool_python
    import pandas as pd
    import datetime
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
    #==========================Corrector Ortográfico==========================
    datos = pd.DataFrame([])
    datos[textos_col_name] = textos.copy()
    t0 = datetime.datetime.now()
    print('Hallando Coincidencias...',end =' ')
    datos['Coincidencias'] = datos[textos_col_name].apply(lambda txt: tool.check(txt))
    print('Corrigiendo...',end =' ')
    datos['Corregido'] = datos.apply(lambda l: language_tool_python.utils.correct(l[textos_col_name], l['Coincidencias']), axis=1)
    datos['Correcciones'] = datos.apply(lambda l: len(l['Coincidencias']), axis=1)
    t1 = datetime.datetime.now()
    print('Tiempo de Procesamiento: {}'.format(t1 - t0))
    
    return datos