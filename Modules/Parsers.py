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
from collections import Counter
import re
def coincidence_parser(datos,column_name='Coincidencias_iniciales', verbose = True,kind = 'ruleId'):
    coincidencias = datos[column_name].values
    size =  coincidencias.shape[0] 
    
    #list for the dictionaries
    clist = []
    # counter for rules
    rules = Counter()

    for i, index in enumerate(datos.index):
        if i % 100 == 0 and verbose: print(i,end=' ')
       
        # extract coincidences from row i
        # split the rules, according to the data structure
        c = coincidencias[i]
        c = re.sub('Match\({','MatchXXXX({',c)
        l = c.split('MatchXXXX')
        
        # create a list with each dictionary obtained
        clist.clear()
        for k in range(1, len(l)):
            dictionary = l[k]
            try: 
                val = dict(eval(dictionary[1:-3]))
            except:
                val = dict(eval(dictionary[1:-2]))

            clist.append(val)
        
        # count the rules found  by type of rule
        rules.clear()
        for j in range(len(clist)):
            # Posibles: ruleId, ruleIssueType, category
            rules[clist[j][kind]] += 1

        # to the dataframe
        for key, value in rules.items():
            datos.at[index, key] = value
            
from collections import Counter

def spacy_column_parser(column_name, verbose=True):
    # start
    size =  datos.shape[0] 
    print('¡¡Empezando...!! Se procesaran ', size, ' registros de la columna ', column_name)
    
     # counter for rules
    rules = Counter()

    # working bucle
    for i, index in enumerate(datos.index):
        if i % 100 == 0 and verbose: print(i, end=' ')
       
        # read column value in this register (index)
        values = eval(datos.at[index, column_name])
        
        # extract the rules
        rules.clear()
        for value in values:
            rules[value] += 1
        
        # to the dataframe
        for key, value in rules.items():
            datos.at[index, key] = value 
          
    print('\n¡¡Hecho!!.... Se procesaron ', i+1, ' registros de la columna ', column_name)


def spacy_parser( column_names=['Upos',  'Dep', 'Ner_type'], verbose = True):
    for column_name in column_names:
        spacy_column_parser(column_name, verbose=True)