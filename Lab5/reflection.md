# Reflection

The PDF handout describes static analysis and its learning outcomes but does not include four reflection questions. The starter repository README asks for four answers, so the responses below use four reflection prompts aligned with the handout's stated outcomes.

## 1. What is the purpose of static code analysis?

Static analysis examines source code without running it. Pylint highlights likely bugs and maintainability concerns, Flake8 checks Python style and formatting, and Bandit looks for insecure patterns. Together, they find issues early, before they become runtime failures or security problems.

## 2. Which finding had the greatest practical impact?

The unsafe archive extraction and disabled TLS certificate verification had the greatest security impact. An uploaded archive could otherwise place files outside the intended directory, while an unverified HTTPS connection could accept a fraudulent rate table. The fixes constrain archive paths and size and restore certificate verification with a timeout.

## 3. What did the tools miss or require you to reason about?

Static tools do not know the intended business meaning of every input. The original demo passed the string `"no"` as the smoker value; because non-empty strings are truthy, the applicant received a surcharge. The age calculation also ignored whether the birthday had passed. Reading the program's behavior and checking boundary cases was necessary in addition to tool output.

## 4. How will static analysis help maintainability in future work?

Running the tools regularly gives the team consistent feedback on style, likely defects, and common security hazards. Small changes are easier to review when they follow established conventions, and repeatable reports help confirm that a fix removed a warning without introducing new ones. Tool output still needs human review because warnings require context and tools can miss logic errors.
