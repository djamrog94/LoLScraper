import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


df = pd.read_excel('900_df.xlsx')

X = df[['cent_chg_1', 'cent_chg_3', 'damage', 'dragons', 'kills', 'vision']]
y = df['result']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)


lrg = LogisticRegression(solver='liblinear')
lrg.fit(X_test, y_test)
print(lrg.score(X_test,y_test))
