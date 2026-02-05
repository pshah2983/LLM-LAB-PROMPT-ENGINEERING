# Prompting Best Practices for Engineers

*A one-page reference guide for effective LLM prompting in engineering contexts*

---

## 🎯 Core Principles

| Principle | Why It Matters | How to Apply |
|-----------|----------------|--------------|
| **Be Specific** | Vague prompts → vague answers | State exact requirements upfront |
| **Constrain Output** | Controls verbosity and focus | Set word limits, bullet counts |
| **Request Reasoning** | Improves logical coherence | Use "think step-by-step" |
| **Provide Context** | Enables domain-relevant answers | Background before question |

---

## ✅ Prompt Design Checklist

```
□ Clear task statement (what you want)
□ Explicit constraints (format, length, scope)
□ Relevant context (domain, constraints, goals)
□ Output format specification (bullets, tables, steps)
□ Uncertainty acknowledgment request
```

---

## 📋 Template: Engineering Query Prompt

```
Context:
[Brief background on your system/problem]

Task:
[Clear statement of what you need]

Requirements:
- [Specific constraint 1]
- [Specific constraint 2]
- Maximum [N] words/points

Think through this step-by-step before answering.
Express uncertainty where information is incomplete.
```

---

## ⚠️ Common Pitfalls to Avoid

| Mistake | Problem | Fix |
|---------|---------|-----|
| No constraints | Overly verbose responses | Add word/point limits |
| Missing context | Generic advice | Include domain specifics |
| Direct questions only | Surface-level answers | Add "explain your reasoning" |
| Accepting at face value | Hallucination risk | Ask for sources or caveats |

---

## 🔄 Prompt → Production Pipeline

```
1. Direct Query → Add constraints (P2)
2. Add expert role or reasoning steps (P3/P4)
3. Include retrieved context (RAG-ready, P5)
4. Validate output against checklist
```

---

## 📊 Quick Metrics Reference

| Metric | What to Measure | Target |
|--------|-----------------|--------|
| Accuracy | Key points covered | ≥80% |
| Completeness | Checklist items | ≥75% |
| Efficiency | Useful info per token | Higher is better |
| Reliability | Consistent across runs | Low variance |

---

## 💡 Key Takeaways

1. **Never use naive prompts** for critical applications
2. **Chain-of-Thought improves accuracy** at cost of tokens
3. **Constrained prompts are most efficient** for routine queries
4. **Context-first ordering** scales best to RAG systems
5. **Always verify** claims with specific statistics or sources

---

*Created for EDS 6344 AI for Engineers | LLM Lab Assignment*
