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
        datos['Texto'] = textos
        #Transformar todo a string
        datos['Texto'] = datos['Texto'].astype(str)
        
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
    print('Tiempo de Procesamiento: {}'.format(t1 - t0),end=' ')
    print('Correcciones: {}'.format(datos['Correcciones'].sum()))
    return datos