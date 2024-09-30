import re
import time


def response_generator(response):
    response = "Assistant : " + response
    lines = response.splitlines(True)  # Preserve line breaks
    table_pattern = re.compile(r"^\|.*\|$")  # Pattern to detect Markdown table lines

    buffer = []
    # in_table = False

    for line in lines:
        # Check if the line starts with '|' and ends with '|'
        if table_pattern.match(line):
            # If a table line is detected, add to buffer
            buffer.append(line)
            # in_table = True
        else:
            if not table_pattern.match(line) and buffer:
                # If the end of the table is reached, emit the complete table followed by a line break
                yield "".join(buffer) + "\n"
                buffer = []
                # in_table = False

            # Emit words line by line for normal text
            words = line.split()
            for i, word in enumerate(words):
                yield word + (" " if i < len(words) - 1 else "\n")
                time.sleep(0.05)

    # Emit any remaining content in the buffer (last table)
    if buffer:
        yield "".join(buffer)
