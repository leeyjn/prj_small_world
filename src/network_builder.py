import networkx as nx
import pandas as pd

def build_network(user_id, df_requests):
    """ 선택된 유저의 친구 네트워크를 그래프로 구축 """
    G = nx.Graph()
    G.add_node(user_id)  # 중심 유저 추가

    for _, row in df_requests.iterrows():
        friend_id = row["send_user_id"]
        G.add_node(friend_id)  # 친구 추가
        G.add_edge(user_id, friend_id)  # 중심 유저와 연결

    return G
