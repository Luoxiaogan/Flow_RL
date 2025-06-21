import json
import random

def is_prime(num):
    """Checks if a number is prime."""
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def generate_prime(min_val=10, max_val=200):
    """Generates a random prime number within a given range."""
    while True:
        p = random.randint(min_val, max_val)
        if is_prime(p):
            return p

def iterative_squaring(x, n, p):
    """Calculates x^(2^n) mod p."""
    result = x
    for _ in range(n):
        result = (result * result) % p
    return result

def generate_dataset(num_samples=100, output_file="TCS_problem/iterative_squaring_dataset.json"):
    """Generates the dataset and saves it to a JSON file."""
    dataset = []
    for _ in range(num_samples):
        p = generate_prime()
        x = random.randint(1, p - 1)
        n = random.randint(1, 6)  # Number of squaring operations

        answer = iterative_squaring(x, n, p)

        prompt_text = f"The problem is to compute x raised to the power of 2^n, modulo p. This is also known as iterative squaring. " \
                      f"You are given a prime modulus p = {p}, an initial value x = {x}, and a number of squaring iterations n = {n}. " \
                      f"Your task is to calculate the final result of x^(2^{n}) mod p. " \
                      f"Please provide a step-by-step calculation. Start with the initial value x. In each step i (from 1 to n), square the result from the previous step and take the modulo p. " \
                      f"Clearly show each intermediate squaring and modulo operation."

        dataset.append({
            "input": {
                "p": p,
                "initial_value": x,
                "iterations": n
            },
            "prompt": prompt_text,
            "answer": answer
        })

    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=4)
    print(f"Dataset with {num_samples} samples generated and saved to {output_file}")

if __name__ == "__main__":
    # You can create the directory if it doesn't exist before running,
    # or handle it within the script if preferred.
    # For simplicity, this example assumes TCS_problem directory exists.
    generate_dataset(num_samples=200) 