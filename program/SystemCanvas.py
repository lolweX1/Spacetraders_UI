from PyQt6 import QtWidgets, QtGui, QtCore
import GlobalVariableAccess as gva
from Authorize import *

class SystemCanvas(QtWidgets.QWidget):
    def __init__(self, width=800, height=600):
        super().__init__()
        self.setMinimumSize(width, height)
        self.points = {}  # {"system_name": [x, y]}
        self.offset = QtCore.QPointF(0, 0)
        self._last_mouse_pos = None
        self.scale_factor = 1.0  # for zoom in/out

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)

        self.center_point = gva.ship_data["nav"]["waypointSymbol"]
        self.center_data = get_generic_data(f"https://api.spacetraders.io/v2/systems/{gva.system}/waypoints/{self.center_point}")
        print(self.center_data)
        self.center_data_dir = [self.center_data["data"]["x"], self.center_data["data"]["y"]]

    def set_points(self, points_dict):
        self.points = points_dict
        self.update()

    # --- Mouse drag for panning ---
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._last_mouse_pos = event.position()
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self._last_mouse_pos is not None:
            delta = event.position() - self._last_mouse_pos
            self.offset += delta
            self._last_mouse_pos = event.position()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._last_mouse_pos = None
            self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)

    # --- Keyboard input ---
    def keyPressEvent(self, event):
        key = event.key()
        step = 40  # move amount per arrow press

        if key == QtCore.Qt.Key.Key_Left:
            self.offset += QtCore.QPointF(step, 0)
        elif key == QtCore.Qt.Key.Key_Right:
            self.offset += QtCore.QPointF(-step, 0)
        elif key == QtCore.Qt.Key.Key_Up:
            self.offset += QtCore.QPointF(0, step)
        elif key == QtCore.Qt.Key.Key_Down:
            self.offset += QtCore.QPointF(0, -step)
        elif key == QtCore.Qt.Key.Key_Plus or key == QtCore.Qt.Key.Key_Equal:
            self.scale_factor *= 1.1  # zoom in
        elif key == QtCore.Qt.Key.Key_Minus or key == QtCore.Qt.Key.Key_Underscore:
            self.scale_factor /= 1.1  # zoom out

        self.update()

    # --- Drawing ---
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # background
        painter.fillRect(self.rect(), QtGui.QColor("black"))

        # apply offset and scaling
        painter.translate(self.offset)
        painter.scale(self.scale_factor, self.scale_factor)

        pen = QtGui.QPen(QtGui.QColor("white"), 3)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("white")))

        font = painter.font()
        font.setPointSize(3)
        painter.setFont(font)
        print(self.points.items())
        for name, (x, y) in self.points.items():
            mx = x-self.center_data_dir[0]
            my = y-self.center_data_dir[1]
            if (mx == 0 and my == 0):
                painter.setBrush(QtGui.QBrush(QtGui.QColor("red")))
            else:
                painter.setBrush(QtGui.QBrush(QtGui.QColor("white")))
            painter.drawEllipse(QtCore.QPointF(mx, my), 5, 5)
            painter.drawText(x + 10 - self.center_data_dir[0], y - 10 - self.center_data_dir[1], name)
        
class CanvasWindow(QtWidgets.QMainWindow):
    def __init__(self, title="Stars Map"):
        super().__init__()
        self.setWindowTitle(title)
        self.canvas = SystemCanvas()
        self.setCentralWidget(self.canvas)
        self.resize(800, 600)

    def set_points(self, points_dict):
        self.canvas.set_points(points_dict)