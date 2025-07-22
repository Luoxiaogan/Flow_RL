#!/usr/bin/env python3
"""
vLLM Server Startup Script for Model Checkpoint Testing
Starts a vLLM server with specified checkpoint on CUDA:7
"""

import argparse
import subprocess
import time
import sys
import os


def start_vllm_server(
    model_path: str,
    port: int = 8000,
    gpu_id: int = 7,
    tensor_parallel_size: int = 1,
    max_model_len: int = 4096,
    served_model_name: str = "checkpoint-model"
):
    """
    Start vLLM server with specified parameters
    
    Args:
        model_path: Path to the model checkpoint
        port: Port number for the server
        gpu_id: GPU device ID (default: 7)
        tensor_parallel_size: Number of GPUs for tensor parallelism
        max_model_len: Maximum sequence length
        served_model_name: Name to serve the model as
    """
    # Set CUDA_VISIBLE_DEVICES to use specified GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    
    # Construct vLLM command
    cmd = [
        "python", "-m", "vllm.entrypoints.openai.api_server",
        "--model", model_path,
        "--port", str(port),
        "--tensor-parallel-size", str(tensor_parallel_size),
        "--max-model-len", str(max_model_len),
        "--served-model-name", served_model_name,
        "--trust-remote-code",
        "--enable-auto-tool-choice",
        "--disable-log-requests"
    ]
    
    print(f"Starting vLLM server with command:")
    print(" ".join(cmd))
    print(f"\nServer will be available at: http://localhost:{port}")
    print(f"Using GPU: cuda:{gpu_id}")
    print(f"Model name: {served_model_name}")
    
    try:
        # Start the server process
        process = subprocess.Popen(cmd)
        
        # Give server time to start
        print("\nWaiting for server to start...")
        time.sleep(10)
        
        # Check if process is still running
        if process.poll() is None:
            print("Server started successfully!")
            print(f"Process PID: {process.pid}")
            
            # Keep the script running
            print("\nPress Ctrl+C to stop the server...")
            process.wait()
        else:
            print("Server failed to start!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nShutting down server...")
        process.terminate()
        process.wait()
        print("Server stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Start vLLM server for checkpoint testing")
    parser.add_argument("--model-path", type=str, required=True,
                        help="Path to the model checkpoint")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port number for the server (default: 8000)")
    parser.add_argument("--gpu-id", type=int, default=7,
                        help="GPU device ID (default: 7)")
    parser.add_argument("--tensor-parallel-size", type=int, default=1,
                        help="Number of GPUs for tensor parallelism (default: 1)")
    parser.add_argument("--max-model-len", type=int, default=4096,
                        help="Maximum sequence length (default: 4096)")
    parser.add_argument("--served-model-name", type=str, default="checkpoint-model",
                        help="Name to serve the model as (default: checkpoint-model)")
    
    args = parser.parse_args()
    
    # Validate model path
    if not os.path.exists(args.model_path):
        print(f"Error: Model path '{args.model_path}' does not exist!")
        sys.exit(1)
    
    start_vllm_server(
        model_path=args.model_path,
        port=args.port,
        gpu_id=args.gpu_id,
        tensor_parallel_size=args.tensor_parallel_size,
        max_model_len=args.max_model_len,
        served_model_name=args.served_model_name
    )


if __name__ == "__main__":
    main()