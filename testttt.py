"""from fuzzywuzzy import fuzz
def jaccard_similarity(text1, text2):
    # Split the texts into sets of words
    words_text1 = set(text1.lower().split())
    words_text2 = set(text2.lower().split())

    # Calculate the intersection and union of the two sets
    intersection = words_text1.intersection(words_text2)
    union = words_text1.union(words_text2)

    # Calculate the Jaccard similarity index
    similarity = len(intersection) / len(union)

    return similarity
# Check two texts are similar or not
text1 = "Die durch gegenwärtigen Bund vereinigten Völkerschaften der zwei und zwanzig souveränen Kantone, als: Zürich, Bern, Luzern, Ury, Schwyz, Unterwalden (ob und nid dem Wald), Glarus, Zug, Freyburg, Solothurn"
text2 = "Die durch gegenwärtigen Bund vereinigten Völkerschaften der zwei und zwanzig souveränen kanten, als: Zürich, Bern, Luzern, Neÿ, Schwyz, Unterwaldere (ob und indem Wals), Glarus, Zug, Freijburg, Holothurn"
text3 = "Die durch gegenwärtigen Bund vereinigten Völkerschaften der zwei und zwanzig souverainen Kantone, als: Zürich, Bern, Luzern, Uri, Schwyz, Unterwalden (ob und nid dem Wald), Glaris, Zug, Freiburg, Solothurn,"
text4 = "Die durch gegenwärtigen Bund vereinigten Völkerschaften der zwei und zwanzig souveränen Kantone, als: Zürich, Bern, Luzern, Uri, Schwyz, Unterwalden (ob und nid dem Walde), Glarus, Zug, Freiburg, Solothurn,"
text5 = "Die durch gegenwärtigen Bund vereinigten Völkerschaften der zwei und zwanzig souveränen kanten, als: Zürich, Bern, Luzern, Neÿ, Schwyz, Unterwaldere (ob und indem Wals), Glarus, Zug, Freijburg, Holothurn"
text6 = "Die durch gegenwärtigen Bund vereinigten Völkerschaften der zwei und zwanzig souveränen Kantone: Zürich, Bern, Luzern, Uri, Schwyz, Unterwalden (ob- und nid dem Wald), St. Gallen, Zug, Freiburg, Solothurn,"
similarity_ratio = fuzz.ratio(text1, text4)
# Display the similarity score
print(f"Similarity between the texts: {similarity_ratio}%")
# Check two texts are similar or not using Jaccard similarity
result = jaccard_similarity(text1, text4)
print(f"Jaccard similarity index: {result}")"""

import json


def reformat_data(data):
    reformatted_data = []
    for document in data:
        for doc_id, pages in document.items():
            new_doc = {"id": doc_id, "pages": []}
            for page in pages:
                for page_key, page_data in page.items():
                    page_number = page_key.split('/')[-1]
                    page_data['page_number'] = page_number
                    new_doc['pages'].append(page_data)
            reformatted_data.append(new_doc)
    return reformatted_data

# Reformat the data
with open('pk_Wh.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

formatted_data = reformat_data(data)

with open('pk_Wh_formatted.json', 'w', encoding='utf-8') as file:
    json.dump(formatted_data, file, indent=4)

