This phase has two important parts:

1. Creating an inverted index on normalized contents and storing the frequency of the words so we can rank documents based on how much they relate to our query.

2. Creating a champion list, which is a list that contains the most relevant documents for each word. By doing this, we can speed up our search because fewer related documents will be pruned. 
