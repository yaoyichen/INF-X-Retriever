from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model and tokenizer
model_name = "infly/inf-query-aligner"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Define input query
query = "Claim in article about why insects are attracted to light\nIn this article they are addressing the reason insects are attracted to light when they say\nHeat radiation as an attractive component is refuted by the effect of LED lighting, which supplies negligible infrared radiation yet still entraps vast numbers of insects.\nI don't see why attraction to LEDs shows they're not seeking heat. Could they for example be evolutionarily programmed to associate light with heat? So that even though they don't encounter heat near/on the LEDs they still \"expect\" to?"

QUERY_WRITER_PROMPT = (
    "For the input query, formulating a concise search query for dense retrieval by distilling the core intent from a complex user prompt and ignoring LLM instructions."
    "The response should be less than 200 words"
)
messages = [
    {
        "role": "system",
        "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
    },
    {
        "role": "user",
        "content": (
            f"{QUERY_WRITER_PROMPT}\n\n"
            f"**Input Query:**\n{query}\n"
            f"**Your Output:**\n"
        ),
    },
]

# Apply chat template
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer(
    [text], 
    truncation=True, 
    max_length=8192, 
    return_tensors="pt"
).to(model.device)

# Generate rewritten query
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print(response)
