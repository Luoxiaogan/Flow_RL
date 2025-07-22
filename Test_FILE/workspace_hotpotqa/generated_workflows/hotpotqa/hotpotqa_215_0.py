# Workflow ID: hotpotqa_215_0
# Benchmark: hotpotqa
# Data Indices: [1400, 2331, 3362, 496]

<operator id="0" type="agent">
        <instruction>Think step by step to identify the key entities in the problem. Extract relevant information from the context that directly answers the question.</instruction>
        <input>problem</input>
        <output>entity_extraction</output>
    </operator>
    <operator id="1" type="agent">
        <instruction>Verify if the extracted entities are sufficient to answer the question. If not, refine the extraction process or look for additional contextual clues.</instruction>
        <input>entity_extraction</input>
        <output>verification</output>
    </operator>
    <operator id="2" type="agent">
        <instruction>Based on the verified entities, determine the correct answer using logical reasoning. Ensure no external assumptions are made.</instruction>
        <input>verification</input>
        <output>final_answer</output>
    </operator>
    <operator id="3" type="agent">
        <instruction>Check for consistency between the final answer and all provided context. Flag any contradictions or ambiguities.</instruction>
        <input>final_answer</input>
        <output>consistency_check</output>
    </operator>
    <operator id="4" type="agent">
        <instruction>Generate a concise explanation of how the answer was derived, based on the verified steps and consistent evidence.</instruction>
        <input>consistency_check</input>
        <output>explanation</output>
    </operator>
    <operator id="5" type="agent">
        <instruction>Review the entire workflow: ensure each operator contributes uniquely and the graph complexity is between 3 and 8.</instruction>
        <input>explanation</input>
        <output>optimized_graph</output>
    </operator>