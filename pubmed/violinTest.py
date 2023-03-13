import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#%pylab inline

dataframe = pd.read_csv("/Users/simonray/Downloads/archive/gapminder_full.csv", error_bad_lines=False, encoding="ISO-8859-1")
print(dataframe.head())
print(dataframe.isnull().values.any())

#population = dataframe.population
#life_exp = dataframe.life_exp
#gdp_cap = dataframe.gdp_cap

sns.violinplot(x='continent', y='life_exp', data=dataframe)
plt.show()
