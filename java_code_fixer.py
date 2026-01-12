import anthropic


class JavaCodeFixer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def fix_code(self, java_code: str, error_message: str, java_version: str, model: str = "claude-opus-4-5") -> str:
        prompt = f"""
You are a Java compiler and code fixer.

Rules:
- Return ONLY valid Java source code
- Do NOT include explanations, comments, or markdown
- The code MUST compile and run successfully on Java {java_version}

Java Version:
{java_version}

Compilation / Runtime Error:
{error_message}

Original Java Code:
{java_code}

Return the corrected Java code only.
"""

        response = self.client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract text safely
        corrected_code = ""
        for block in response.content:
            if block.type == "text":
                corrected_code += block.text

        # Remove markdown code block formatting
        corrected_code = corrected_code.strip()
        if corrected_code.startswith("```java"):
            corrected_code = corrected_code[7:]
        elif corrected_code.startswith("```"):
            corrected_code = corrected_code[3:]
        if corrected_code.endswith("```"):
            corrected_code = corrected_code[:-3]

        return corrected_code.strip()
