# RAGnarok

RAGnarok offers an automated testing and evaluation of LLM chatbots using Retrieval-Augmented Generation (RAG). Think Selenium, but for LLM finetuning.

Project submitted for [Encode AI Hackathon, 2024](https://www.encode.club/ai-hackathon)

Authored by:
[Vincent Hao](https://github.com/VinceHow),
[Billy Zhao](https://github.com/billlyzhaoyh),
[Andrew Tan](https://github.com/twinbarrel)

## Summary

It is easy to spin up a RAG-based application as a proof-of-concept, but there is often a long tail of edge cases that fail, and need to be solved before the application is production ready. In addition, these edge cases need to be manually tested for each new deployment of the prompt / vector database, which becomes a huge time sink.

There is a massive opportunity for RAG-based applications - with ~$400B productivity uplift estimated to be gained from customer service operations improvements.

Against this, RAGnarok provides an automated testing and evaluation framework that serves two functions:

1. Generates test cases against 'jobs to be done' defined by the business user
2. Evaluates and scores the model's performance against these test cases through a three-round conversation

This provides a clearer, robust view of model performance, and allows faster improvement and iteration of the model, driving better user experience.

This demo uses a fictional gourmet snack website ("snack52"), and is composed of the following components:
- **Knowledge source**: AI-generated landing page, FAQs and product databases
- **Front-end**: Streamlit, deployed on Heroku
- **Back-end**: Pinecone, RAGA
- **LLM**: Stability AI

## Overview

[To come - Screenshots from demo]

The evaluation is based off of four key metrics, leveraging the RAGA framework:

1. Faithfulness - Measures the factual consistency of the answer to the context based on the question.
2. Context_precision - Measures how relevant the retrieved context is to the question, conveying the quality of the retrieval pipeline.
3. Answer_relevancy - Measures how relevant the answer is to the question.
4. Context_recall - Measures the retriever’s ability to retrieve all necessary information required to answer the question.