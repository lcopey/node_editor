from PyQt5.QtWidgets import QWidget, QItemDelegate, QLineEdit
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import QLocale, Qt


class EditDelegate(QItemDelegate):

    # ========================================================================
    def createEditor(self, parent, option, index):
        """Create widget to edit cell `DataTableModel`

        Parameters
        ----------
        parent: QWidget
        option
        index

        Returns
        -------
        QWidget
        """
        edit = QLineEdit(parent)

        # define cell validator - Double in this case
        # validator = QDoubleValidator()
        # # Define local numeric format
        # # TODO detect from system
        # local = QLocale(QLocale.French, QLocale.France)
        # validator.setLocale(local)  # pour Excel français avec virgule
        # validator.setNotation(QDoubleValidator.StandardNotation)  # pour flottants sans exposant
        # validator.setRange(+0.0, +100.0, 2)  # pour saisi de % avec 2 chiffres après la virgule
        #
        # edit.setValidator(validator)
        return edit

        # ========================================================================

    def setEditorData(self, editor, index):
        """Executed when entering edition mode

        Parameters
        ----------
        editor
        index

        Returns
        -------

        """
        edit = editor
        value = index.model().data(index, Qt.EditRole)
        edit.setText(value)
