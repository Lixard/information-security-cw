from cgitb import text
from enum import Enum
from re import L
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import tkinter
from unittest import result

from md5 import MD5, MD5Buffer


class UI:
    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.title("Информационная безопасность бАП-181 Борисов Максим")
        # _call_theme(root)
        self._main_window()
        self._root.mainloop()

    def _main_window(self) -> None:
        self._input_type = tk.StringVar().set("text")

        self._text_radio_button = ttk.Radiobutton(
            text="Текст",
            value="text",
            variable=self._input_type,
            command=self._input_type_changed,
        )
        self._file_radio_button = ttk.Radiobutton(
            text="Файл",
            value="file",
            variable=self._input_type,
            command=self._input_type_changed,
        )

        self._file_radio_button.grid(row=1, column=0)
        self._text_radio_button.grid(row=2, column=0)

        self._text_radio_button.invoke()

        self._text_field = scrolledtext.ScrolledText(self._root, width=60, height=10)
        self._text_field.grid()

        self._result_field = ttk.Entry(self._root, width=45)
        self._result_field.grid()

        self._hash_button = ttk.Button(
            self._root, text="Хешировать", command=self._hash_button_clicked
        )
        self._hash_button.grid()
        self._help_button = ttk.Button(
            self._root, text="Помощь", command=self._help_button_clicked
        )
        self._help_button.grid()

    def _input_type_changed(self):
        pass

    def _hash_button_clicked(self):
        saved: str = self._text_field.get("1.0", tk.END)
        
        hash: str = MD5.hash(saved)
        self._result_field.delete(0, tk.END)
        if saved.strip() == "":
            return
        self._result_field.insert(0, hash)

    def _help_button_clicked(self):
        pass

    # def _call_theme(self.root):
    #     self.root.tk.call("source", "theme.tcl")
    #     self.root.tk.call("set_theme", "light")
