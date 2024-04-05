#
# See: https://youtu.be/_4K20tOsXK8?si=UE2UszopQ0ju1xIR
#
import ollama

msgs = [
  {"role": "system", "content": "You are a speech writer. Create a speech on the topic that the user provides. It should be witty and fun."},
  { "role": "user", "content": "Arnold has been working hard is whole life using his hands. He has now turned 50. He has two dogs , a wife and three children. He likes spagetti." }
]
output = ollama.chat(model="mistral", messages=msgs )

print(output['message']['content'])
