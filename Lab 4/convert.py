import sys
import json

def convert_notebook_to_python(input_filename):
    with open(input_filename, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    converted_cells = []

    exercise_count = sum(
        1 for cell in filter(
            lambda c: c['cell_type'] == 'markdown' and '# Ćwiczenie' in c['source'][0].strip(),
            notebook.get('cells', [])
        )
    )

    for cell in notebook.get('cells', []):
        if cell['cell_type'] == 'markdown':
            markdown_content = ''.join(cell['source']).strip()

            if '\n' not in markdown_content:
                markdown_text = f"# {markdown_content}"
                converted_cells.append(markdown_text)
            else:
                markdown_text = "\n".join(f"# {line.strip()}" for line in cell['source'] if line.strip())
                if markdown_text.strip():
                    converted_cells.append(markdown_text)

        elif cell['cell_type'] == 'code':
            code_text = "".join(cell['source']).strip()
            converted_cells.append(code_text)

    output_filename = input_filename.replace('.ipynb', '.py')

    with open(output_filename, 'w', encoding='utf-8') as output_file:
        output_file.write("\n\n".join(converted_cells) + "\n")

    print(f"Liczba ćwiczeń: {exercise_count}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python convert_notebook_to_python.py <filename.ipynb>")
    else:
        convert_notebook_to_python(sys.argv[1])
