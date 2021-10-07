'''
test_dates = ['2021-04-16']

scaler = StandardScaler()

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('voting', VotingRegressor(
        [
            ('gradient_boosting', GradientBoostingRegressor()),
        ],
        n_jobs=-1,
    )),
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
preds = []
for yp, yt in zip(y_pred, y_test):
    preds.append((yp, yt))

top = sorted(preds, key=lambda x: x[0], reverse=True)[:10]
pprint(top)

corr = np.corrcoef(y_test, y_pred)[0, 1]
print(corr)
print(np.mean([t[1] for t in top]))
print(basic_stats(y))
'''