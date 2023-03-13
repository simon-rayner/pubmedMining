import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

lAllIFs = []
dfSummary = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/entrez_searches/disease_list_summary.tsv",
                        sep="\t")
#df_tips['sex'].value_counts()
dfSummary.columns
#dfSummary.set_index('disease', inplace=True)

for indexD, thisDisease in dfSummary.iterrows():
    theseIFs = thisDisease['IFs'].split("|")
    for ifs in theseIFs:
        lAllIFs.append({'disease': thisDisease['disease'], 'IF': float(ifs)})
plt.figure(figsize=(6,18))
dfAllIFs = pd.DataFrame(lAllIFs).head(50000)
df = sns.load_dataset('iris')
sns.set(style="darkgrid")
dfAllIFs['mean']=dfAllIFs.groupby('disease').IF.transform('mean')
dfAllSort=dfAllIFs.sort_values(by=['mean'], ascending=False)

sns.violinplot(y='disease', x='IF', data=dfAllSort,fontsize=12, linewidth=0.5)


grouped=dfAllIFs.groupby(by=["disease"])
df2 = pd.DataFrame({col:vals['IF'] for col,vals in grouped})
plt.xticks(fontsize=12)
plt.xlabel("IF", labelpad=14, fontsize=15)
plt.ylabel("disease", labelpad=14, fontsize=15)
plt.savefig('/Users/simonray/DropboxUiO/dropData/text_mining/plots/violin_IFs_vs_disease.TIFF',dpi=600)
plt.show()

#dfAllIFs.groupby(by=["disease"])["IF"].mean().sort_values(ascending=False, inplace=True).index
meds = df2.median()
df2=pd.sort_values(by=meds.index, ascending=False, inplace=True)
#df2 = df2[meds.index]
#sns.violinplot(y=dfAllIFs["disease"], x=dfAllIFs["IF"].astype(float), fontsize=2)
sns.set(font_scale=0.1)
sns.violinplot(y='disease', x='IF', data=dfAllIFs,  order=meds, fontsize=12, linewidth=0.5)
#sns.violinplot(y='disease', x='IF', data=dfAllIFs, fontsize=12)
plt.xticks(fontsize=12)
plt.xlabel("IF", labelpad=14, fontsize=15)
plt.ylabel("disease", labelpad=14, fontsize=15)
plt.savefig('/Users/simonray/DropboxUiO/dropData/text_mining/plots/violin_IFs_vs_disease.TIFF',dpi=600)
plt.show()
