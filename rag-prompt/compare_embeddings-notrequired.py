from langchain.embeddings import OpenAIEmbeddings
from langchain.evaluation import load_evaluator


def main():
    # Get embedding for a word.
    embedding_function = OpenAIEmbeddings()
    vector = embedding_function.embed_query("apple")
    print("Vector for 'apple': {vector}")
    print("Vector length: {len(vector)}")

    # Compare vector of two words
    evaluator = load_evaluator("pairwise_embedding_distance")
    words = ("apple", "iphone")
    x = evaluator.evaluate_string_pairs(prediction=words[0], prediction_b=words[1])
    print("Comparing ({words[0]}, {words[1]}): {x}")


if __name__ == "__main__":
    main()
