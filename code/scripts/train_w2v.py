import json

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from spacy.lang.de import German
from gensim.models import Word2Vec


def main():

    nlp = German()
    nlp.add_pipe("sentencizer")

    preprocessed_data_fn = Path("processed_data") / "eltec.jsonl"
    
    sentences = []
    with open(preprocessed_data_fn, "r") as in_file:
        for line in tqdm(in_file, desc="load sentences"):
            data = json.loads(line)
            text = data["text"]
            if len(text) >= nlp.max_length:
                nlp.max_length = len(text)+1
            for sent in nlp(text).sents:
                sentences.append([])
                for token in sent:
                    sentences[-1].append(token.text)

        model = Word2Vec(
            sentences=sentences,
            vector_size=100,
            window=5,
            min_count=1,
            workers=4
        )

        model.train(
            sentences,
            total_examples=len(sentences),
            epochs=2
        )

        wv = model.wv

        vocab = wv.index_to_key
        vocab = sorted(vocab)

        vecs = [wv[it] for it in vocab]
        
        df = pd.DataFrame(data=vecs, index=vocab)


            

if __name__ == "__main__":
    main()
