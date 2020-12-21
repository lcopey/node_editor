def func_name(func):
    def inner(*args, **kwargs):
        print(func.__name__)
        return inner(args, kwargs)

    return inner


def print_func_name(func):
    def inner(*args, **kwargs):
        print(f'Entering function : {func.__name__}')
        return func(*args, **kwargs)

    return inner


def return_simple_id(obj, text):
    return "<{} {}...{}>".format(text, f'{id(obj):02x}'[2:5], f'{id(obj):02x}'[-3:])


def print_scene(scene):
    """Affiche les éléments actuels de la scene"""
    print('SCENE')
    print('  Nodes :')
    [print(node) for node in scene.nodes]
    print('  Edges :')
    [print(edge) for edge in scene.edges]


def print_items(item):
    if 'QNEGraphicsEdge' in item.__str__():
        print('EDGE : ', item.edge)
        print('  Start sockets : ', item.edge.start_socket)
        print('  End sockets : ', item.edge.end_socket)

    elif 'QNEGraphicsSocket' in item.__str__():
        print('SOCKET :', item.socket)
        print('  Edge :', item.socket.edge)

    elif 'QNEGraphicsNode' in item.__str__():
        print('NODE :', item.node)
        print('  Input sockets :', *item.node.inputs)
        print('  Output sockets :', *item.node.outputs)

    else:
        print(item)
