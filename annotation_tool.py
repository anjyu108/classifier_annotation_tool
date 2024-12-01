import tkinter
from PIL import Image, ImageTk
import os
import json
import argparse


class MainWindow():
    def __init__(self, main, args):
        self.current_image_num = 0
        self.main = main
        self.images_dir = args["images_dir"]
        self.json_path = args["json_path"]
        self.image_width = args["width"]
        self.image_height = args["height"]
        self.images_list = os.listdir(self.images_dir)
        self.images_num = len(self.images_list)
        self.img = []
        self.annotation_result = self.load_json()
        self.init_window()
        self.init_shortcuts()

    def init_window(self):
        # タイトルの設定
        self.main.title("yasux annotation tool")

        # 画像名を表示する
        self.image_name = tkinter.Label(
            self.main,
            text=self.images_list[self.current_image_num],
            font=('Times', 12))
        self.image_name.grid(row=0)

        # 画像を表示するキャンバスを作る
        self.canvas = tkinter.Canvas(self.main, width=self.image_width,
                                     height=self.image_height)
        self.canvas.grid(row=1, column=0, rowspan=1)

        # 書かれた指し手を入力するテキストフィールド
        self.move_text_value = tkinter.StringVar()
        self.move_text = tkinter.Entry(width=20, font=('Times', 20),
                                       textvariable=self.move_text_value)
        self.move_text.grid(row=2, column=0)

        # 最初の画像をセット
        self.image_on_canvas = self.canvas.create_image(0, 0,
                                                        anchor=tkinter.NW,
                                                        image=self.img)

        # ショートカットの説明
        self.shortcut_label = tkinter.Label(
            self.main,
            text="next: Enter | back: Ctr-Enter(label not saved)",
            font=('Times', 8),
            )
        self.shortcut_label.grid(row=3, column=0)

        # TODO: fix this tentative separator
        self.txt = tkinter.Label(self.main)
        self.txt.grid(row=4, column=0)
        self.txt["text"] = "---------------------------------------------------------"

        self.txt = tkinter.Label(self.main, bg='white', justify='left')
        self.txt.grid(row=5, column=0)

        # Init the contents
        self.update_contents()

    def init_shortcuts(self):
        self.move_text.focus_force()
        self.main.bind('<Return>', self.onNextButton)
        self.main.bind('<Control-Return>', self.onBackButton)

    def update_contents(self):
        self.set_image()
        self.set_message()
        self.set_move_text()

        # print annotation result for debug
        self.txt["text"] = json.dumps(self.annotation_result, indent=4)

    def set_message(self):
        self.image_name["text"] = self.images_list[self.current_image_num]

    def set_image(self, e=None):
        img = Image.open(os.path.join(self.images_dir,
                                      self.images_list[self.current_image_num]))
        img = img.resize((self.image_width, self.image_height), Image.LANCZOS)
        self.img = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.image_on_canvas, image=self.img)

    def set_move_text(self):
        image_name = self.images_list[self.current_image_num]
        saved_label = self.annotation_result.get(image_name, "")
        self.move_text_value.set(saved_label)

    def onNextButton(self, e=None):
        self.labeling(self.current_image_num, self.move_text.get())

        self.current_image_num += 1
        if self.current_image_num == self.images_num:
            self.current_image_num = 0

        self.update_contents()

    def onBackButton(self, e=None):
        self.current_image_num -= 1
        if self.current_image_num == -1:
            self.current_image_num = self.images_num - 1

        self.update_contents()

    def labeling(self, current_image_num, label_text):
        self.update_json(self.images_list[current_image_num], label_text)

    def load_json(self):
        data = {}
        try:
            data = json.load(open(self.json_path, 'r'))
        except json.JSONDecodeError as e:
            pass
        except FileNotFoundError as e:
            with open(self.json_path, 'w'):
                pass
        return data

    def update_json(self, img_path, label_text):
        self.annotation_result[img_path] = label_text
        with open(self.json_path, 'w') as f:
            json.dump(self.annotation_result, f, indent=4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--images_dir', default=".\\images")
    parser.add_argument('-o', '--output_json', default=".\\result.json")
    parser.add_argument('--width_image', type=int, default=257 * 2)
    parser.add_argument('--height_image', type=int, default=61 * 2)
    args = parser.parse_args()

    root = tkinter.Tk()
    args = {"images_dir": args.images_dir,
            "json_path": args.output_json,
            "width": args.width_image,
            "height": args.height_image,
            }
    MainWindow(root, args)
    root.mainloop()


if __name__ == "__main__":
    main()