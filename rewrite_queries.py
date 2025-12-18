"""
Script Name: rewrite_queries.py
Description: Rewrites queries in parquet files using a causal language model (LLM).
             Reads parquet files, generates rewritten queries, and saves them as JSON.
"""

import argparse
import copy
import json
import logging
import os
import sys
from typing import List, Dict, Any, Union

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class GenerateWrapper(nn.Module):
    """
    Wrapper class for AutoModelForCausalLM to handle custom generation logic,
    specifically padding the output to a target length if necessary.
    """

    def __init__(self, model_name_or_path: str, max_new_tokens: int = 512):
        """
        Initialize the wrapper.

        Args:
            model_name_or_path (str): Path or name of the pretrained model.
            max_new_tokens (int): Maximum number of new tokens to generate.
        """
        super().__init__()
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            torch_dtype="auto"
        )
        self.max_new_tokens = max_new_tokens

    def forward(self, pad_token_id: int, input_len: int, **model_inputs) -> torch.Tensor:
        """
        Forward pass to generate tokens.

        Args:
            pad_token_id (int): The token ID used for padding.
            input_len (int): The length of the input sequence.
            **model_inputs: Keyword arguments for the model (e.g., input_ids, attention_mask).

        Returns:
            torch.Tensor: Generated token IDs.
        """
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=self.max_new_tokens
        )

        bsz, seq_len = generated_ids.shape
        target_len = input_len + self.max_new_tokens

        # If the generated sequence is shorter than expected, pad it
        if seq_len < target_len:
            pad_len = target_len - seq_len
            pad = torch.full(
                (bsz, pad_len),
                pad_token_id,
                dtype=generated_ids.dtype,
                device=generated_ids.device
            )
            generated_ids = torch.cat([generated_ids, pad], dim=1)

        return generated_ids


