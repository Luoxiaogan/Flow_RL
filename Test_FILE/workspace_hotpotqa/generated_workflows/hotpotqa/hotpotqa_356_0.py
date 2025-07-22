# Workflow ID: hotpotqa_356_0
# Benchmark: hotpotqa
# Data Indices: [2735, 2971, 2025, 1544, 1212]

<agent name="Extractor">
        <instruction>Identify key entities and relationships from the context. Focus on the main subject, its attributes, and associated facts.</instruction>
        <input>problem</input>
        <output>structured_data</output>
    </agent>

    <agent name="Resolver">
        <instruction>Use structured data to determine the correct answer by matching the question's requirements with the extracted facts.</instruction>
        <input>structured_data</input>
        <output>answer</output>
    </agent>

    <agent name="Validator">
        <instruction>Verify that the answer aligns with the most relevant and specific information in the context. Eliminate ambiguous or indirect matches.</instruction>
        <input>answer</input>
        <output>final_answer</output>
    </agent>

    <agent name="Ensemble">
        <instruction>Generate multiple interpretations of the question using loops and list comprehensions to explore different angles—then select the best one based on clarity and precision.</instruction>
        <input>problem</input>
        <output>ensemble_answers</output>
    </agent>

    <agent name="Filter">
        <instruction>From the ensemble answers, filter out any that are not directly supported by the context. Keep only those with clear evidence.</instruction>
        <input>ensemble_answers</input>
        <output>filtered_answers</output>
    </agent>

    <connect from="Extractor" to="Resolver"/>
    <connect from="Resolver" to="Validator"/>
    <connect from="Extractor" to="Ensemble"/>
    <connect from="Ensemble" to="Filter"/>
    <connect from="Filter" to="Validator"/>