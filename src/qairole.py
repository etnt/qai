#
# See: https://youtu.be/_4K20tOsXK8?si=UE2UszopQ0ju1xIR
#
import ollama

prompt = "> Why is the sky blue?"
print(f"\n{prompt}\n")

msgs  = [
    {"role": "system",
     "content": "The user will give you a concept. Explain it to a 5 year old, using descriptive imagery and intersting and fun language."},
     {"role": "user",
      "content": "Quantum physics"}]

output = ollama.generate(model="mistral", msgs=msgs)

print(output['message']['content'])