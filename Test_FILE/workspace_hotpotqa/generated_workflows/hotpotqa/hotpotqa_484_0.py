# Workflow ID: hotpotqa_484_0
# Benchmark: hotpotqa
# Data Indices: [3530, 1921, 2206, 3639]

<operator id="0" type="agent">
        <instruction>
            Analyze the context to identify the key entities and relationships relevant to the question. Focus on extracting the founder of Newark Castle, Nottinghamshire, and their death year.
        </instruction>
    </operator>
    <operator id="1" type="agent">
        <instruction>
            From the context, determine who founded Newark Castle in Nottinghamshire and verify the year of their death using historical references provided.
        </instruction>
    </operator>
    <operator id="2" type="agent">
        <instruction>
            Cross-check the information from multiple sources in the context to ensure accuracy regarding the founder's death year—avoid relying on a single ambiguous reference.
        </instruction>
    </operator>
    <operator id="3" type="agent">
        <instruction>
            Synthesize the verified information to produce the final answer: the year the founder of Newark Castle, Nottinghamshire, died.
        </instruction>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>