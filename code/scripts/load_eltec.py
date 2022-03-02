import requests

from pathlib import Path
from tqdm import tqdm


data = "https://zenodo.org/record/4662482/files/ELTeC-deu-1.0.0.zip?download=1"
meta_data  = "https://zenodo.org/record/4662482/files/metadata.csv?download=1"

def download_file(url, local_filename):

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
    
        with open(local_filename, 'wb') as f:

            pbar = tqdm(
                r.iter_content(chunk_size=8192),
                desc=f"downloading {local_filename.name}"
            )

            for chunk in pbar: 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)

    return local_filename


def main():
    raw_data_path = Path("raw_data")
    data_local_filename = raw_data_path / "ELTeC-deu-1.0.0-data.zip"
    meta_data_local_filename = raw_data_path / "ELTeC-deu-1.0.0-metadata.csv"

    download_file(data, data_local_filename)
    download_file(meta_data, meta_data_local_filename)


if __name__ == '__main__':
    main()
    