class INFRewrite:
    """
    Class to handle the query rewriting process using an LLM.
    """

    def __init__(self, model_name_or_path: str, batch_size: int = 32) -> None:
        """
        Initialize the rewriter.

        Args:
            model_name_or_path (str): Path or name of the model.
            batch_size (int): Batch size for inference.
        """
        self.batch_size = batch_size

        logger.info(f"Loading model: {model_name_or_path}")
        self.model = GenerateWrapper(model_name_or_path=model_name_or_path, max_new_tokens=512)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, padding_side='left')

        # Set pad_token if it's not defined
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Device setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # Multi-GPU support
        if torch.cuda.device_count() > 1:
            logger.info(f"Using {torch.cuda.device_count()} GPUs")
            self.model = nn.DataParallel(self.model)
            self.batch_size *= torch.cuda.device_count()

        self.model.eval()

    def prompt_build(self, query: str) -> List[Dict[str, str]]:
        """
        Builds the prompt for the model based on the input query.

        Args:
            query (str): The original query to rewrite.

        Returns:
            List[Dict[str, str]]: A list of messages formatted for the chat template.
        """
        QUERY_WRITER_PROMPT = (
            "For the input query, formulating a concise search query for dense retrieval "
            "by distilling the core intent from a complex user prompt and ignoring LLM instructions."
            "The response should be less than 200 words"
        )

        prompt_content = [
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

        return prompt_content

    @torch.no_grad()
    def rewrite(self, queries: List[Dict[str, Any]], data_name: str) -> List[Dict[str, Any]]:
        """
        Rewrites a list of queries in batches.

        Args:
            queries (List[Dict[str, Any]]): List of query objects.
            data_name (str): Name of the dataset (for logging/progress).

        Returns:
            List[Dict[str, Any]]: List of query objects with rewritten queries.
        """
        queries_rewrite = []
        total_queries = len(queries)

        for i in tqdm(range(0, total_queries, self.batch_size), desc=f"{data_name} rewrite"):
            query_batch = queries[i : i + self.batch_size]
            prompt_content_list = [self.prompt_build(line["query"]) for line in query_batch]

            # Apply chat template
            input_list = [
                self.tokenizer.apply_chat_template(
                    prompt,
                    tokenize=False,
                    add_generation_prompt=True
                )
                for prompt in prompt_content_list
            ]

            # Tokenize
            model_inputs = self.tokenizer(
                input_list,
                padding=True,
                truncation=True,
                max_length=8192,
                return_tensors="pt"
            ).to(self.device)

            global_input_len = model_inputs['input_ids'].shape[1]

            # Generate
            generated_ids = self.model(
                self.tokenizer.pad_token_id,
                input_len=global_input_len,
                **model_inputs
            )

            # Post-process: Remove input tokens from generated output
            input_len = model_inputs['attention_mask'].shape[1]
            trimmed_generated = []
            for out_ids in generated_ids:
                trimmed_generated.append(out_ids[input_len:])

            response = self.tokenizer.batch_decode(trimmed_generated, skip_special_tokens=True)

            # Update results
            for line, query_rewrite in zip(query_batch, response):
                line_rewrite = copy.deepcopy(line)
                line_rewrite["query"] = query_rewrite
                queries_rewrite.append(line_rewrite)

        return queries_rewrite

    def __call__(self, queries: List[Dict[str, Any]], data_name: str) -> List[Dict[str, Any]]:
        """Allow the instance to be called like a function."""
        return self.rewrite(queries, data_name)


def save_custom_json(data_list: List[Dict[str, Any]], output_path: str) -> None:
    """
    Saves a list of dictionaries to a JSON file with custom formatting.

    Args:
        data_list (List[Dict[str, Any]]): The data to save.
        output_path (str): The destination file path.
    """
    
    def numpy_serializer(obj):
        """Helper to serialize numpy objects."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("[\n")
        total = len(data_list)
        for idx, item in enumerate(data_list):
            json_line = json.dumps(item, ensure_ascii=False, default=numpy_serializer)
            comma = "," if idx < total - 1 else ""
            f.write(f"  {json_line}{comma}\n")
        f.write("]\n")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Rewrite queries using INF-X-Retrieve model.")
    parser.add_argument('--data_folder_path', type=str, default='xlangai/bright', help="Path to the folder containing parquet files.")
    parser.add_argument('--model_name_or_path', type=str, default='infly/inf-query-aligner', help="HuggingFace model name or local path.")
    parser.add_argument('--batch_size', type=int, default=256, help="Inference batch size.")
    parser.add_argument('--output_path', type=str, default="./rewrite_data/INF-X-Retrieve", help="Directory to save output files.")
    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_path, exist_ok=True)
    logger.info(f"Results will be saved to: {args.output_path}")

    # Initialize Rewriter
    try:
        rewrite_llm = INFRewrite(args.model_name_or_path, args.batch_size)
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        sys.exit(1)

    # Process files
    try:
        # Check if directory exists
        if not os.path.exists(args.data_folder_path):
             logger.error(f"Data folder path does not exist: {args.data_folder_path}")
             # Note: If passing a HF dataset ID like 'xlangai/bright', os.listdir will fail.
             # The original code assumed a local directory or failed. 
             # For now, we assume local directory behavior as in the original script.
             return

        files = [f for f in os.listdir(args.data_folder_path) if f.endswith(".parquet")]
        
        if not files:
            logger.warning(f"No .parquet files found in {args.data_folder_path}")
            return

        for file_name in files:
            dataset_name = file_name.replace(".parquet", "")
            file_path = os.path.join(args.data_folder_path, file_name)
            
            logger.info(f"Processing dataset: {dataset_name} from {file_path}")

            df = pd.read_parquet(file_path)
            queries = df.to_dict(orient="records")
            
            # Run rewriting
            queries_rewrite = rewrite_llm(queries, dataset_name)

            # Construct output filename
            # Example: biology-test.parquet -> biology_queries.json
            prefix = dataset_name.split('-')[0]
            out_filename = f"{prefix}_queries.json"
            out_file_path = os.path.join(args.output_path, out_filename)

            save_custom_json(queries_rewrite, out_file_path)
            logger.info(f"Saved to {out_file_path}")

    except Exception as e:
        logger.exception(f"An error occurred during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
