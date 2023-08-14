import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from ebooklib import epub


# def merge_epubs(filenames, output_filename):
#    # Create a new EPUB book
#    merged_book = epub.EpubBook()
#
#    for filename in filenames:
#        book = epub.read_epub(filename)
#        for item in book.get_items():
#            # Handle items (chapters, styles, images, etc.)
#            # This would need careful handling to avoid overwriting items
#            # with the same ID from different books
#            pass
#
#    # Write the merged book to disk
#    epub.write_epub(output_filename, merged_book)


# def find_files(directory, extension):
#    return [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.endswith(extension)]


# def main():
#    filetype = input("Enter the filetype (.zip, .epub, or leave blank for both): ")
#    directory = input("Enter the directory to look in: ")
#    output_folder = input("Enter the output folder: ")
#
#    if not os.path.exists(output_folder):
#        os.makedirs(output_folder)
#
#    files_to_merge = []
#
#    if filetype in ["", ".zip"]:
#        files_to_merge.extend(find_files(directory, '.zip'))
#    if filetype in ["", ".epub"]:
#        files_to_merge.extend(find_files(directory, '.epub'))
#
#    output_filename = os.path.join(output_folder, 'merged.epub')
#
#    merge_epubs(files_to_merge, output_filename)


def find_files(directory, extensions):
    files = []
    print(extensions)
    for extension in extensions:
        files.extend([os.path.join(directory, filename) for filename in os.listdir(directory) if
                      filename.endswith(extension)])
    return files


class App:
    def __init__(self, root):
        self.root = root
        self.file_types = []

        self.root.title("EPUB Merger")

        self.tracker_var = tk.IntVar(root, value=2)
        # print(self.tracker_var.get())
        self.tracker_var.trace_add('write', self.change_file_selection)

        self.label = tk.Label(root, text="Select the directory containing .zip and .epub files:")
        # self.label.pack(pady=20)
        self.label.grid(row=0, column=0, pady=5, columnspan=3)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse)
        self.browse_button.grid(row=1, column=0, pady=5, columnspan=3)
        # sself.browse_button.pack(pady=20)

        self.zip_only = tk.Radiobutton(root, text=".zip", variable=self.tracker_var, value=0)
        self.zip_only.grid(row=2, column=0)
        self.epub_only = tk.Radiobutton(root, text=".epub", variable=self.tracker_var, value=1)
        self.epub_only.grid(row=2, column=1)
        self.both_ze = tk.Radiobutton(root, text="both", variable=self.tracker_var, value=2)
        self.both_ze.grid(row=2, column=2)

        # self.zip_only.deselect()
        # self.epub_only.deselect()
        # self.both_ze.invoke()

        # self.both_ze.pack(anchor=tk.W)
        # self.epub_only.pack(anchor=tk.W)
        # self.zip_only.pack(anchor=tk.W)

        self.files_listbox = tk.Listbox(root)
        self.files_listbox.grid(row=3, column=0, columnspan=3, pady=5, padx=5, sticky=tk.NSEW)
        # self.files_listbox.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=4, column=0, columnspan=3, pady=5, padx=5, sticky=tk.NSEW)
        # self.progress_bar.pack(pady=20)

        self.merge_button = tk.Button(root, text="Merge", command=self.merge)
        self.merge_button.grid(row=5, column=0, columnspan=3, pady=5, padx=5, sticky=tk.NSEW)

        # self.merge_button.pack(pady=20)

    def change_file_selection(self, *args):
        print(f"args: {args}")
        # print(str(self.tracker_var.get()))
        # self.file_types = [*args]
        # for arg in args:
        #    self.file_types.append(arg)
        # selection = "You selected the option " + str(var.get())
        # label.config(text=selection)
        # selection = self.tracker_var.get() #args[0]
        t_var = self.tracker_var.get()
        print(f"t_var: {t_var}\ntracker_var: {self.tracker_var.get()}")
        self.file_types = []
        if t_var == 0:
            self.file_types = ['.zip']
        elif t_var == 1:
            self.file_types = ['.epub']
        elif t_var == 2:
            self.file_types = ['.zip', '.epub']
        else:
            print(f"Error: invalid file type selection, {t_var}")
        # breakpoint()
        return

    def browse(self):
        folder_selected = filedialog.askdirectory()
        if not folder_selected:
            return

        files_to_merge = find_files(folder_selected, self.file_types)
        self.files_listbox.delete(0, tk.END)  # clear the listbox
        for file in files_to_merge:
            self.files_listbox.insert(tk.END, file)

    def merge(self):
        output_file = filedialog.asksaveasfilename(defaultextension=".epub", filetypes=[("EPUB files", "*.epub")])
        if not output_file:
            return

        files_to_merge = self.files_listbox.get(0, tk.END)
        total_files = len(files_to_merge)
        self.progress_bar["maximum"] = total_files

        # for index, file in enumerate(files_to_merge):
        # self.progress_bar["value"] = index + 1
        # self.root.update_idletasks()

        merged_book = epub.EpubBook()
        toc_items = []

        for index, filename in enumerate(files_to_merge):
            book = epub.read_epub(filename)

            merged_book.set_identifier(book.get_identifier())
            merged_book.set_title(book.get_metadata('DC', 'title')[0][0])
            for author in book.get_metadata('DC', 'creator'):
                merged_book.add_author(author[0])

            for item in book.items:
                new_file_name = f"book_{index}_{os.path.basename(item.file_name)}"
                item.file_name = new_file_name

                # Add item to the merged book
                merged_book.add_item(item)

                if isinstance(item, epub.EpubHtml):
                    toc_items.append(item)

        # Create a table of contents
        merged_book.toc = toc_items

        # Define the spine (this controls the reading order)
        # nav = table of contents
        merged_book.spine = ['nav'] + toc_items

        epub.write_epub(output_file, merged_book)
        tk.messagebox.showinfo("Success", "Files merged successfully!")


if __name__ == "__main__":
    primary = tk.Tk()
    app = App(primary)
    primary.mainloop()
