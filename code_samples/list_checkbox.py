#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtGui, QtWidgets


##############################################################################
class Test(QtWidgets.QDialog):

    # =========================================================================
    def __init__(self, listitems=[], parent=None):
        super().__init__(parent)

        self.listWidget = QtWidgets.QListWidget()

        for check, item in listitems:
            qitem = QtWidgets.QListWidgetItem()
            qitem.setText(item)
            qitem.setCheckState(QtCore.Qt.Checked if check else QtCore.Qt.Unchecked)
            self.listWidget.addItem(qitem)

        # optionnel
        self.listWidget.itemClicked.connect(self.modifcoche)

        # crée les boutons pour terminer le dialogue
        boutons = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.boutonbox = QtWidgets.QDialogButtonBox(boutons)
        self.boutonbox.accepted.connect(self.accept)  # => bouton "Ok"
        self.boutonbox.rejected.connect(self.reject)  # => bouton "Annuler"

        # positionner les widgets dans la fenêtre de dialogue
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.listWidget, 0, 0)
        layout.addWidget(self.boutonbox, 1, 0)
        self.setLayout(layout)

    # =========================================================================
    def modifcoche(self, qitem):
        """appelé à chaque modification d'un checkbox avec pour paramètre le
           QListWidgetItem concerné
        """
        ligne = qitem.listWidget().row(qitem)
        item = qitem.text()
        coche = True if qitem.checkState() == QtCore.Qt.Checked else False
        print("ligne:", ligne, "item:", item, "=>", coche)

    # =========================================================================
    def resultat(self):
        """retourne la liste résultat [[check, item], ...]
        """
        self.result = []
        for i in range(0, self.listWidget.count()):
            qitem = self.listWidget.item(i)
            coche = True if qitem.checkState() == QtCore.Qt.Checked else False
            item = qitem.text()
            self.result.append([coche, item])
        return self.result


##############################################################################
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    # données d'entrée
    listitems = [[True, "item0"], [False, "item1"], [False, "item2"], [True, "item3"], [True, "item4"], ]

    # appel dialogue
    form = Test(listitems)

    # exécution du dialogue et résultats
    if form.exec_():
        resultat = form.resultat()
        print()
        for check, item in resultat:
            print(check, item)
    else:
        print()
        print("Annulation")