from PyQt6.QtWidgets import QLayout, QSizePolicy, QWidgetItem, QApplication
from PyQt6.QtCore import QRect, QSize, Qt, QPoint

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        try:
            return self.itemList[index]
        except IndexError:
            return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(),
                      margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        maxWidth = rect.width()

        for item in self.itemList:
            widget = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + widget.sizeHint().width() + spaceX
            if nextX - rect.x() > maxWidth and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + widget.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), widget.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, widget.sizeHint().height())
        return y + lineHeight - rect.y()
