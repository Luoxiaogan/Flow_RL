# Workflow ID: hotpotqa_437_0
# Benchmark: hotpotqa
# Data Indices: [2678, 1906, 3347, 2174, 38]

<agent id="1">
        <instruction>Identify the key entities and relationships in the problem context. Focus on extracting direct answers from the provided text.</instruction>
        <input>problem</input>
        <output>extracted_answers</output>
    </agent>
    <agent id="2">
        <instruction>Verify if the extracted answer matches the question structure. If not, look for related entities or events that may provide a solution.</instruction>
        <input>extracted_answers</input>
        <output>validated_answer</output>
    </agent>
    <agent id="3">
        <instruction>Check for temporal or categorical consistency (e.g., year, name, location) between the answer and known facts in the context. Resolve ambiguity if needed.</instruction>
        <input>validated_answer</input>
        <output>final_answer</output>
    </agent>
    <agent id="4">
        <instruction>Generate a concise, step-by-step reasoning path based on the final answer to ensure clarity and correctness.</instruction>
        <input>final_answer</input>
        <output>reasoning_path</output>
    </agent>
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />