## Model used : all-mpnet-base-v2

This is a sentence-transformers model: It maps sentences & paragraphs to a 768 dimensional dense vector space and can be used for tasks like clustering or semantic search.

## What's a SentenceTransformers ?

SentenceTransformers is a Python framework for state-of-the-art sentence, text and image embeddings.
You can use this framework to compute sentence / text embeddings for more than 100 languages. 

These embeddings can then be compared e.g. with cosine-similarity to find sentences with a similar meaning. This can be useful for semantic textual similarity, semantic search, or paraphrase mining.

## Downloading models
 
Git LFS (Large File Storage) should be installed on your system :

```
sudo apt-get install git-lfs
```
Next you should create an account in https://huggingface.co/

Then generate an access token in Setttings page https://huggingface.co/settings/tokens

This token will enable you to download the Model locally.

Now clone the models locally by running:

```
git clone git@hf.co:sentence-transformers/all-mpnet-base-v2 Model/all-mpnet-base-v2
```
then hit :

```
git remote set-url origin https://<user_name>:<token>@huggingface.co/sentence-transformers/all-mpnet-base-v2
git pull origin
```

After this pull large files needed to run the model:

```
git lfs install
git lfs pull
```

## Need more info

SBERT.net ==> https://www.sbert.net/

Embeddings Model repo ==> https://huggingface.co/sentence-transformers/all-mpnet-base-v2?library=transformers