#pilote_dictionary.py

#imports
import streamlit as st
import pickle
from greek_accentuation.characters import *
import pandas as pd
import ast
import io

#to upload the pkl in the cache
@st.cache_data(ttl=1200)
def load_data_pickle(file_path):
	with open(file_path, "rb") as fp:
		pickle_data = pickle.load(fp)
	return pickle_data


#rep = st.sidebar.selectbox('choose a text representation',['lemmas','diplomatics','normalised'])
rep = 'diplomatics'

if rep == 'lemmas':
	st.warning('in building, features may not work')
	b = load_data_pickle("data/les_lemmes.pkl")
elif rep == 'diplomatics':
	b = load_data_pickle("data/les_diplos.pkl")
	abbrev = st.sidebar.checkbox('abbreviations only',True)
	if abbrev:
		b = [el for el in b if '(' in el[0] and ')' in el[0]]
else:
	st.warning('in building, features may not work')
	b = load_data_pickle("data/les_normaux.pkl")


repared = [list(el) for el in b]

if rep != 'diplomatics':
	remove_accents = st.sidebar.checkbox('remove accents?',False)
else:
	remove_accents = False
if remove_accents:
	new_repared = []
	for el in repared:
		#temp = []
		temp_str = [base(t) for t in el[0]]
		temp_str = ''.join(temp_str)

		new_repared.append([temp_str,el[1]])
		#.append(temp)
	repared = new_repared
	#st.write(type(temp_str))
	#st.write(temp_str)


#b = b[:20]



letter = st.sidebar.text_input('choose a letter (max. 3)','!')
#for len(letter)
#if len(letter)!=1:
#if el[0][0]==letter:

grk_alpha = '!αβγδεζηθικλμνξοπρcτυφχψω'

#letter = st.sidebar.selectbox('choose a letter',[el for el in grk_alpha])
inverse = st.sidebar.checkbox('inverse dictionary',False)


display = []
#st.write(repared[:3])

if rep != 'diplomatics':
	lunar_sigma = st.sidebar.checkbox('lunar sigma?', False)
else:
	lunar_sigma = False

for el in repared:
	if lunar_sigma:
		el[0] = el[0].replace('σ','c').replace('ς','c')
	if letter == '!':
		display = repared
	
	#t.write(type(el[0]))
	#st.write(el[0])
	else:
		try:
			if not inverse:
				if el[0][0]==letter[0]:
					if len(letter) == 1:
						display.append(el)
					else:
						if el[0][1]==letter[1]:
							if len(letter) == 2:
								display.append(el)
							else:
								if el[0][2]==letter[2]:
									display.append(el)
					#st.write(el)
			else:
				if el[0][-1]==letter[-1]:
					if len(letter) == 1:

						display.append(el)
					else:
						if el[0][-2]==letter[-2]:
							if len(letter) == 1:
								display.append(el)
							else:
								if el[0][-3]==letter[-3]:
									display.append(el)



					#st.write(el)
		except:
			pass

by_number = st.sidebar.checkbox('sort by number of attestations',True)

if by_number:
	display = sorted(display, 
    key=lambda x: x[1]
)
	display = display[::-1]
	#.reversed()

last_include = st.sidebar.selectbox('include: ',['all','words replaced by symbols only','words partially abbreviated only','words containing more than one abbreviation only'])

if last_include == 'words replaced by symbols only':
	display = [el for el in display if el[0][0]=='(' and el[0][-1]==')']
elif last_include == 'words partially abbreviated only':
	display = [el for el in display if not el[0][0]=='(' and el[0][-1]==')']
elif last_include == 'words containing more than one abbreviation only':
	display = [el for el in display if el[0].count('(')>1]


#if 'words replaced by symbols' not in last_include:
#	display = [el for el in display if ]

limit_results = st.sidebar.text_input('Top X results only','50')

if limit_results !='':
	display = display[:int(limit_results)]

#display = display[:100]
#
if 'dfw2' not in st.session_state:
	dfs = []
	for i in range(0,6):
		temp_df = pd.read_parquet(f'data/chunk{i}.parquet')
		dfs.append(temp_df)
		
	dfw =pd.concat(dfs)
	st.write(dfw.head())
	dfw = dfw.drop_duplicates(subset=['tmid'])
	dipll = list(ast.literal_eval(el) for el in dfw.diplomatic)

	dfw['dip2'] = dipll
	st.session_state['dfw'] = dfw
	dfw2 = dfw[['tmid','period_min','genre']]
	st.session_state['dfw2'] = dfw2


with st.expander('show TmWords'):
	st.write(st.session_state['dfw2'].head())

#
#


if 'refList' not in st.session_state:
	explodf = st.session_state['dfw'][['tmid','dip2']]
	explodf2 = explodf.explode('dip2').reset_index(drop=True)
	explodf3 = explodf2.explode('dip2').reset_index(drop=True)
	refList = explodf3.groupby(by='dip2').agg({'tmid':lambda x:list(x)})
	st.session_state['refList']=refList
#let user choose whether 2 attestations in 1 text are to be counted as one or 2


st.header(f'{len(display)} hits: ')
for el in display:
	st.write(el)
	letsay = st.session_state['refList'].tmid[el[0]]
	oneWord = st.session_state['dfw2'][st.session_state['dfw2'].tmid.isin(letsay)]
	col1,col2,col3 = st.columns(3)
	with col1:
		st.warning('in building')
		#st.write(oneWord.genre.value_counts(normalize=True)[:5])
	with col2:
		st.write(oneWord.genre.value_counts(normalize=True)[:5])
	with col3:
		st.write(oneWord.period_min.value_counts(normalize=True)[:5])
	#st.write(oneWord.place.value_counts()[:5])
#st.write(display)

st.write('CREDITS: raw data from A.Keersmaekers https://github.com/alekkeersmaekers/duke-nlp, snippets for online version by André Walsøe, everything else from Audric-Charles Wannaz, March 2023')

