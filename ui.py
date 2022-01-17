from distutils import command
from logging import root
import tkinter as tk
from tkinter import Entry, ttk
from tkinter import scrolledtext
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from turtle import left, setheading, window_height

from md5 import MD5


HELP_MESSAGE = """
Программа предназначена для хеширования текстов или файлов.

В зависимости от выбранного режима работы (переключателя) будет предложен либо выбор файла, либо поле для ввода текста.

При нажатии на кнопку "Хешировать" произойдет хеширование с помощью алгоритма MD5.

По завершению работы алгоритма в поле ниже появится результат работы алгоритма(хеш-сумма).

Разработал студент группы бАП-181 Борисов М. А.
"""


class UI:
    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.title("Курсовая по информационной безопасности бАП-181 Борисов Максим")
        self._root.resizable(False, False)
        # _call_theme(root)
        self._main_window()
        self._root.mainloop()

    def _main_window(self) -> None:
        self._input_type = tk.StringVar()
        self._input_type.set("text")

        self._type_frame = ttk.Frame(self._root)
        self._text_radio_button = ttk.Radiobutton(
            self._type_frame,
            text="Текст",
            value="text",
            variable=self._input_type,
            command=self._input_type_changed,
        )
        self._file_radio_button = ttk.Radiobutton(
            self._type_frame,
            text="Файл",
            value="file",
            variable=self._input_type,
            command=self._input_type_changed,
        )

        self._file_radio_button.pack(side="left")
        self._text_radio_button.pack(side="right")
        self._type_frame.pack()

        self._text_field = scrolledtext.ScrolledText(self._root, width=60, height=10)
        self._text_field.pack()

        self._file_frame = ttk.Frame(self._root)

        self._choose_file_btn = ttk.Button(
            self._file_frame,
            text="...",
            command=self.choose_file_btn_clicked,
            width=1,
        )
        self._filepath_field = ttk.Entry(
            self._file_frame,
            width=39,
        )
        self._filepath_field.bind("<Key>", lambda x: "break")

        self._result_field = ttk.Entry(self._root, width=45)
        self._result_field.bind("<Key>", lambda a: "break")

        self._hash_button = ttk.Button(
            self._root, text="Хешировать", command=self._hash_button_clicked
        )
        self._help_button = ttk.Button(
            self._root, text="Помощь", command=self._help_button_clicked
        )

        self._help_button.pack(side="bottom")
        self._hash_button.pack(side="bottom")
        self._result_field.pack(side="bottom")

    def _input_type_changed(self):
        if self._input_type.get() == "file":
            self._choose_file_btn.pack(side="right")
            self._filepath_field.pack(side="left")
            self._file_frame.pack()
            self._text_field.pack_forget()
        elif self._input_type.get() == "text":
            self._text_field.pack()
            self._choose_file_btn.pack_forget()
            self._choose_file_btn.pack_forget()
            self._filepath_field.pack_forget()
            self._file_frame.pack_forget()
        self._result_field.delete(0, tk.END)

    def _hash_button_clicked(self):
        if self._input_type.get() == "file":
            value: str = self._filename
            hash: str = MD5.from_path(value)
        elif self._input_type.get() == "text":
            value: str = self._text_field.get("1.0", tk.END)
            hash: str = MD5.from_str(value)

        self._result_field.delete(0, tk.END)

        if value.strip() == "":
            return
        self._result_field.insert(0, hash)

    def _help_button_clicked(self):
        mb.showinfo("Помощь", HELP_MESSAGE)

    def choose_file_btn_clicked(self):
        self._filename = fd.askopenfilename()
        self._filepath_field.delete(0, tk.END)
        self._filepath_field.insert(0, self._filename)
