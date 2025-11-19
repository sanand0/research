"""
Word File Splitter & Renamer GUI
Main application with tabbed interface for splitting and renaming files.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading

from word_splitter import WordSplitter
from file_renamer import FileRenamer, SuffixType, PREDEFINED_PREFIXES


class SplitterTab(ttk.Frame):
    """Tab for Word file splitting functionality."""

    def __init__(self, parent):
        """Initialize the Splitter tab."""
        super().__init__(parent)
        self.splitter = WordSplitter()
        self.processing_thread = None
        self.create_widgets()

    def create_widgets(self):
        """Create all widgets for the Splitter tab."""
        # Input Path Section
        input_frame = ttk.LabelFrame(self, text="Input", padding=10)
        input_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        ttk.Label(input_frame, text="Path:").grid(row=0, column=0, sticky="w", pady=2)
        self.input_path_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_path_var, width=50)
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Button(input_frame, text="Browse File", command=self.browse_input_file).grid(
            row=0, column=2, padx=2, pady=2
        )
        ttk.Button(input_frame, text="Browse Folder", command=self.browse_input_folder).grid(
            row=0, column=3, padx=2, pady=2
        )

        input_frame.columnconfigure(1, weight=1)

        # Output Path Section
        output_frame = ttk.LabelFrame(self, text="Output", padding=10)
        output_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        ttk.Label(output_frame, text="Path:").grid(row=0, column=0, sticky="w", pady=2)
        self.output_path_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path_var, width=50).grid(
            row=0, column=1, sticky="ew", padx=5, pady=2
        )
        ttk.Button(output_frame, text="Browse", command=self.browse_output_folder).grid(
            row=0, column=2, padx=2, pady=2
        )

        output_frame.columnconfigure(1, weight=1)

        # Delimiter Section
        delimiter_frame = ttk.LabelFrame(self, text="Delimiter", padding=10)
        delimiter_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        ttk.Label(delimiter_frame, text="Delimiter:").grid(row=0, column=0, sticky="w", pady=2)
        self.delimiter_var = tk.StringVar(value="***")
        ttk.Entry(delimiter_frame, textvariable=self.delimiter_var, width=20).grid(
            row=0, column=1, sticky="w", padx=5, pady=2
        )
        ttk.Label(delimiter_frame, text="(Default: ***)").grid(row=0, column=2, sticky="w", padx=5)

        # Batch Processing Option
        self.batch_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            delimiter_frame,
            text="Batch Processing (Process all files in input folder)",
            variable=self.batch_mode_var
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=5)

        # Progress Section
        progress_frame = ttk.LabelFrame(self, text="Progress", padding=10)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.status_var).grid(
            row=1, column=0, sticky="w", padx=5, pady=2
        )

        progress_frame.columnconfigure(0, weight=1)

        # Control Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)

        self.start_button = ttk.Button(
            button_frame,
            text="Start",
            command=self.start_processing,
            width=15
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = ttk.Button(
            button_frame,
            text="Pause",
            command=self.pause_processing,
            width=15,
            state="disabled"
        )
        self.pause_button.grid(row=0, column=1, padx=5)

        self.stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self.stop_processing,
            width=15,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=2, padx=5)

        # Configure grid weights
        self.columnconfigure(0, weight=1)

    def browse_input_file(self):
        """Browse for input file."""
        filename = filedialog.askopenfilename(
            title="Select Word File",
            filetypes=[("Word Documents", "*.docx *.doc"), ("All Files", "*.*")]
        )
        if filename:
            self.input_path_var.set(filename)

    def browse_input_folder(self):
        """Browse for input folder."""
        foldername = filedialog.askdirectory(title="Select Input Folder")
        if foldername:
            self.input_path_var.set(foldername)

    def browse_output_folder(self):
        """Browse for output folder."""
        foldername = filedialog.askdirectory(title="Select Output Folder")
        if foldername:
            self.output_path_var.set(foldername)

    def start_processing(self):
        """Start the splitting process."""
        input_path = self.input_path_var.get().strip()
        output_path = self.output_path_var.get().strip()
        delimiter = self.delimiter_var.get().strip()

        # Validation
        if not input_path:
            messagebox.showerror("Error", "Please specify an input path")
            return

        if not output_path:
            messagebox.showerror("Error", "Please specify an output path")
            return

        if not delimiter:
            messagebox.showerror("Error", "Please specify a delimiter")
            return

        if not os.path.exists(input_path):
            messagebox.showerror("Error", "Input path does not exist")
            return

        # Update button states
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.stop_button.config(state="normal")

        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting...")

        # Update splitter delimiter
        self.splitter.delimiter = delimiter

        # Start processing in background thread
        self.processing_thread = threading.Thread(target=self._process, daemon=True)
        self.processing_thread.start()

    def _process(self):
        """Background processing method."""
        try:
            input_path = self.input_path_var.get().strip()
            output_path = self.output_path_var.get().strip()
            is_batch = self.batch_mode_var.get()

            if is_batch or os.path.isdir(input_path):
                # Batch processing
                results = self.splitter.split_batch(
                    input_path,
                    output_path,
                    progress_callback=self._update_progress
                )

                if not self.splitter.is_stopped:
                    messagebox.showinfo(
                        "Batch Complete",
                        f"Successfully processed: {len(results['success'])} files\n"
                        f"Failed: {len(results['failed'])} files"
                    )
            else:
                # Single file processing
                output_files = self.splitter.split_single_file(
                    input_path,
                    output_path,
                    progress_callback=self._update_progress
                )

                if not self.splitter.is_stopped:
                    messagebox.showinfo(
                        "Complete",
                        f"Successfully created {len(output_files)} files"
                    )

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self._update_progress(0, f"Error: {str(e)}")

        finally:
            # Reset button states
            self.start_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")
            if not self.splitter.is_stopped:
                self.pause_button.config(text="Pause")

    def _update_progress(self, percent: int, message: str):
        """Update progress bar and status message."""
        self.progress_var.set(percent)
        self.status_var.set(message)

    def pause_processing(self):
        """Pause or resume the processing."""
        if self.splitter.is_paused:
            self.splitter.resume()
            self.pause_button.config(text="Pause")
            self.status_var.set("Resumed...")
        else:
            self.splitter.pause()
            self.pause_button.config(text="Resume")
            self.status_var.set("Paused")

    def stop_processing(self):
        """Stop the processing."""
        self.splitter.stop()
        self.status_var.set("Stopping...")
        self.pause_button.config(state="disabled")
        self.stop_button.config(state="disabled")


class RenamerTab(ttk.Frame):
    """Tab for file renaming functionality."""

    def __init__(self, parent):
        """Initialize the Renamer tab."""
        super().__init__(parent)
        self.renamer = FileRenamer()
        self.processing_thread = None
        self.file_list = []
        self.create_widgets()

    def create_widgets(self):
        """Create all widgets for the Renamer tab."""
        # Input Path Section
        input_frame = ttk.LabelFrame(self, text="Input Folder", padding=10)
        input_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        ttk.Label(input_frame, text="Path:").grid(row=0, column=0, sticky="w", pady=2)
        self.input_path_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_path_var, width=50).grid(
            row=0, column=1, sticky="ew", padx=5, pady=2
        )
        ttk.Button(input_frame, text="Browse", command=self.browse_input_folder).grid(
            row=0, column=2, padx=2, pady=2
        )
        ttk.Button(input_frame, text="Load Files", command=self.load_files).grid(
            row=0, column=3, padx=2, pady=2
        )

        input_frame.columnconfigure(1, weight=1)

        # Output Path Section
        output_frame = ttk.LabelFrame(self, text="Output Folder", padding=10)
        output_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        ttk.Label(output_frame, text="Path:").grid(row=0, column=0, sticky="w", pady=2)
        self.output_path_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path_var, width=50).grid(
            row=0, column=1, sticky="ew", padx=5, pady=2
        )
        ttk.Button(output_frame, text="Browse", command=self.browse_output_folder).grid(
            row=0, column=2, padx=2, pady=2
        )

        output_frame.columnconfigure(1, weight=1)

        # Naming Options Section
        naming_frame = ttk.LabelFrame(self, text="Naming Options", padding=10)
        naming_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        # Prefix
        ttk.Label(naming_frame, text="Prefix:").grid(row=0, column=0, sticky="w", pady=2)

        prefix_inner_frame = ttk.Frame(naming_frame)
        prefix_inner_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        self.prefix_combo = ttk.Combobox(
            prefix_inner_frame,
            values=PREDEFINED_PREFIXES,
            width=15,
            state="readonly"
        )
        self.prefix_combo.set(PREDEFINED_PREFIXES[0])
        self.prefix_combo.grid(row=0, column=0, padx=2)

        ttk.Label(prefix_inner_frame, text="or Custom:").grid(row=0, column=1, padx=5)

        self.custom_prefix_var = tk.StringVar()
        ttk.Entry(prefix_inner_frame, textvariable=self.custom_prefix_var, width=20).grid(
            row=0, column=2, padx=2
        )

        # Suffix Type
        ttk.Label(naming_frame, text="Suffix Type:").grid(row=1, column=0, sticky="w", pady=2)

        suffix_frame = ttk.Frame(naming_frame)
        suffix_frame.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        self.suffix_type_var = tk.StringVar(value="numeric")

        ttk.Radiobutton(
            suffix_frame,
            text="Numeric (1, 2, 3, ...)",
            variable=self.suffix_type_var,
            value="numeric"
        ).grid(row=0, column=0, sticky="w", padx=5)

        ttk.Radiobutton(
            suffix_frame,
            text="Alpha Lower (a, b, c, ...)",
            variable=self.suffix_type_var,
            value="alpha_lower"
        ).grid(row=0, column=1, sticky="w", padx=5)

        ttk.Radiobutton(
            suffix_frame,
            text="Alpha Upper (A, B, C, ...)",
            variable=self.suffix_type_var,
            value="alpha_upper"
        ).grid(row=1, column=0, sticky="w", padx=5)

        ttk.Radiobutton(
            suffix_frame,
            text="Roman Lower (i, ii, iii, ...)",
            variable=self.suffix_type_var,
            value="roman_lower"
        ).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Radiobutton(
            suffix_frame,
            text="Roman Upper (I, II, III, ...)",
            variable=self.suffix_type_var,
            value="roman_upper"
        ).grid(row=2, column=0, sticky="w", padx=5)

        # Start Number
        ttk.Label(naming_frame, text="Start From:").grid(row=2, column=0, sticky="w", pady=2)
        self.start_number_var = tk.IntVar(value=1)
        ttk.Spinbox(
            naming_frame,
            from_=1,
            to=999,
            textvariable=self.start_number_var,
            width=10
        ).grid(row=2, column=1, sticky="w", padx=5, pady=2)

        naming_frame.columnconfigure(1, weight=1)

        # File List Section
        list_frame = ttk.LabelFrame(self, text="Files to Rename", padding=10)
        list_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=10, pady=5)

        # Listbox with scrollbar
        list_inner_frame = ttk.Frame(list_frame)
        list_inner_frame.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_inner_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            list_inner_frame,
            yscrollcommand=scrollbar.set,
            height=10,
            selectmode=tk.EXTENDED
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # List control buttons
        list_buttons_frame = ttk.Frame(list_frame)
        list_buttons_frame.grid(row=0, column=1, sticky="ns", padx=5)

        ttk.Button(list_buttons_frame, text="Add Files", command=self.add_files, width=12).pack(pady=2)
        ttk.Button(list_buttons_frame, text="Remove", command=self.remove_files, width=12).pack(pady=2)
        ttk.Button(list_buttons_frame, text="Clear All", command=self.clear_files, width=12).pack(pady=2)
        ttk.Separator(list_buttons_frame, orient="horizontal").pack(fill="x", pady=5)
        ttk.Button(list_buttons_frame, text="Move Up", command=self.move_up, width=12).pack(pady=2)
        ttk.Button(list_buttons_frame, text="Move Down", command=self.move_down, width=12).pack(pady=2)
        ttk.Button(list_buttons_frame, text="Move to Top", command=self.move_to_top, width=12).pack(pady=2)
        ttk.Button(list_buttons_frame, text="Move to Bottom", command=self.move_to_bottom, width=12).pack(pady=2)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Progress Section
        progress_frame = ttk.LabelFrame(self, text="Progress", padding=10)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.status_var).grid(
            row=1, column=0, sticky="w", padx=5, pady=2
        )

        progress_frame.columnconfigure(0, weight=1)

        # Control Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)

        self.start_button = ttk.Button(
            button_frame,
            text="Start",
            command=self.start_processing,
            width=15
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = ttk.Button(
            button_frame,
            text="Pause",
            command=self.pause_processing,
            width=15,
            state="disabled"
        )
        self.pause_button.grid(row=0, column=1, padx=5)

        self.stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self.stop_processing,
            width=15,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=2, padx=5)

        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

    def browse_input_folder(self):
        """Browse for input folder."""
        foldername = filedialog.askdirectory(title="Select Input Folder")
        if foldername:
            self.input_path_var.set(foldername)

    def browse_output_folder(self):
        """Browse for output folder."""
        foldername = filedialog.askdirectory(title="Select Output Folder")
        if foldername:
            self.output_path_var.set(foldername)

    def load_files(self):
        """Load all files from input folder."""
        input_path = self.input_path_var.get().strip()
        if not input_path:
            messagebox.showerror("Error", "Please specify an input folder")
            return

        if not os.path.exists(input_path):
            messagebox.showerror("Error", "Input folder does not exist")
            return

        # Get all files from folder
        files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if os.path.isfile(os.path.join(input_path, f))
        ]

        if not files:
            messagebox.showinfo("Info", "No files found in the selected folder")
            return

        # Add to file list
        self.file_list.extend(files)
        self._update_listbox()
        self.status_var.set(f"Loaded {len(files)} files")

    def add_files(self):
        """Add files manually."""
        filenames = filedialog.askopenfilenames(title="Select Files to Rename")
        if filenames:
            self.file_list.extend(filenames)
            self._update_listbox()
            self.status_var.set(f"Added {len(filenames)} files")

    def remove_files(self):
        """Remove selected files from list."""
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            return

        # Remove in reverse order to maintain indices
        for idx in reversed(selected_indices):
            del self.file_list[idx]

        self._update_listbox()
        self.status_var.set(f"Removed {len(selected_indices)} files")

    def clear_files(self):
        """Clear all files from list."""
        self.file_list.clear()
        self._update_listbox()
        self.status_var.set("Cleared all files")

    def move_up(self):
        """Move selected file up in the list."""
        selected_indices = self.file_listbox.curselection()
        if not selected_indices or selected_indices[0] == 0:
            return

        for idx in selected_indices:
            self.file_list[idx], self.file_list[idx - 1] = \
                self.file_list[idx - 1], self.file_list[idx]

        self._update_listbox()
        # Reselect moved items
        for idx in selected_indices:
            self.file_listbox.selection_set(idx - 1)

    def move_down(self):
        """Move selected file down in the list."""
        selected_indices = self.file_listbox.curselection()
        if not selected_indices or selected_indices[-1] == len(self.file_list) - 1:
            return

        for idx in reversed(selected_indices):
            self.file_list[idx], self.file_list[idx + 1] = \
                self.file_list[idx + 1], self.file_list[idx]

        self._update_listbox()
        # Reselect moved items
        for idx in selected_indices:
            self.file_listbox.selection_set(idx + 1)

    def move_to_top(self):
        """Move selected file to top of the list."""
        selected_indices = list(self.file_listbox.curselection())
        if not selected_indices or selected_indices[0] == 0:
            return

        selected_files = [self.file_list[idx] for idx in selected_indices]
        for idx in reversed(selected_indices):
            del self.file_list[idx]

        self.file_list = selected_files + self.file_list

        self._update_listbox()
        # Reselect moved items
        for idx in range(len(selected_files)):
            self.file_listbox.selection_set(idx)

    def move_to_bottom(self):
        """Move selected file to bottom of the list."""
        selected_indices = list(self.file_listbox.curselection())
        if not selected_indices or selected_indices[-1] == len(self.file_list) - 1:
            return

        selected_files = [self.file_list[idx] for idx in selected_indices]
        for idx in reversed(selected_indices):
            del self.file_list[idx]

        self.file_list.extend(selected_files)

        self._update_listbox()
        # Reselect moved items
        start_idx = len(self.file_list) - len(selected_files)
        for idx in range(start_idx, len(self.file_list)):
            self.file_listbox.selection_set(idx)

    def _update_listbox(self):
        """Update the listbox display."""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.file_list:
            self.file_listbox.insert(tk.END, Path(file_path).name)

    def start_processing(self):
        """Start the renaming process."""
        if not self.file_list:
            messagebox.showerror("Error", "No files to rename")
            return

        output_path = self.output_path_var.get().strip()
        if not output_path:
            messagebox.showerror("Error", "Please specify an output folder")
            return

        # Get prefix (custom or predefined)
        custom_prefix = self.custom_prefix_var.get().strip()
        prefix = custom_prefix if custom_prefix else self.prefix_combo.get()

        if not prefix:
            messagebox.showerror("Error", "Please specify a prefix")
            return

        # Update button states
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.stop_button.config(state="normal")

        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting...")

        # Start processing in background thread
        self.processing_thread = threading.Thread(target=self._process, daemon=True)
        self.processing_thread.start()

    def _process(self):
        """Background processing method."""
        try:
            output_path = self.output_path_var.get().strip()
            custom_prefix = self.custom_prefix_var.get().strip()
            prefix = custom_prefix if custom_prefix else self.prefix_combo.get()
            suffix_type_str = self.suffix_type_var.get()
            start_number = self.start_number_var.get()

            # Convert suffix type string to enum
            suffix_type = SuffixType(suffix_type_str)

            # Perform renaming
            results = self.renamer.rename_files(
                self.file_list,
                output_path,
                prefix,
                suffix_type,
                start_number,
                progress_callback=self._update_progress
            )

            if not self.renamer.is_stopped:
                messagebox.showinfo(
                    "Complete",
                    f"Successfully renamed {len(results)} files"
                )

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self._update_progress(0, f"Error: {str(e)}")

        finally:
            # Reset button states
            self.start_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")
            if not self.renamer.is_stopped:
                self.pause_button.config(text="Pause")

    def _update_progress(self, percent: int, message: str):
        """Update progress bar and status message."""
        self.progress_var.set(percent)
        self.status_var.set(message)

    def pause_processing(self):
        """Pause or resume the processing."""
        if self.renamer.is_paused:
            self.renamer.resume()
            self.pause_button.config(text="Pause")
            self.status_var.set("Resumed...")
        else:
            self.renamer.pause()
            self.pause_button.config(text="Resume")
            self.status_var.set("Paused")

    def stop_processing(self):
        """Stop the processing."""
        self.renamer.stop()
        self.status_var.set("Stopping...")
        self.pause_button.config(state="disabled")
        self.stop_button.config(state="disabled")


class MainApplication(tk.Tk):
    """Main application window."""

    def __init__(self):
        """Initialize the main application."""
        super().__init__()

        self.title("Word File Splitter & Renamer")
        self.geometry("800x700")

        # Create notebook (tabbed interface)
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        splitter_tab = SplitterTab(notebook)
        renamer_tab = RenamerTab(notebook)

        notebook.add(splitter_tab, text="Word Splitter")
        notebook.add(renamer_tab, text="File Renamer")

        # Center window
        self.center_window()

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')


def main():
    """Main entry point."""
    app = MainApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
