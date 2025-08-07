from PIL import Image, ImageDraw, ImageFont
import textwrap
class TextJustification:
    def justify_yugioh_text(self, text, max_font_size, max_width, max_height, font_path):
        """
        Justify Yu-Gi-Oh card description text to fit within specified dimensions.
        
        Args:
            text (str): The card description text to justify
            max_font_size (int): Maximum font size to try
            max_width (int): Maximum width available for text
            max_height (int): Maximum height available for text
            font_path (str): Path to the font file
        
        Returns:
            tuple: (optimal_font_size, justified_text)
                - optimal_font_size: The best font size that fits
                - justified_text: Complete justified text as a single string
        """
        
        def get_text_dimensions(text, font):
            """Get the width and height of text with given font"""
            # Create a temporary image to measure text
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # Use textlength for more accurate width measurement
            try:
                width = temp_draw.textlength(text, font=font)
            except AttributeError:
                # Fallback for older Pillow versions
                bbox = temp_draw.textbbox((0, 0), text, font=font)
                width = bbox[2] - bbox[0]
            
            # Get height using textbbox
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            height = bbox[3] - bbox[1]
            
            return width, height
        
        def justify_line(words, font, target_width):
            """Justify a line using Microsoft Word's low justification strategy with safety checks"""
            if len(words) <= 1:
                return ' '.join(words)
            
            # Calculate original line width without justification
            original_line = ' '.join(words)
            original_width = get_text_dimensions(original_line, font)[0]
            
            # Safety checks to prevent over-justification
            MIN_FILL_RATIO = 0.65  # Only justify if line is at least 65% of target width
            MIN_WORD_COUNT = 3     # Don't justify lines with less than 3 words
            MAX_SPACES_PER_GAP = 5  # Maximum spaces between words
            
            # Check if line is too short to justify
            if original_width / target_width < MIN_FILL_RATIO:
                return original_line
            
            # Check if too few words
            if len(words) < MIN_WORD_COUNT:
                return original_line
            
            # Calculate total width of words without spaces
            total_word_width = sum(get_text_dimensions(word, font)[0] for word in words)
            
            # Calculate available space for gaps with safety margin
            # safe_target_width = target_width * 0.98  # 2% safety margin
            safe_target_width = target_width
            available_space = safe_target_width - total_word_width
            gaps = len(words) - 1
            
            if gaps == 0 or available_space <= 0:
                return original_line
            
            # Microsoft Word "low" strategy: distribute space as evenly as possible
            single_space_width = get_text_dimensions(' ', font)[0]
            
            if single_space_width <= 0:
                return original_line
            
            # Calculate base spaces per gap and remainder
            total_spaces_needed = available_space / single_space_width
            base_spaces_per_gap = int(total_spaces_needed / gaps)
            extra_spaces = int(total_spaces_needed % gaps)
            
            # Ensure minimum of 1 space between words
            base_spaces_per_gap = max(1, base_spaces_per_gap)
            
            # Check if gaps would be too large
            max_spaces_in_any_gap = base_spaces_per_gap + (1 if extra_spaces > 0 else 0)
            if max_spaces_in_any_gap > MAX_SPACES_PER_GAP:
                return original_line
            
            # Build justified line with distributed spaces
            justified_words = []
            for i, word in enumerate(words):
                justified_words.append(word)
                if i < len(words) - 1:  # Don't add spaces after last word
                    # Base spaces plus one extra space for first 'extra_spaces' gaps
                    spaces_count = base_spaces_per_gap + (1 if i < extra_spaces else 0)
                    justified_words.append(' ' * spaces_count)
            
            # Final safety check: verify the justified line doesn't exceed target width
            justified_line = ''.join(justified_words)
            justified_width = get_text_dimensions(justified_line, font)[0]
            
            if justified_width > target_width:
                return original_line  # Return original if justified version is too wide
            
            return justified_line
        
        def wrap_text_to_lines(text, font, max_width):
            """Wrap text into lines that fit within max_width"""
            # Split text into paragraphs first
            paragraphs = text.split('\n')
            all_lines = []
            line_metadata = []  # Track which lines should NOT be modified
            
            for paragraph in paragraphs:
                if not paragraph.strip():
                    all_lines.append('')  # Empty line for paragraph breaks
                    line_metadata.append('empty')
                    continue
                
                # First check if entire paragraph fits in one line with safety margin
                paragraph = paragraph.strip()
                para_width = get_text_dimensions(paragraph, font)[0]
                safe_max_width = max_width
                
                if para_width <= safe_max_width:
                    # Paragraph fits on one line, add it as-is without any modifications
                    all_lines.append(paragraph)
                    line_metadata.append('original_fit')  # Mark as original paragraph that fit
                    continue
                
                # Paragraph doesn't fit, split into words and wrap
                words = paragraph.split()
                current_line = []
                
                for word in words:
                    # Test if adding this word exceeds width with safety margin
                    test_line = current_line + [word]
                    test_text = ' '.join(test_line)
                    test_width = get_text_dimensions(test_text, font)[0]
                    # safe_max_width = max_width * 0.98  # 2% safety margin
                    safe_max_width = max_width
                    
                    if test_width <= safe_max_width:
                        current_line.append(word)
                    else:
                        # Current line is full, save it and start new line
                        if current_line:
                            all_lines.append(' '.join(current_line))
                            line_metadata.append('wrapped')  # Mark as wrapped line
                        current_line = [word]
                
                # Add remaining words in current line
                if current_line:
                    all_lines.append(' '.join(current_line))
                    line_metadata.append('wrapped')  # Mark as wrapped line
            
            return all_lines, line_metadata
        
        # Try different font sizes starting from max_font_size
        for font_size in range(max_font_size, 6, -1):  # Don't go below size 6
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                # If truetype fails, try default font
                try:
                    font = ImageFont.load_default()
                except:
                    continue
            
            # Wrap text into lines
            lines, line_metadata = wrap_text_to_lines(text, font, max_width)
            
            # Calculate total height needed
            line_height = get_text_dimensions("Ay", font)[1]  # Use characters with ascenders/descenders
            total_height = len(lines) * line_height
            
            # Check if text fits within height constraint
            if total_height <= max_height:
                # Process lines based on their metadata
                justified_lines = []
                
                for i, (line, metadata) in enumerate(zip(lines, line_metadata)):
                    if metadata == 'empty':
                        # Empty line - keep as is
                        justified_lines.append(line)
                    elif metadata == 'original_fit':
                        # Original paragraph that fit - DO NOT MODIFY AT ALL
                        justified_lines.append(line)
                    elif i == len(lines) - 1:
                        # Last line - don't justify (MS Word behavior)
                        justified_lines.append(line)
                    else:
                        # Wrapped line that can be justified
                        words = line.split()
                        if len(words) > 1:
                            # Apply Microsoft Word low justification strategy
                            justified_line = justify_line(words, font, max_width)
                            justified_lines.append(justified_line)
                        else:
                            justified_lines.append(line)
                
                return font_size, '\n'.join(justified_lines)
        
        # If no font size works, return minimum size with basic wrapping
        font_size = 8
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
        
        lines, line_metadata = wrap_text_to_lines(text, font, max_width)
        return font_size, '\n'.join(lines)

    # Uncomment to test
    # test_yugioh_justify()