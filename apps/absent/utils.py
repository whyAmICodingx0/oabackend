
def get_responder(request):
    user = request.user
    # 獲取審批者
    # 1. 如果是部門leader
    if user.department.leader.uid == user.uid:
        # 1.1 如果是董事會
        if user.department.name == '董事會':
            responder = None
        else:
            responder = user.department.manager
    # 2. 如果不是部門leader
    else:
        responder = user.department.leader
    return responder