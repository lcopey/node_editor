def func_name(func):
    def inner(*args, **kwargs):
        print(func.__name__)
        return inner(args, kwargs)

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
        print(item)
        print('EDGE : ', item.edge)
        print('  Start socket : ', item.edge.start_socket)
        print('  End socket : ', item.edge.end_socket)

    elif 'QNEGraphicsSocket' in item.__str__():
        print('SOCKET :', item.socket)
        print('  Edges :', item.socket.edges)

    elif 'QNEGraphicsNode' in item.__str__():
        print('NODE :', item.node)
        print('  Input socket :', *item.node.inputs)
        print('  Output socket :', *item.node.outputs)

    else:
        print(item)
