from __future__ import annotations

import re


class TextTruncate:
    """Flexible text truncation with intelligent boundary detection.

    Provides sophisticated text truncation methods that can truncate from the beginning, end, or
    middle of text while respecting word and sentence boundaries. Offers both strict character-count
    truncation and intelligent truncation that preserves readability by avoiding mid-word cuts and
    handling punctuation gracefully.
    """

    @staticmethod
    def truncate(
        text: str,
        chars: int = 200,
        from_middle: bool = False,
        strict: bool = False,
        strip_punctuation: bool = True,
        strip_line_breaks: bool = True,
        condensed: bool = False,
        limit_length: bool = False,
        max_chars: int = 4096,
    ) -> str:
        """Truncate text to a specified length.

        In strict mode, truncation strictly adheres to the character limit. In non-strict mode, the
        method seeks to end on full sentences or words. When truncating from the middle, text is cut
        from the center to preserve the start and end of the text, adding an ellipsis in the middle.

        Args:
            text: The text to be truncated.
            chars: The maximum number of characters the truncated text should contain. Uses default
                   settings value if not specified.
            from_middle: Whether to truncate the text from its middle. Defaults to False.
            strict: When True, truncation will strictly adhere to the 'chars' limit, possibly
                    cutting words or sentences. Defaults to False.
            strip_punctuation: If True, the method ensures the truncated text does not end with
                               punctuation, improving readability. Defaults to True.
            strip_line_breaks: If True, the method ensures the truncated text does not contain line
                               breaks. Defaults to True.
            condensed: Switches to a more condensed ellipses when using from_middle, so ' [...] '
                       becomes '...'. This is better for logging, as one example. Defaults to False.
            limit_length: If True, the method ensures the truncated text does not exceed the
                          specified character limit. Defaults to False.
            max_chars: The maximum number of characters the truncated text should contain. Uses
                       default settings value if not specified.

        Returns:
            The truncated text, potentially modified to meet the specified conditions.
        """
        if len(text) <= chars:  # Return as-is if it's already under the desired length
            return text

        if strict:  # In strict mode, truncate the text exactly to the specified limit
            truncated_text = TextTruncate._truncate_strict(text, chars, from_middle)
        else:  # In non-strict mode, truncate at sentence or word boundaries
            truncated_text = TextTruncate._truncate_at_boundaries(
                text, chars, from_middle, strip_punctuation, condensed
            )

        # Ensure final length does not exceed 4096 characters
        if limit_length and len(truncated_text) > max_chars:
            truncated_text = f"{truncated_text[:max_chars]}..."

        if strip_line_breaks:  # Remove line breaks if specified
            truncated_text = truncated_text.replace("\n", " ")

        return truncated_text

    @staticmethod
    def _truncate_strict(text: str, chars: int, from_middle: bool) -> str:
        return (
            f"{text[: chars // 2].strip()}...{text[-chars // 2 :].strip()}"
            if from_middle
            else f"{text[:chars].strip()}..."
        )

    @staticmethod
    def _truncate_at_boundaries(
        text: str, chars: int, from_middle: bool, strip: bool, condensed: bool
    ) -> str:
        # Truncate from the middle or end, attempting to preserve whole sentences or words
        if from_middle:
            truncated_text = TextTruncate._truncate_from_middle(chars, text, condensed)
        else:  # For standard (non-middle) truncation, find the optimal single truncation point
            split_index = TextTruncate._find_index(text, chars)
            truncated_text = f"{text[:split_index].rstrip()}..."

        # Clean up and ensure it doesn't end with punctuation
        truncated_text = re.sub(r"\s+", " ", truncated_text)
        if strip and not from_middle and truncated_text[-1] in ".?!":
            truncated_text = f"{truncated_text[:-1]}..."

        # Ensure there are never more than three dots at the end, and replace with ellipsis
        while truncated_text.endswith("...."):
            truncated_text = truncated_text[:-1]
        if truncated_text.endswith("..."):
            truncated_text = f"{truncated_text[:-3]}..."

        return truncated_text

    @staticmethod
    def _truncate_from_middle(chars: int, text: str, condensed: bool) -> str:
        separator = "..." if condensed else " [...] "
        first_half_limit = chars // 2  # Calculate limit for first and second half
        second_half_limit = chars - first_half_limit
        # Find truncation points for both halves and combine with an ellipsis in between
        first_half_index = TextTruncate._find_index(text, first_half_limit)
        second_half_index = len(text) - TextTruncate._find_index(text[::-1], second_half_limit)
        result = f"{text[:first_half_index]}{separator}{text[second_half_index:]}"

        return result.rstrip() if result.endswith(tuple(".?!")) else f"{result.rstrip()}..."

    @staticmethod
    def _find_index(text: str, limit: int) -> int:
        # Search for sentence-ending punctuation to end on a complete sentence if possible
        for punct in [". ", "? ", "! "]:
            index = text.rfind(punct, 0, limit)
            if index != -1:
                return index + len(punct)  # Return the index just after the punctuation
        # If no suitable punctuation is found, fall back to the last space within the limit
        space_index = text.rfind(" ", 0, limit)
        return space_index if space_index != -1 else limit  # Use limit if no space is found
