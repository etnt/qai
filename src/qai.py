#
# See: https://youtu.be/_4K20tOsXK8?si=UE2UszopQ0ju1xIR
#
import ollama

prompt = "> Why is the sky blue?"
print(f"\n{prompt}\n")

output = ollama.generate(model="mistral", prompt=prompt, stream=True)

for chunk in output:
    print(chunk["response"], end="", flush=True)
    if chunk["done"] == True:
        context = chunk["context"]
        print("")

prompt2 = "> Can it be another?"
print(f"\n{prompt2}\n")

output2 = ollama.generate(model="mistral", prompt=prompt2, context=context, stream=True)

for chunk in output2:
    print(chunk["response"], end="", flush=True)
    if chunk["done"] == True:
        print("")
