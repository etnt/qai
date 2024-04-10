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

Note: Per default we are using the `mistral` LLM. To try out
another model you can do:

```shell
ollama pull starling-lm
env USE_MODEL="starling-lm" make qdad
```

## Demo

Here is a [screen recording](https://youtu.be/JVlqGH9KSnc?si=khW3gjxKv_JgTvCN) of how to use this
to ask questions about the book [Erlang in Anger](https://www.erlang-in-anger.com/).

## Analyse a picture

There is a picture of an Elephant in the data directory. Try it out like this:

1. ollama pull llava
2. make qpic

Add your own pictures and modify the qpic program...

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

## Using Agents

By designing the prompt in a clever way we can make the LLM ask
for help from external tools; such a system is called an LLM agent.
See [also](https://huggingface.co/blog/open-source-llms-as-agents)

Here we have made it possible for the LLM to request help with
doing a search query and then returning some relevant content
that the LLM can make use of to formulate an answer.

```shell
#
# Let's ask a question that our LLM doesn't know the answer to.
#
$ ollama run mistral
>>> Who won the Nobel prize in Physics 2023? Tell me something about the motiviation for getting the prize.
 I apologize for any confusion, but as of now, the Nobel Prizes for 2023 have not been announced yet. The Nobel Prizes are awarded annually, and the winners are typically announced between October
and December. Therefore, it is currently impossible to provide information about who won the Nobel Prize in Physics 2023 or the motivation behind their work. I suggest checking back later for 
updates.

#
# Now as the same question when our LLM can take help from an external Agent.
#
$ make qagent
./pyvenv/bin/python3 ./src/qagent.py
Enter a question: Who won the Nobel prize in Physics 2023? Tell me something about the motiviation for getting the prize.
Answer:
 According to my search results, Pierre Agostini from The Ohio
State University, Ferenc Krausz from Max Planck Institute of
Quantum Optics, and Anne L'Huillier from Lund University won
the Nobel Prize in Physics 2023. They were awarded for
"experimental methods that generate attosecond pulses of light
for the study of electron dynamics in matter."

#
# Turn on some verbose output to see what it does
#
$ env QAI_VERBOSE=true make qagent
./pyvenv/bin/python3 ./src/qagent.py
Enter a question: Who won the Nobel prize in Medicine 2023? Tell me about the motivation behind the prize.
<info> Extracted JSON object:  {'action': 'search', 'action_input': {'query': 'Nobel prize in Medicine 2023 winner'}}
<info> Performing Google search for: Nobel prize in Medicine 2023 winner
<info> (0) Extracting content from: https://www.nobelprize.org/prizes/medicine/2023/press-release/
<info> (1) Extracting content from: https://www.nobelprize.org/prizes/medicine/2023/kariko/facts/
<info> (2) Extracting content from: https://en.wikipedia.org/wiki/2023_Nobel_Prize_in_Physiology_or_Medicine
<info> (3) Extracting content from: https://www.nobelprize.org/prizes/medicine/
<info> (4) Extracting content from: https://ki.se/en/about/the-nobel-prize-in-physiology-or-medicine
<info> (5) Extracting content from: https://www.nobelprize.org/prizes/medicine/2023/advanced-information/
Answer:
 Katalin Karikó and Drew Weissman won the Nobel Prize in
Physiology or Medicine 2023 for their discoveries concerning
nucleoside base modifications that enabled the development of
effective mRNA vaccines against COVID-19. These discoveries
were critical during the pandemic that began in early 2020.
```


## Dungeons and Dragons game

This is just pure fun. A very simple Python program and you can play
`Dungeon and Dragons` just as in the good'ol days...

Note: Per default we are using the `mistral` LLM. To try out
another model you can do:

```shell
ollama pull starling-lm
env USE_MODEL="starling-lm" make qdad
```

``` shell.
$ make qdad 
./pyvenv/bin/python3 ./src/qdad.py 
 
Greetings, brave adventurer! I see you're standing at the 
entrance of an ancient tomb, shrouded in the mystical gloom of 
a moonless night. The air is heavy with the scent of damp 
earth and decaying foliage. Before you lies a massive stone 
door, adorned with intricate carvings that depict scenes of 
fierce battles and mythical creatures. 
 
As you take a moment to survey your surroundings, I present 
you with the following options: 
 
1) Attempt to force open the stone door with all your might. 
2) Search for any hidden mechanisms or clues that may reveal 
the entrance's secret. 
3) Call upon your deity for divine intervention in unlocking 
this tomb. 
4) Retreat and gather allies or resources before attempting 
entry. 
 
Which path would you like to take, valiant adventurer? 
 
>>> What do you want to do: search for hidden mechanisms 
 
As you turn your gaze from the stone door, your keen eyes scan 
the area around it. The dim light of the torches flickers 
across the surface of the tomb, revealing small cracks and 
crevices in the ancient stone. You notice a peculiar pattern 
on one side of the door - three interlocking gears that seem 
to be part of some sort of mechanism. 

You reach out to touch the carvings, feeling the rough texture
of the stone beneath your fingers. As you trace the lines of
the gears with your mind, you begin to sense a faint hum of
energy coursing through them. With a renewed sense of purpose,
you focus your attention on the mechanism.

As you continue to explore the hidden workings of the door,
the hum grows louder and more distinct. Suddenly, you hear the
sound of grating stone as the gears shift and realign. The
heavy stone door begins to creak open, revealing a dark and
narrow passageway beyond. The air inside is stale and thick
with dust, but there's a faint glimmer of light that beckons
you forward.

Congratulations, adventurer! You have discovered the secret
entrance to this ancient tomb. What would you like to do next?
[1) Enter the tomb.\n2) Search for more hidden mechanisms or
clues before entering.\n3) Call upon your allies or summon
help before proceeding.

>>> What do you want to do: enter the tomb 
 
As you step through the now fully open door, the dim light 
from the torches outside barely reaches into the tomb, leaving 
the passageway shrouded in darkness. You take a deep breath 
and draw your weapon, preparing yourself for whatever lies 
ahead. The air in the tomb is stale and musty, and the silence 
is broken only by the sound of your own footsteps echoing off 
the damp stone walls. 
 
As you move deeper into the tomb, you notice that the 
passageway splits into several different corridors. To your 
left, you see a narrow corridor leading to what looks like a 
library or archive room. To your right, there's a wider 
hallway with large statues on either side, and at the end of 
it, you can make out the outline of a throne room. Straight 
ahead, the passageway continues deeper into the tomb. 
 
Which path would you like to take, brave adventurer? [1) 
Explore the library or archive room.\n2) Approach the statues 
in the wider hallway.\n3) Continue deeper into the tomb.] 
 
>>> What do you want to do: explore the library 
 
As you turn left and follow the narrow corridor, the dim light 
from your torch reveals shelves upon shelves of ancient tomes 
and scrolls. The air is thick with the scent of parchment and 
dust. You can see the faint outlines of figures hunched over 
...
```
