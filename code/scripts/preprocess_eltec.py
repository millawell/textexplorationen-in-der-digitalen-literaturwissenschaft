import json

from pathlib import Path
from zipfile import ZipFile
from zipfile import Path as zPath
import pandas as pd
from tqdm import tqdm
from lxml import etree

from standoffconverter import Standoff, View


def xml_to_plain(xml_str):
    namespaces = {
        "tei": "http://www.tei-c.org/ns/1.0",
    }

    tree = etree.fromstring(xml_str)
    so = Standoff(tree, namespaces=namespaces)

    view = View(so)

    linebreak_tag = '{http://www.tei-c.org/ns/1.0}lb'

    for _, row in view.view.iterrows():
            if row.el is not None and row.el.tag == linebreak_tag:
                if 'break' in row.el.attrib and row.el.attrib['break'] == 'no':
                    view.view.loc[row.name, 'char'] = ''
                else:
                    view.view.loc[row.name, 'char'] = ' '
    text = (
        view
        .exclude_outside("{http://www.tei-c.org/ns/1.0}body")
        .remove_comments()
        .shrink_whitespace()
        .get_plain()
    ).strip()

    return text


def main():
    raw_data_path = Path("raw_data")
    preprocessed_data_fn = Path("processed_data") / "eltec.jsonl"

    in_data_filename = raw_data_path / "ELTeC-deu-1.0.0-data.zip"
    in_meta_data_filename = raw_data_path / "ELTeC-deu-1.0.0-metadata.csv"

    metadata = pd.read_csv(in_meta_data_filename)
    metadata.set_index("id", inplace=True)

    suffix = ".xml"
    with open(preprocessed_data_fn, "w") as out_file:
        with ZipFile(in_data_filename) as archive:
            l1_path = zPath(archive, at="ELTeC-deu-1.0.0/level1/")
            for zfn in tqdm(l1_path.iterdir(), desc="parse level1"):

                if zfn.is_file() and zfn.name.endswith(suffix):

                    stem = zfn.name.split(".xml")

                    plain = xml_to_plain(zfn.read_bytes())

                    out_obj = {"text": plain}
                    out_obj.update(metadata.loc[stem[0]].to_dict())

                    out_file.write(json.dumps(out_obj) + "\n")


if __name__ == "__main__":
    main()
