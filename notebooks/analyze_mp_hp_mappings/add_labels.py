import pandas as pd
import os

os.system('wget https://kg-hub.berkeleybop.io/kg-ontoml/20220304/KG-OntoML.tar.gz')
os.system('tar -xvzf KG-OntoML.tar.gz')
os.system('cut -f 1,3 merged-kg_nodes.tsv | grep -E -p "MP:|HP:" > labels.tsv')

up = pd.read_csv('unmapped_prediction', sep=" ", index_col=False, header=None)
up = up.rename(columns={0: 'HP', 1: 'MP'})

labels = pd.read_csv('labels.tsv', sep="\t", index_col=False, header=None)
labels = labels.rename(columns={0: 'node', 1: 'name'})

m = pd.merge(up, labels, left_on='HP', right_on='node', how='left')
m = pd.merge(m, labels, left_on='MP', right_on='node', how='left')

m = m.drop(["HP", "MP"], axis=1)
m = m.rename(columns={'node_x': 'HP', 'name_x': 'HP_name', 'node_y': 'MP', 'name_y': 'MP_name'})
m.to_csv("unmapped_prediction_with_labels.tsv", sep="\t", index=None)

def sorted_mp_hp(row):
   row_items =  [row['subject'], row['object']]
   row_items.sort()
   return "".join(row_items)

edges = pd.read_csv('merged-kg_edges.tsv', sep="\t", index_col=False, header=None)
edges['hpmp'] = edges.apply(lambda row: sorted_mp_hp(row), axis=1)
edges = edges[edges.hpmp.str.contains("HP") & edges.hpmp.str.contains("MP")]  # existing HP MP edges (HP first, MP second)

m['hpmp'] = m['HP'] + m['MP']

df = pd.merge(m, edges, how='outer', on=['hpmp'], indicator = True)
df = df.loc[df['_merge']=='left_only']

m.to_csv("unmapped_prediction_with_labels_no_existing_edges.tsv", sep="\t", index=None)
