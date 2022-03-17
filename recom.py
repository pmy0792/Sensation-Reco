import json
import random

import pandas as pd
import requests
import json
import numpy as np
from scipy.sparse.linalg import svds

url = 'http://ation-server.seohyuni.com'


def get_data_from_api():
    res = requests.get(url + '/api/recommend/view-matrix')
    history = json.loads(res.content)
    res = requests.get(url + '/api/recommend/insight-matrix')
    insights = json.loads(res.content)
    res = requests.get(url + '/api/recommend/user-matrix')
    user_id_list = json.loads(res.content)
    '''
    print("History: ",history)
    print("Insights: ",insights)'''
    print("Users:", user_id_list)

    # dummy data
    '''
    user_id_list=[1,2,3,4,5,6]
    user_history_dict={1:[1,6],2:[],3:[4,6,8,9,12,18],4:[13,14,15,16],5:[1,3,2,10],6:[1,2,3,4,5,6]}
    for i in range(20):
        insight_df.loc[i]=[i,"title {}".format(i)]
    '''

    history_df = pd.DataFrame(history, columns=['user_id', 'insight_id'])
    insight_df = pd.DataFrame(insights, columns=['insight_id', 'insight_title'])
    user_df = pd.DataFrame(user_id_list, columns=['user_id'])

    insight_id_list = [i for i in range(20)]

    user_history_dict = dict()
    for user in user_id_list:
        user_history_dict[user] = []

    for item in history:
        user, insight = item[0], item[1]
        user_history_dict[user].append(insight)

    history_df = pd.DataFrame(columns=['user_id', 'insight_id', 'seen'])
    for user in user_id_list:
        for insight in insight_id_list:
            if insight in user_history_dict[user]:
                history_df = history_df.append({'user_id': user, 'insight_id': insight, 'seen': 1}, ignore_index=True)

    insight_df = pd.DataFrame(insights, columns=['insight_id', 'insight_title'])

    insight_df = insight_df.astype({'insight_id': 'int'})
    # user_insight_data=pd.merge(history_df,insight_df, on='insight_id')
    user_insight_history = history_df.pivot_table(
        index='user_id',
        columns='insight_id',
        values='seen',
        aggfunc='first').fillna(0)

    matrix = user_insight_history.values
    user_seen_mean = np.mean(matrix, axis=1)
    normalized = matrix - user_seen_mean.reshape(-1, 1)
    U, sigma, Vt = svds(normalized, k=1)

    sigma = np.diag(sigma)
    svd_user_predicted = np.dot(np.dot(U, sigma), Vt) + user_seen_mean.reshape(-1, 1)

    df_svd_preds = pd.DataFrame(svd_user_predicted,
                                columns=user_insight_history.columns,
                                index=user_insight_history.index
                                )

    return df_svd_preds, insight_df, history_df


def recommend_insights(df_svd_preds, user_id, insight_df, history_df, num_recommendations=4):
    # 해당 사용자의 예상점수 높게 나온 순서대로 정렬
    user_id = int(user_id)
    user_rec_data = df_svd_preds[df_svd_preds.index == user_id].iloc[0]
    sorted_user_predictions = user_rec_data.sort_values(ascending=False)

    user_data = history_df[history_df.user_id == user_id]
    user_history = user_data.merge(insight_df, on='insight_id').sort_values(['seen'], ascending=False)
    recommendations = insight_df[~insight_df['insight_id'].isin(user_history['insight_id'])]
    recommendations = recommendations.merge(pd.DataFrame(sorted_user_predictions).reset_index(), on='insight_id')
    recommendations = recommendations.rename(columns={user_id: 'Predictions'}).sort_values('Predictions',
                                                                                           ascending=False)
    recommendations = recommendations[:num_recommendations]
    recommendations = recommendations['insight_id'].to_list()
    while len(recommendations) < 4:
        spare_rec = random.sample(range(1, insight_df.shape[0]), 1)
        if spare_rec[0] not in recommendations:
            recommendations += spare_rec
    return recommendations


def get_rec(user_id):
    df_svd_preds, insight_df, history_df = get_data_from_api()
    print("Df_svd_preds:\n", df_svd_preds)
    if (user_id not in history_df["user_id"].values):
        return random.sample(range(1, insight_df.shape[0]), 4)
    return recommend_insights(df_svd_preds, user_id, insight_df, history_df)
