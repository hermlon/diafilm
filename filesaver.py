import os
import cv2

class Filesaver():

    def save(self, output_dir, prefix, no, image):
        if output_dir != "":
            dir_path =  os.path.join(output_dir, prefix)
            try:
                os.mkdir(dir_path)
            except FileExistsError:
                pass
            path =  os.path.join(dir_path, str(no) + ".png")
            cv2.imwrite(path, image)
            print("saving " + path)
        else:
            print("empty output dir")