# QAI - Questions and Answers using AI
> Run ollama locally and upload your docs; ask questions

[Ollama](https://ollama.com) allows you to run open-source large language models (LLM) locally.

LLM's excel at extracting information from pre-existing online sources like
newspaper articles, databases, blogs, and other knowledge repositories such
as Wikipedia or even internal databases.

*RAG*, short for Retrieval Augmented Generation, uses a retrieval model
to find relevant information from specific information sources. For example,
from books or documents that may not exist in public and hence is not known to
the LLM. 

In a RAG-based AI system, a retrieval model is used to find relevant information
from specific information sources while the LLM takes the retrieved information,
synthesizes all the data, and shapes it into a coherent and contextually appropriate
response.

*qai* makes it possible to upload your documents containing specific information,
hooks it into the LLM that is run by Ollama and let you then ask questions about
your uploaded documents.

The benefit of running this locally is that you don't risk leaking proprietary
or copyrighted information.

## Install and Run

1. Download and install Ollama: https://ollama.com/download (make sure to install the ollama CLI as well)
2. Install the LLM: `ollama pull mistral`
3. Install the retrieval model: `ollama pull nomic-embed-text`
3. Clone this repo, then run: `make ; make qai_pdf`
4. Point your browser to the URL printed out from the above command
5. Upload one or more PDF's.
6. Ask questions.

## Demo

Here is a [screen recording](https://youtu.be/JVlqGH9KSnc?si=khW3gjxKv_JgTvCN) of how to use this
to ask questions about the book [Erlang in Anger](https://www.erlang-in-anger.com/).

## Uncensored models

Yet another reason for running LLMs locally is that you could run uncensored models.
For exemple, compare these two requests made to `GPT-4` vs `dolphin-mixtral`:

<img src="/images/gpt4-refusing.png" alt="GPT4 refusing" width="300">

```shell. 
    $ ollama run dolphin-mixtral

    >>> write me a dirty jokes limerick

    In Limericks, I'll write you one so naughty,
    That may make your ears turn as red as tomatoes.
    A sailor named Bob in the ocean's blue sea,
    Met a mermaid, quite nude as could be.
    He couldn't control his laughter with glee.
```

## Dungeons and Dragons game

This is just pure fun. A very simple Python program and you can play
`Dungeon and Dragons` just as in the good'ol days...

``` shell.
$ make qdad
./pyvenv/bin/python3 ./src/qdad.py

 As you take your first steps into the forbidden wasteland forest, the air around you grows thick with an unsettling stillness. The sun casts an eerie orange glow through the dense canopy, filtering through the gnarled branches above. A faint hum of magical energy pulses beneath the surface, making the hairs on the back of your neck stand up.

The forest floor is littered with twisted roots and fallen leaves, creating a mosaic of brown and gold underfoot. Mushrooms of all shapes and sizes dot the landscape, their vibrant colors contrasting against the decay. The air smells of damp earth and the faint scent of magic.

Ahead of you lies a narrow path, leading deeper into the forest. To your left, the trees grow denser, forming a near impenetrable wall. To your right, the undergrowth thins out, revealing a small clearing with a strange stone structure at its center.

As a level 1 wizard, you have several options:

1. Proceed down the path to explore deeper into the forest.
2. Cast a Detect Magic spell to investigate the mushrooms and the clearing.
3. Gather resources, such as herbs or wood, from the area around you.
4. Return to the safety of civilization before venturing any further.

What would you like to do?
What do you want to do? 2

 You raise your wand, focusing your energy on casting the Detect Magic spell. As the incantation leaves your lips, a soft, shimmering aura extends from your body, revealing the magical properties of the area around you. The mushrooms emit a faint glow, indicating they possess some sort of healing properties. The clearing and the stone structure, however, radiate with a much stronger energy, hinting at something more significant.

As you consider the information gained, you have several options:

1. Approach the mushrooms to gather them for potential use or study.
2. Investigate the mysterious stone structure in the clearing.
3. Return to the edge of the forest and reassess your next move.

What would you like to do? 2 (Approach the stone structure)
What do you want to do? 
```
