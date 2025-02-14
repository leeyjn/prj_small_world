import networkx as nx

def build_network(user_id, df_requests, selected_date):
    """선택된 날짜까지의 네트워크 그래프 구축"""
    G = nx.Graph()
    G.add_node(int(user_id), label=str(user_id))  # 초기 노드

    filtered_requests = df_requests[df_requests["created_at"] <= selected_date]
    
    for _, row in filtered_requests.iterrows():
        G.add_node(row["send_user_id"], label=str(row["send_user_id"]))
        G.add_edge(int(user_id), row["send_user_id"])

    return G
