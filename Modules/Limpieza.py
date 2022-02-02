# Copyright 2022 Aprendizaje Profundo, All rights reserved.
#
# Licensed under the MIT License;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Developed by Alvaro Mauricio Montenegro Reyes and Daniel Mauricio Montenegro Reyes
# ==================================================================================
def Limpiar_Textos(textos,idioma='Spanish',Stopwords=True):
    #==========================Librerías==========================
    import pandas as pd
    import datetime
    import num2words
    import re
    #==========================Input Datos==========================
    # Si es dataframe, no cambiar nada
    if isinstance(textos, pd.DataFrame):
        datos = textos.copy()
    # Si es Serie, formar dataframe
    elif isinstance(textos, pd.Series):
        datos = pd.DataFrame(textos,columns=[textos.name])
    # Si no es nada (lista de textos), generar un dataframe
    else:
        datos = pd.DataFrame([])
        datos['Texto'] = textos
        #Transformar todo a string
        datos['Texto'] = datos['Texto'].astype(str)
    
    # Nombres de las columnas
    textos_col_name               = datos.columns.values[0]
    textos_col_name_limpio        = f'{textos_col_name}_limpio'
    textos_col_name_limpio_no_stp = f'{textos_col_name}_sin_stopwords'
    #print(textos_col_name)
    #==========================Limpieza General==========================
    print('Limpiando Texto...',end='    ')
    t0 = datetime.datetime.now()
    # Poner en minúsculas
    datos[textos_col_name_limpio] = datos[textos_col_name].str.lower()
    # Quitar Puntuaciones, etc...
    #datos[textos_col_name_limpio] = datos[textos_col_name_limpio].str.replace('[^\w\s]',' ',regex=True)
    ###### Se dejan puntuaciones para analizar sentencias por separado. ###########
    datos[textos_col_name_limpio] = datos[textos_col_name_limpio].str.replace('[^\w\s\@\\.]',' ',regex=True)
    # Quitar dígitos (O será mejor transformarlos a texto??)
    #datos[textos_col_name_limpio] = datos[textos_col_name_limpio].replace('\d+','',regex=True)
    ###### Se transforman digitos a texto para ver cómo actúa el modelo. ###########
    datos[textos_col_name_limpio] = datos[textos_col_name_limpio].apply(lambda x: re.sub('\d+',lambda y: '_'+num2words.num2words(int(y.group(0))),x))
    # Quitar espacios extra
    datos[textos_col_name_limpio] = datos[textos_col_name_limpio].replace('\s\s+',' ',regex=True)
    # Quitar espacio al inicio y al final
    datos[textos_col_name_limpio] = datos[textos_col_name_limpio].str.strip()
    t1 = datetime.datetime.now()
    print('Tiempo de Procesamiento: {}'.format(t1 - t0))
    
    #=================================Stopwords=================================
    if Stopwords:
        
        from Limpieza import get_models_from_db,check_install_model_spacy,get_model_spacy
        
        langs = get_models_from_db(verbose=False)
        chosen_model = check_install_model_spacy(langs,lang=idioma,kind='sm')
        nlp = get_model_spacy(chosen_model[0])
        
        # Importar stopwords con nltk
        from nltk.corpus import stopwords
        
        # Stopwords en nltk
        stop_nltk = stopwords.words(idioma)
        # Stopwords en spacy
        stop_spacy = nlp.Defaults.stop_words
        
        # Sacar lo mejor de todas las librerías (sin duplicados) ENGLISH
        if idioma=='English':
            from gensim.parsing.preprocessing import STOPWORDS
            stop_gensim = set(STOPWORDS)
            stop_todas = list(stop_spacy.union(set(stop_nltk).union(stop_gensim)))
        else:
            # Sacar lo mejor de todas las librerías (sin duplicados)
            stop_todas = list(stop_spacy.union(set(stop_nltk)))
            
        #print(stop_todas)
        #=================================Procesamiento=================================
        t0 = datetime.datetime.now()
        # Quitar stopwords
        print('Quitando Stopwords...',end=' ')
        datos[textos_col_name_limpio_no_stp] = datos[textos_col_name_limpio].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_todas)]))
        t1 = datetime.datetime.now()
        print('Tiempo de Procesamiento: {}'.format(t1 - t0))
    return datos

def get_models_from_db(verbose=False):
    #====================== LIBRARIES NEEDED ========================
    import requests
    import re
    import spacy
    from bs4 import BeautifulSoup
    
    #====================== BASE URLS ========================
    url_root = 'https://spacy.io'
    where_models = '/usage/models'
    url_all_models = url_root + where_models
    
    #====================== GET MODELS URLS INFO ========================
    # get connection to the frontend table
    res = requests.get(url_all_models)
    # get content from all website
    html_page = res.content
    # parse website
    soup = BeautifulSoup(html_page, 'html.parser')
    # take where models are (table)
    texto = soup.find_all('table')
    # filter where models are (chinese is duplicated at the end)
    models_url = re.findall('\/models\/\w\w',str(texto))[:-1]
    
    if verbose:
        #show models found
        print(f'Models Found: {len(models_url)}\n')
        print(models_url)
    
    # Obtener las urls de los modelos
    url_models = [url_root + model_url for model_url in models_url]
    #====================== GET LANGUAGE INFO ========================
    # Get all places where languages (are in option value xx)
    texto = soup.find_all('option',{'value':re.compile(r'\b\w\w\b')})
    # Filter all Languages (includes spaces and - delimiter)
    models_lang = re.findall('\w\w\"\>([A-Z]\w+[\s\-]?\w+)\<',str(texto))
    
    if verbose:
        #show languages found
        print(f'\nLanguages Found: {len(models_lang)}\n')
        print(models_lang)
    
    # Crear Diccionario {lenguaje:url}
    langs = dict(zip(models_lang, url_models))
    
    return langs

def check_install_model_spacy(langs,lang='Spanish',kind='sm'):
    #====================== LIBRARIES NEEDED ========================
    import requests
    import re
    import html2text
    import spacy
    from bs4 import BeautifulSoup
    #====================== GET SELECTED LANGUAGE MODEL ========================
    # get connection to the specific language website
    res = requests.get(langs[lang])
    # get content from website
    html_page = res.content
    # parse website
    soup = BeautifulSoup(html_page, 'html.parser')
    # find where the models definition are 
    texto = soup.find_all('span')
    # get text from raw html
    texto_limpio = html2text.html2text(''.join(str(texto)))
    # Type of models (They are not Standard)
    model_type = re.compile('\w*_core_*\w+|\w*_dep_*\w+|\w*_ent_*\w+|\w*_sent_*\w+')
    # Filter exact names of models
    models = re.findall(model_type,texto_limpio)
    
    # Get model info
    print(f'\nAvailable Models for {lang}:\n')
    for model in models:
        print(model)
    
    # Look for installed models to avoid double download
    installed_models = sorted(list(spacy.info()['pipelines'].keys()))
    
    # Get chosen model
    from itertools import chain
    chosen_model = list(chain.from_iterable([re.findall('.*'+kind,model) for model in models]))
    
    print(f'\nLooking if Model {chosen_model} in {lang} Already Installed...\n')
    
    # Look for chosen models
    for model in chosen_model:
        # Check if they are installed
        if model in installed_models:
            print(f'- {model} already installed.')
        else:
            # Python Loves Bash (PLB)
            import os
            os.system(f"bash -c 'python -m spacy download {model} -q'")
            
    return chosen_model

def get_model_spacy(chosen_model):
    import spacy
    nlp = spacy.load(chosen_model)
    print(f'\nModel {chosen_model} loaded.\n')
    return nlp