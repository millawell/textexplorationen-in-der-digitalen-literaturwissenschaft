import json

import click 

from pathlib import Path
from tqdm import tqdm

@click.command()
@click.argument('input_file')
@click.argument('output_path')
def main(input_file, output_path):
    """
    Convert a jsonl file to txt files.
    """

    output_path = Path(output_path)

    with open(input_file, 'r') as f:
        for line in tqdm(f.readlines(), total=100):
            data = json.loads(line)

            author = data['author-name'][:15].replace(",", "").replace(" ", "-")
            title = data['book-title'][:10].replace(",", "").replace(" ", "-")
            out_file_name = output_path / f"{author}_{title}.txt"
            with open(out_file_name, 'w') as out_file:
                out_file.write(data['text'])


if __name__ == "__main__":
    main()
