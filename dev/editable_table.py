#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import (QtWidgets, QtGui, QtCore)


#############################################################################
class EditDelegate(QtWidgets.QItemDelegate):

    # ========================================================================
    def createEditor(self, parent, option, index):
        """crée les widgets utilisés pour l'édition
        """
        edit = QtWidgets.QLineEdit(parent)
        validator = QtGui.QDoubleValidator()

        validator.setLocale(
            QtCore.QLocale(QtCore.QLocale.French, QtCore.QLocale.France))  # pour Excel français avec virgule
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)  # pour flottants sans exposant
        validator.setRange(+0.0, +100.0, 2)  # pour saisi de % avec 2 chiffres après la virgule

        edit.setValidator(validator)
        return edit

        # ========================================================================

    def setEditorData(self, editor, index):
        """exécuté lors de l'entrée en édition
        """
        edit = editor
        value = index.model().data(index, QtCore.Qt.EditRole)
        edit.setText(value)


#############################################################################
class Fenetre(QtWidgets.QWidget):

    # ========================================================================
    def __init__(self, parent=None):
        super().__init__(parent)

        # définit la taille de la fenêtre
        self.resize(500, 200)

        # crée la table
        self.table = QtWidgets.QTableWidget(self)
        self.table.setRowCount(4)
        self.table.setColumnCount(4)

        # définit le mode de sélection
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)

        # crée le delegate
        self.mondelegate = EditDelegate(self.table)
        self.table.setItemDelegate(self.mondelegate)

        # positionne la table dans la fenêtre
        posit = QtWidgets.QGridLayout()
        posit.addWidget(self.table, 0, 0)
        self.setLayout(posit)

    # ========================================================================
    def copier(self):
        """copie les valeurs sélectionnées dans le clipboard
        """
        selected = self.table.selectedRanges()  # zone sélectionnée à copier
        texte = ""
        for i in range(selected[0].topRow(), selected[0].bottomRow() + 1):
            for j in range(selected[0].leftColumn(), selected[0].rightColumn() + 1):
                texte += self.table.item(i, j).text() + "\t"
            texte = texte[:-1]  # élimine le dernier '\t' en trop
            if i != selected[0].bottomRow():
                texte += "\n"  # ajoute une fin de ligne (sauf pour la dernière)
        # place le texte dans le clipboard
        QtWidgets.QApplication.clipboard().setText(texte)

    # ========================================================================
    def coller(self):
        """colle les données du clipboard à partir de la case sélectionnée
        """
        selected = self.table.selectedRanges()
        row0 = selected[0].topRow()
        col0 = selected[0].leftColumn()
        texte = QtWidgets.QApplication.clipboard().text()
        for i, texteligne in enumerate(texte.split('\n')):
            for j, textecase in enumerate(texteligne.split('\t')):
                self.table.setItem(row0 + i, col0 + j, QtWidgets.QTableWidgetItem(textecase))

    # ========================================================================
    def keyPressEvent(self, event):
        """lance des actions avec certaines touches clavier
        """
        if self.table.hasFocus():
            # Ctrl-C pour copier une zone sélectionnée dans le clipboard
            if event.key() == QtCore.Qt.Key_C and (event.modifiers() & QtCore.Qt.ControlModifier):
                self.copier()
                event.accept()
            # Ctrl-V pour coller une zone du clipboard
            if event.key() == QtCore.Qt.Key_V and (event.modifiers() & QtCore.Qt.ControlModifier):
                self.coller()
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()


#############################################################################
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    fen = Fenetre()
    fen.show()
    sys.exit(app.exec_())