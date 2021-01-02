from .node_graphics_edge import QNEGraphicsEdge
from .utils import dumpException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_scene import Scene

DEBUG = True


class SceneHistory:
    def __init__(self, scene: 'Scene'):
        self.scene = scene

        self.clear()
        self.history_limit = 50

        # listeners
        self._history_modified_listeners = []
        self._history_stored_listeners = []
        self._history_restored_listeners = []

    def addHistoryModifiedListener(self, callback):
        self._history_modified_listeners.append(callback)

    def addHistoryStoredListener(self, callback):
        self._history_stored_listeners.append(callback)

    def addHistoryRestoredListener(self, callback):
        self._history_restored_listeners.append(callback)

    def clear(self):
        """Clear history stack"""
        self.history_stack = []
        self.history_current_step = -1

    def storeInitialHistoryStamp(self):
        self.storeHistory('Initial History Stamp')

    def canUndo(self):
        return self.history_current_step > 0

    def canRedo(self):
        return self.history_current_step + 1 < len(self.history_stack)

    def undo(self):
        if DEBUG: print('UNDO')
        if self.canUndo():
            self.history_current_step -= 1
            self.restoreHistory()
            self.scene.has_been_modified = True

    def redo(self):
        if DEBUG: print('REDO')
        if self.canRedo():
            self.history_current_step += 1
            self.restoreHistory()
            self.scene.has_been_modified = True

    def restoreHistory(self):
        if DEBUG:
            print('Restoring history .... current step: {}'.format(self.history_current_step),
                  'len {}'.format(len(self.history_stack)))
        self.restoreHistoryStamp(self.history_stack[self.history_current_step])
        # Listeners
        for callback in self._history_modified_listeners:
            callback()

        for callback in self._history_restored_listeners:
            callback()

    def storeHistory(self, desc, setModified=False):
        if setModified:
            self.scene.has_been_modified = True

        if DEBUG:
            print('Storing history ', '{}'.format(desc),
                  '.... current step: {}'.format(self.history_current_step),
                  'len {}'.format(len(self.history_stack)))

        # if the current step is not at the end of the history stack
        if self.history_current_step - 1 < len(self.history_stack):
            self.history_stack = self.history_stack[0:self.history_current_step + 1]

        # history is outside of the limits
        if self.history_current_step + 1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1

        hs = self.createHistoryStamp(desc)
        self.history_stack.append(hs)
        self.history_current_step += 1
        if DEBUG: print(' -- setting step to: ', self.history_current_step)

        # always trigger history modified i.e. updateEditMenu
        for callback in self._history_modified_listeners:
            callback()

        for callback in self._history_stored_listeners:
            callback()

    def createHistoryStamp(self, desc):
        # save selected items
        sel_obj = {
            'nodes': [],
            'edges': [],
        }
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                sel_obj['nodes'].append(item.node.id)
            elif isinstance(item, QNEGraphicsEdge):
                sel_obj['edges'].append(item.edge.id)

        # take a snapshot of current scene
        hystory_stamp = {
            'desc': desc,
            'snapshot': self.scene.serialize(),
            'selection': sel_obj
        }
        return hystory_stamp

    def restoreHistoryStamp(self, history_stamp):
        if DEBUG: print('RHS :', history_stamp['desc'])

        self.scene.deserialize(history_stamp['snapshot'])

        try:
            # restore selection
            if DEBUG: print('restoring edge selection')
            for edge_id in history_stamp['selection']['edges']:
                for edge in self.scene.edges:
                    if edge.id == edge_id:
                        edge.grEdge.setSelected(True)
                        break
            if DEBUG: print('restoring node selection')
            for node_id in history_stamp['selection']['nodes']:
                for node in self.scene.nodes:
                    if node.id == node_id:
                        node.grNode.setSelected(True)
                        break
        except Exception as e:
            dumpException(e)
