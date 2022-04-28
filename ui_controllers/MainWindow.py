import cv2
from PyQt5 import uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QFileDialog


def find_shapes(file_name):
    image = cv2.imread(file_name)
    contours = find_contours(image)
    shapes = get_shapes_from_contours(contours, image)
    cv2.imwrite('images/result.jpg', image)
    return shapes


def find_contours(image):
    gr = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gr, 10, 250)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
    contours = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    return contours


def get_shapes_from_contours(contours, image):
    shapes_list = []

    for contour in contours:
        sm = cv2.arcLength(contour, True)
        apd = cv2.approxPolyDP(contour, 0.02 * sm, True)

        if len(apd) == 3:
            shapes_list.append("Triangle")
            cv2.drawContours(image, [apd], -1, (0, 255, 0), 4)
        elif len(apd) == 4:
            shapes_list.append("Quadrilateral")
            cv2.drawContours(image, [apd], -1, (255, 0, 0), 4)
        elif len(apd) == 8:
            shapes_list.append("Circle")
            cv2.drawContours(image, [apd], -1, (255, 255, 255), 4)
        else:
            shapes_list.append("Unexpected Shape")
            cv2.drawContours(image, [apd], -1, (0, 0, 255), 4)

    return shapes_list


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/main_window.ui", self)
        self.inputFileButton.clicked.connect(self.on_input_file_button_clicked)
        self.findShapesButton.clicked.connect(self.on_find_shape_button_clicked)

        self.current_image = ""

    def on_input_file_button_clicked(self):
        image_file_name = QFileDialog.getOpenFileName(self, 'Open file', 'images',
                                                      filter="Images (*.png *.xpm *.jpg)")[0]
        self.current_image = image_file_name
        self.set_new_image_to_label(image_file_name)

    def on_find_shape_button_clicked(self):
        image_file_name = self.current_image
        if image_file_name != "":
            shapes = find_shapes(image_file_name)
            shapes_dict = self.shapes_to_dict(shapes)
            self.add_shapes_to_shapes_label(shapes_dict)
            self.set_new_image_to_label()

    @staticmethod
    def shapes_to_dict(shapes):
        shapes_dict = dict()
        for shape in shapes:
            if shape in shapes_dict:
                shapes_dict[shape] = shapes_dict[shape] + 1
            else:
                shapes_dict[shape] = 1
        return shapes_dict

    def add_shapes_to_shapes_label(self, shapes_dict):
        self.foundShapesTextField.setText("")

        for shape, repeats in shapes_dict.items():
            self.foundShapesTextField.setText(self.foundShapesTextField.toPlainText() + f"{shape} - {repeats}\n")

    def set_new_image_to_label(self, file_name="images/result.jpg"):
        pixmap: QPixmap = QPixmap(file_name)
        preferred_width = 1531
        preferred_height = 911

        self.imageLabel.setPixmap(
            pixmap.scaled(QSize(preferred_width, preferred_height), Qt.KeepAspectRatio, Qt.SmoothTransformation))
