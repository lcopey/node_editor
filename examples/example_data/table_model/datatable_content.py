from PyQt5.QtWidgets import QVBoxLayout
import pandas as pd
from node_editor.node_content_widget import NodeContentWidget
from .dataframe_model import DataframeView

DEBUG = False


class DataTableContent(NodeContentWidget):
    def __init__(self, node: 'Node', parent: 'QWidget' = None, editable=False):
        self.editable = editable
        super().__init__(node, parent)

    def initUI(self):
        df = pd.DataFrame()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)
        self.view = DataframeView(dataframe=df, parent=self, editable=self.editable)
        self.layout.addWidget(self.view)
        self.view.setObjectName(self.node.content_label_objname)

    def print(self, *args):
        if DEBUG:
            print('>DataTableContent :', *args)

    def setDataFrame(self, dataframe: pd.DataFrame):
        self.view.setDataFrame(dataframe, editable=self.editable)

    def getDataFrame(self):
        return self.view.getDataFrame()

    def serialize(self):
        # must return a value otherwise crash on deserialize
        self.print('serialize')
        return 0
    #
    # def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True):
    #     res = super().deserialize(data, hashmap)
    #     try:
    #         value = data['value']
    #         self.edit.setText(value)
    #         return True & res
    #     except Exception as e:
    #         dumpException(e)
    #     return res


class DataEditableTableContent(DataTableContent):
    def __init__(self, node: 'Node', parent: 'QWidget' = None):
        super().__init__(node, parent, editable=True)
