"""
GUI of Gene
"""
import Gene
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import threading


class App:
    def __init__(self):
        """
        Initialize Main Frame
        """
        # root window
        self.root = Tk()
        self.root.title('GeneQuery')
        # self.root.columnconfigure(0, weight=1)
        # self.root.rowconfigure(0, weight=1)
        # self.root.rowconfigure(1, weight=1)
        # self.root.rowconfigure(2, weight=1)
        # make root not resizable
        self.root.resizable(False, False)

        # container frame
        self.mainframe = ttk.Frame(self.root, padding=(5, 5, 5, 0))

        # input widgets
        self.input_label = ttk.Label(self.mainframe,
                                     text='DNA Sequence File',
                                     justify='left')
        self.input_entry_var = StringVar()
        self.input_entry = ttk.Entry(self.mainframe,
                                     width=30,
                                     textvariable=self.input_entry_var)
        self.input_button = ttk.Button(self.mainframe,
                                       text='Open...',
                                       command=self.open_button)

        # Species selection box
        self.species_frame = ttk.Frame(self.root, padding=(5, 0, 5, 5))
        self.species_label = ttk.Label(self.species_frame,
                                       text='Species',
                                       justify='left')
        # Load list of species from species.txt
        self.species = [x.strip() for x in open('species.txt', 'r')]
        self.species_var = StringVar()
        self.species_box = ttk.Combobox(self.species_frame,
                                        textvariable=self.species_var,
                                        values=self.species,
                                        state='readonly',
                                        width=65)

        # Output widgets
        self.output_frame = ttk.Frame(self.root, padding=(5, 0, 5, 5))
        self.output_label = ttk.Label(self.output_frame,
                                      text='Output Directory',
                                      justify='left')
        self.output_entry_var = StringVar()
        self.output_entry = ttk.Entry(self.output_frame,
                                      width=30,
                                      textvariable=self.output_entry_var)
        self.output_button = ttk.Button(self.output_frame,
                                        text='Select Output',
                                        command=self.output_select)

        # Progress and Query
        self.progress = ttk.Progressbar(self.output_frame,
                                        orient='horizontal',
                                        mode='determinate',
                                        value=0)
        self.query_button = ttk.Button(self.output_frame,
                                       text='Query',
                                       command=self.query)

        # Assign grid
        self.mainframe.grid(row=0, column=0, sticky='nswe')
        self.species_frame.grid(row=1, column=0, sticky='nswe')
        self.output_frame.grid(row=2, column=0, sticky='nswe')

        # Input Widgets
        self.input_label.grid(row=1, column=0, sticky='nws')
        self.input_entry.grid(row=2, column=0, sticky='we')
        self.input_button.grid(row=2, column=1, padx=(5, 0))

        # Species Widgets
        self.species_label.grid(row=1, column=0, sticky='nws')
        self.species_box.grid(row=2, column=0, sticky='we')

        # Output Widgets
        self.output_label.grid(row=1, column=0, sticky='nws')
        self.output_entry.grid(row=2, column=0, sticky='we')
        self.output_button.grid(row=2, column=1, padx=(5, 0))

        # Progress/Query
        self.progress.grid(row=3, column=0, sticky='we')
        self.query_button.grid(row=3, column=1, padx=(5, 0))

        # Configure Grid
        self.mainframe.columnconfigure(0, weight=1)
        self.species_frame.columnconfigure(0, weight=1)
        self.output_frame.columnconfigure(0, weight=1)
        self.output_frame.rowconfigure(3, pad=7)

        # open window
        self.root.mainloop()

    def open_button(self):
        """
        Asks user for DNA file
        """
        response = filedialog.askopenfilename(title='Open DNA Sequence',
                                              filetypes=[('', '.*')])
        self.input_entry_var.set(response)

    def output_select(self):
        """
        Asks user for output directory
        """
        response = filedialog.askdirectory(title='Select output directory')
        if response != '':
            self.output_entry_var.set(response + '/')

    def query(self):
        """
        Perform Tool Queries and Output Excel File
        """
        # disable query button
        self.query_button.state(['disabled'])
        # check for proper user input
        if not self.__validate_input():
            pass

        # set progressbar (6 tools + 1 excel write)
        self.progress.configure(maximum=7)

        output = self.output_entry_var.get()
        # try to open DNA file, if error, prompt user
        try:
            sequence = Gene.GeneFile(self.input_entry_var.get())
            # query DNA sequence and update progress bar
            self.files = []
            lock = threading.Lock()
            threads = [threading.Thread(target=query_thread,
                                        args=(sequence.glimmer_query,
                                              output + sequence.name + '.glimmer',
                                              self.files,
                                              lock)),
                       threading.Thread(target=query_thread,
                                        args=(sequence.genemark_query,
                                              output + sequence.name + '.gm',
                                              self.files,
                                              lock)),
                       threading.Thread(target=query_thread,
                                        args=(sequence.genemarkhmm_query,
                                              output + sequence.name + '.gmhmm',
                                              self.files,
                                              lock)),
                       threading.Thread(target=query_thread,
                                        args=(sequence.genemarks_query,
                                              output + sequence.name + '.gms',
                                              self.files,
                                              lock)),
                       threading.Thread(target=query_thread,
                                        args=(sequence.genemarks2_query,
                                              output + sequence.name + '.gms2',
                                              self.files,
                                              lock)),
                       threading.Thread(target=query_thread,
                                        args=(sequence.genemark_heuristic_query,
                                              output + sequence.name + '.heuristic',
                                              self.files,
                                              lock))]

            for x in threads:
                x.start()

            # wait until threads finish
            self.wait_gui()
            self.progress.step(1)
            self.root.update_idletasks()

            # write to excel
            Gene.excel_write(output, self.files, sequence)
            self.progress.step(1)
            self.root.update_idletasks()

            # show success message
            messagebox.showinfo(title='Gene Queried!',
                                message='Gene Query Successful. Files written to: ' + output)

        except FileNotFoundError:
            messagebox.showerror(title='Invalid Input File',
                                 message='Provided input file does not exist.')
        except Exception as e:
            messagebox.showerror(title='Query Error',
                                 message=str(e))

        # enable query button / reset progress
        self.query_button.state(['!disabled'])
        self.progress['value'] = 0

    def wait_gui(self):
        """
        Method for GUI to wait and update progress bar while threads finish
        :return:
        """
        while len(self.files) != 6:
            self.progress['value'] = len(self.files)
            self.root.update_idletasks()
            self.root.after(100, self.wait_gui)

    def __validate_input(self):
        """
        Check if DNA file, species and output file were given
        :return: True/False if all parameters were met
        """
        # Check for input
        if self.input_entry_var.get() == '':
            messagebox.showinfo(title='Missing Input File',
                                message='Please provide an input file')
            return False

        # Check for species
        if self.species_var.get() == '':
            messagebox.showinfo(title='Missing Species',
                                message='Please select a species')
            return False

        # Check output
        if self.output_entry_var.get() == '':
            messagebox.showinfo(title='Missing Output Directory',
                                message='Please provide an output directory')
            return False

        return True


def query_thread(func, output, files, lock):
    """
    Function called by threads to call Tool APIs
    :param func: GeneFile.query() call
    :param output: output file name
    :param files: list of outputted file names
    :param lock: lock to protect files list
    :return:
    """
    file = func(out=output)
    with lock:
        files.append(file)


if __name__ == '__main__':
    app = App()
