import ollama

with open('./data/elephant.jpg', 'rb') as f:
    image = f.read()

prompt = "> Describe this picture?"
print(f"\n{prompt}\n")

output = ollama.generate(
    model="llava",
    prompt=prompt,
    images=[image]
)

print(output['response'])

context = output['context']

prompt2 = "> Are there any watermarks in the picture and if so where is it located? If you are not sure then say no."
print(f"\n{prompt2}\n")

output2 = ollama.generate(
    model="llava",
    prompt=prompt2,
    context=context,
    images=[image]
)

print(output2['response'])