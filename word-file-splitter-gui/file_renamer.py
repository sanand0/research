"""
File Renamer Module
Handles renaming files with customizable prefixes and suffixes.
"""
import os
import shutil
from pathlib import Path
from typing import List, Callable, Optional
from enum import Enum


class SuffixType(Enum):
    """Enumeration of suffix types."""
    NUMERIC = "numeric"
    ALPHA_LOWER = "alpha_lower"
    ALPHA_UPPER = "alpha_upper"
    ROMAN_LOWER = "roman_lower"
    ROMAN_UPPER = "roman_upper"


class FileRenamer:
    """Handles renaming files with customizable prefixes and suffixes."""

    def __init__(self):
        """Initialize the FileRenamer."""
        self.is_paused = False
        self.is_stopped = False

    def pause(self):
        """Pause the renaming process."""
        self.is_paused = True

    def resume(self):
        """Resume the renaming process."""
        self.is_paused = False

    def stop(self):
        """Stop the renaming process."""
        self.is_stopped = True
        self.is_paused = False

    def reset(self):
        """Reset the state for a new operation."""
        self.is_paused = False
        self.is_stopped = False

    def rename_files(
        self,
        file_list: List[str],
        output_dir: str,
        prefix: str,
        suffix_type: SuffixType,
        start_number: int = 1,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[tuple]:
        """
        Rename files according to the specified pattern.

        Args:
            file_list: List of file paths to rename (in order)
            output_dir: Directory to save renamed files
            prefix: Prefix for renamed files (e.g., "Chapter", "Section")
            suffix_type: Type of suffix (numeric, alphabetic, roman)
            start_number: Starting number for suffix (default: 1)
            progress_callback: Optional callback function(progress_percent, message)

        Returns:
            List of tuples (original_path, new_path)

        Raises:
            FileNotFoundError: If any input file doesn't exist
            ValueError: If parameters are invalid
        """
        self.reset()

        if not file_list:
            raise ValueError("File list cannot be empty")

        if not prefix:
            raise ValueError("Prefix cannot be empty")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        renamed_files = []
        total_files = len(file_list)

        for idx, file_path in enumerate(file_list):
            if self.is_stopped:
                if progress_callback:
                    progress_callback(100, "Renaming stopped by user")
                break

            while self.is_paused:
                if self.is_stopped:
                    break
                continue

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Generate suffix
            suffix_number = start_number + idx
            suffix = self._generate_suffix(suffix_number, suffix_type)

            # Get file extension
            ext = Path(file_path).suffix

            # Create new filename
            new_filename = f"{prefix} {suffix}{ext}"
            new_path = os.path.join(output_dir, new_filename)

            # Copy file with new name
            shutil.copy2(file_path, new_path)
            renamed_files.append((file_path, new_path))

            if progress_callback:
                progress = int(((idx + 1) / total_files) * 100)
                progress_callback(
                    progress,
                    f"Renamed: {Path(file_path).name} → {new_filename}"
                )

        if progress_callback and not self.is_stopped:
            progress_callback(100, f"Successfully renamed {len(renamed_files)} files")

        return renamed_files

    def _generate_suffix(self, number: int, suffix_type: SuffixType) -> str:
        """
        Generate suffix based on number and type.

        Args:
            number: The number to convert
            suffix_type: Type of suffix to generate

        Returns:
            The generated suffix string
        """
        if suffix_type == SuffixType.NUMERIC:
            return str(number)

        elif suffix_type == SuffixType.ALPHA_LOWER:
            return self._number_to_alpha(number, uppercase=False)

        elif suffix_type == SuffixType.ALPHA_UPPER:
            return self._number_to_alpha(number, uppercase=True)

        elif suffix_type == SuffixType.ROMAN_LOWER:
            return self._number_to_roman(number).lower()

        elif suffix_type == SuffixType.ROMAN_UPPER:
            return self._number_to_roman(number)

        else:
            raise ValueError(f"Unknown suffix type: {suffix_type}")

    def _number_to_alpha(self, number: int, uppercase: bool = False) -> str:
        """
        Convert a number to alphabetic representation (a, b, c, ... z, aa, ab, ...).

        Args:
            number: The number to convert (1-based)
            uppercase: Whether to use uppercase letters

        Returns:
            Alphabetic representation
        """
        result = ""
        number = number - 1  # Convert to 0-based

        while True:
            result = chr(ord('A' if uppercase else 'a') + (number % 26)) + result
            number = number // 26
            if number == 0:
                break
            number -= 1  # Adjust for aa, ab, etc.

        return result

    def _number_to_roman(self, number: int) -> str:
        """
        Convert a number to Roman numeral representation.

        Args:
            number: The number to convert (1-3999)

        Returns:
            Roman numeral representation

        Raises:
            ValueError: If number is out of valid range
        """
        if number < 1 or number > 3999:
            raise ValueError("Roman numerals only support numbers 1-3999")

        values = [
            (1000, 'M'),
            (900, 'CM'),
            (500, 'D'),
            (400, 'CD'),
            (100, 'C'),
            (90, 'XC'),
            (50, 'L'),
            (40, 'XL'),
            (10, 'X'),
            (9, 'IX'),
            (5, 'V'),
            (4, 'IV'),
            (1, 'I')
        ]

        result = ""
        for value, numeral in values:
            count = number // value
            if count:
                result += numeral * count
                number -= value * count

        return result


# Predefined prefix options
PREDEFINED_PREFIXES = [
    "Chapter",
    "Section",
    "Part",
    "Figure",
    "Table",
    "Equation"
]
