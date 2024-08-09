verbose_prompt = """
You are a marketing analyst tasked with analyzing campaign performance data and generating a narrative report.

Your goal is to analyze this data and create a narrative report focusing on the best and worst performing campaign types. Consider the following metrics in your analysis:

1. Click-Through Rate (CTR)
2. Cost Per Click (CPC)
3. Return On Ad Spend (ROAS)

Follow these steps to complete the task:

1. Analyze the provided data, calculating the average CTR, CPC, and ROAS for each campaign type.

2. Identify the best and worst performing campaign types based on these metrics.

3. Provide a detailed analysis of why these campaign types performed well or poorly.

4. Offer recommendations for improving the performance of the underperforming campaigns and for capitalizing on the success of the top performers.

5. Present your findings in a clear, narrative format. Use paragraphs to separate different ideas and sections of your analysis.

6. Include specific numerical values in your report. Format all percentages to two decimal places (e.g., 12.34%) and all currency values to two decimal places with a dollar sign (e.g., $12.34).

Structure your output as follows:

1. Overview: Provide a brief overview of the campaign performance analysis.

2. Best Performing: Discuss the best performing campaign type(s), including:
   - Which metrics they excelled in
   - Specific numerical values for CTR, CPC, and ROAS
   - Reasons for their success
   - Recommendations for leveraging their success

3. Worst Performing: Discuss the worst performing campaign type(s), including:
   - Which metrics they struggled with
   - Specific numerical values for CTR, CPC, and ROAS
   - Reasons for their poor performance
   - Recommendations for improvement

4. Recommendations: Provide overall recommendations for the campaign strategy based on your analysis.

Ensure that your analysis is thorough, insightful, and actionable. Use clear, professional language throughout your report.
"""

# This can get passed in from top level application
prompts = [
    "Show me a report of spend by device for each placement in a side by side bar chart",
    "Show me a report of spend by device for each placement in a table",
    "Generate me narrative for a report of spend by device for each placement in text format",
    "Show me spend by Campaign Type over time for the last 4 weeks in the data grouped weekly in a line chart",
    verbose_prompt,
]

print(prompts)
