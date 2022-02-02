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
def Spacy_Extractor(datos,idioma='Spanish',col='Corregido',kind='lg'):
    
    from Limpieza import get_models_from_db,check_install_model_spacy,get_model_spacy
    import spacy
    import datetime
    from itertools import chain
    
    
    tokens   = []
    lemma    = []
    upos     = []
    tag      = [] # Por alguna razón dan los mismos resultados, no hay detalles del POS...
    dep      = []
    ner_text = []
    ner_type = []
    sents    = []

    # stop_words.update(punctuation) # remove it if you need punctuation 
    
    #=====================Cargar Modelo Específico==========================
    # Debería sólo cargarse una vez para evitar sobrecargar la memoria (Clases)
    langs = get_models_from_db(verbose=False)
    chosen_model = check_install_model_spacy(langs,lang=idioma,kind=kind)
    nlp = get_model_spacy(chosen_model[0])
    
    t0 = datetime.datetime.now()

    # suppress numpy warnings
    #np.warnings.filterwarnings('ignore')

    # batch_size=100 is approx 7.5 gb of RAM
    # batch_size=200 is approx 8.3 gb of RAM
    for essay in nlp.pipe(datos[col]):
            # is_parsed is deprecated
        if essay.has_annotation("DEP"):
            
            tokens.append([[token.text for token in sent] for sent in essay.sents])
            
            lemma.append([[n.lemma_ for n in sent] for sent in essay.sents])
            # UPOS
            upos.append([[n.pos_ for n in sent] for sent in essay.sents])
            # TAGS
            tag.append([[n.tag_ for n in sent] for sent in essay.sents])
            # Dep
            dep.append([[n.dep_ for n in sent] for sent in essay.sents])
            # NER texto
            ner_text.append([[n.text for n in sent.ents] for sent in essay.sents])
            # NER typo
            ner_type.append([[n.label_ for n in sent.ents] for sent in essay.sents])
            # Frases
            sents.append([sent.text.strip() for sent in essay.sents])

        else:
            # We want to make sure that the lists of parsed results have the
            # same number of entries of the original Dataframe, so add some blanks in case the parse fails
            tokens.append(None)
            lemma.append(None)
            upos.append(None)
            tag.append(None)
            dep.append(None)
            ner_text.append(None)
            ner_type.append(None)
            sents.append(None)
    
    datos['Sent']          = sents
    datos['Sent_tokens']   = tokens
    datos['Sent_lemmas']   = lemma
    datos['Sent_upos']     = upos
    datos['Sent_tag']      = tag
    datos['Sent_dep']      = dep
    datos['Sent_ner_text'] = ner_text
    datos['Sent_ner_type'] = ner_type


    t1 = datetime.datetime.now()
    print('Tiempo de Procesamiento: {}'.format(t1 - t0))
    
    features = datos[['Sent_upos','Sent_dep','Sent_ner_type','Sent_tag']].apply(lambda x: list(chain.from_iterable(x)))
    columns = features.columns

    Upos_l = []
    Dep_l  = []
    Ner_l  = []
    Tag_l  = []

    for index in features.index:
        
        # UPOS RULES
        upos = features.at[index, columns[0]]
        for upo in upos:
            if upo not in Upos_l:
                Upos_l.append(upo)
        
        # DEP RULES
        deps = features.at[index, columns[1]]
        for dep in deps:
            if dep not in Dep_l:
                Dep_l.append(dep)
        
        # NER RULES
        ners = features.at[index, columns[2]]
        for ner in ners:
            if ner not in Ner_l:
                Ner_l.append(ner)
                
        # TAG RULES
        tags = features.at[index, columns[3]]
        for tag in tags:
            if tag not in Tag_l:
                Tag_l.append(tag)
    
    return datos,Upos_l,Dep_l,Ner_l, Tag_l