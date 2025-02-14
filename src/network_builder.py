import networkx as nx

def build_network(user_id, df_requests, selected_date):
    """선택된 날짜까지의 네트워크 그래프 구축"""
    G = nx.Graph()
    G.add_node(str(user_id), label=str(user_id))  # 모든 ID를 문자열로 저장

    filtered_requests = df_requests[df_requests["created_at"] <= selected_date]
    
    for _, row in filtered_requests.iterrows():
        friend_id = str(row["send_user_id"])  # ID를 문자열로 변환
        G.add_node(friend_id, label=friend_id)
        G.add_edge(str(user_id), friend_id)

    return G
