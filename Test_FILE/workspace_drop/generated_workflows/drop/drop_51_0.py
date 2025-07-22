# Workflow ID: drop_51_0
# Benchmark: drop
# Data Indices: [3978, 347, 2269, 3007]

<agent id="1">
        <instruction>Identify the key events or actions in the passage that relate to the question. Break down the passage into discrete scoring or chronological elements.</instruction>
        <input>problem</input>
        <output>parsed_events</output>
    </agent>
    
    <agent id="2">
        <instruction>Filter and extract only the relevant information needed to answer the specific question. For example, if the question is about touchdowns under 5 yards, isolate those plays.</instruction>
        <input>parsed_events</input>
        <output>filtered_data</output>
    </agent>
    
    <agent id="3">
        <instruction>Apply logical reasoning to count or calculate based on the filtered data. If multiple agents are involved, ensure each contributes a unique piece of logic (e.g., counting, summing, comparing).</instruction>
        <input>filtered_data</input>
        <output>final_answer</output>
    </agent>
    
    <agent id="4">
        <instruction>Validate the result by cross-checking with the original passage to avoid misinterpretation or omission.</instruction>
        <input>final_answer, problem</input>
        <output>validated_answer</output>
    </agent>
    
    <operator>
        <type>merge</type>
        <inputs>final_answer, validated_answer</inputs>
        <output>result</output>
    </operator>