---
layout: default
title: SF-Bench vs. SWE-bench - Detailed Comparison
description: Comprehensive comparison between SF-Bench and SWE-bench. When to use which benchmark.
keywords: sf-bench vs swe-bench, benchmark comparison, ai coding benchmark comparison
---

# SF-Bench vs. SWE-bench: Detailed Comparison

**Two benchmarks, different purposes. Here's when to use which.**

---

## 🎯 Quick Comparison

| Aspect | SWE-bench | SF-Bench |
|--------|-----------|----------|
| **Domain** | Open-source Python | Salesforce |
| **Tasks** | 2,000+ GitHub issues | 12+ verified tasks |
| **Execution** | Docker containers | Salesforce scratch orgs |
| **Focus** | General programming | Enterprise CRM development |
| **Validation** | Test suite execution | Functional + deployment |
| **Use Case** | Research, general AI | Salesforce-specific AI |

---

## 📊 Detailed Comparison

### 1. Domain & Scope

#### SWE-bench
- **Domain**: Open-source Python projects
- **Scope**: General software engineering
- **Examples**: Django, scikit-learn, pandas
- **Focus**: Bug fixes, feature additions

#### SF-Bench
- **Domain**: Salesforce platform
- **Scope**: Enterprise CRM development
- **Examples**: Apex, LWC, Flow, Lightning Pages
- **Focus**: Business logic, platform constraints

**When to use SWE-bench**: Testing general programming capabilities  
**When to use SF-Bench**: Testing Salesforce-specific capabilities

---

### 2. Task Types

#### SWE-bench Tasks
- Bug fixes in Python codebases
- Feature additions to open-source projects
- Code refactoring
- Test writing

#### SF-Bench Tasks
- Apex triggers and classes
- Lightning Web Components
- Flow automation
- Lightning Pages
- Experience Cloud sites
- Architecture design

**Key Difference**: SF-Bench covers **multi-modal** development (code + visual tools)

---

### 3. Execution Environment

#### SWE-bench
- **Environment**: Docker containers
- **Setup**: Clone repo, install dependencies
- **Execution**: Run test suite
- **Validation**: Test pass/fail

#### SF-Bench
- **Environment**: Salesforce scratch orgs
- **Setup**: Create scratch org, deploy metadata
- **Execution**: Deploy + run tests + verify outcomes
- **Validation**: Multi-level (deploy + tests + functional)

**Key Difference**: SF-Bench validates **functional outcomes**, not just test execution

---

### 4. Validation Methodology

#### SWE-bench Validation
```
1. Apply patch
2. Run test suite
3. Check: Tests pass? → PASS/FAIL
```

#### SF-Bench Validation
```
1. Apply solution
2. Deploy to scratch org (10%)
3. Run unit tests (20%)
4. Verify functional outcome (50%)
5. Test bulk operations (10%)
6. Check no manual tweaks (10%)
7. Score: 0-100 points
```

**Key Difference**: SF-Bench uses **weighted scoring** with functional validation

---

### 5. Task Complexity

#### SWE-bench
- **Complexity**: Varies (easy to hard)
- **Context**: GitHub issue descriptions
- **Dependencies**: Project-specific
- **Size**: Large codebases

#### SF-Bench
- **Complexity**: Controlled (lite to realistic)
- **Context**: Detailed task descriptions
- **Dependencies**: Salesforce platform
- **Size**: Focused tasks

**Key Difference**: SF-Bench tasks are **curated** for Salesforce development

---

### 6. Use Cases

#### When to Use SWE-bench

✅ **Good for**:
- General AI research
- Testing Python capabilities
- Open-source contribution simulation
- Large-scale evaluation

❌ **Not ideal for**:
- Salesforce-specific evaluation
- Enterprise CRM development
- Multi-modal development testing

#### When to Use SF-Bench

✅ **Good for**:
- Salesforce AI tool evaluation
- Enterprise CRM development
- Multi-modal development testing
- Business logic validation

❌ **Not ideal for**:
- General programming evaluation
- Non-Salesforce use cases
- Large-scale research (yet)

---

## 🔍 Methodology Comparison

### SWE-bench Methodology

1. **Task Selection**: Real GitHub issues
2. **Solution Generation**: AI generates patch
3. **Validation**: Run test suite
4. **Scoring**: Pass/fail binary

**Strengths**:
- Large task set
- Real-world issues
- Reproducible

**Limitations**:
- Binary scoring
- No functional validation
- Python-only

### SF-Bench Methodology

1. **Task Selection**: Curated Salesforce tasks
2. **Solution Generation**: AI generates solution
3. **Validation**: Multi-level validation
4. **Scoring**: Weighted 0-100 points

**Strengths**:
- Functional validation
- Multi-modal testing
- Weighted scoring
- Salesforce-specific

**Limitations**:
- Smaller task set (growing)
- Salesforce-only
- Requires Salesforce org

---

## 📈 Performance Comparison

### What Models Score Well on SWE-bench?

- GPT-4: ~30-40% pass rate
- Claude 3.5: ~25-35% pass rate
- Gemini: ~20-30% pass rate

### What Models Score Well on SF-Bench?

- Claude Sonnet 4.5: 41.67% overall, 6.0% functional
- Gemini 2.5 Flash: 25.0% overall
- *More results pending*

**Note**: Scores aren't directly comparable due to different methodologies.

---

## 🎯 Which Benchmark Should You Use?

### Use SWE-bench If:

- ✅ Testing general programming capabilities
- ✅ Evaluating Python-specific AI
- ✅ Research on open-source contributions
- ✅ Need large-scale evaluation

### Use SF-Bench If:

- ✅ Testing Salesforce-specific AI
- ✅ Evaluating enterprise CRM development
- ✅ Testing multi-modal development
- ✅ Need functional validation

### Use Both If:

- ✅ Comprehensive AI evaluation
- ✅ Comparing general vs. domain-specific
- ✅ Research on AI capabilities
- ✅ Full-spectrum benchmarking

---

## 🔬 Research Implications

### For AI Researchers

**SWE-bench**:
- Tests general programming
- Large-scale evaluation
- Reproducible results

**SF-Bench**:
- Tests domain-specific capabilities
- Functional validation
- Real-world execution

**Combined**:
- Comprehensive evaluation
- General + domain-specific
- Full AI capability spectrum

---

## 📚 Further Reading

- **[SWE-bench Paper](https://arxiv.org/abs/2310.06770)** - Original SWE-bench research
- **[SF-Bench Methodology](../VALIDATION_METHODOLOGY.md)** - Our validation approach
- **[Benchmark Details](../BENCHMARK.md)** - Technical specifications

---

## 🤝 Collaboration

**SF-Bench is inspired by SWE-bench** and follows similar principles:

- ✅ Real-world tasks
- ✅ Functional validation
- ✅ Objective measurement
- ✅ Open source

**We're complementary**, not competitive!

---

## 📊 Summary

| Aspect | Winner |
|--------|--------|
| **General Programming** | SWE-bench |
| **Salesforce Development** | SF-Bench |
| **Task Volume** | SWE-bench |
| **Functional Validation** | SF-Bench |
| **Multi-modal Testing** | SF-Bench |
| **Research Use** | Both |

**Bottom Line**: Use **SWE-bench** for general programming, **SF-Bench** for Salesforce development.

---

**Ready to evaluate?** Check out our [Quick Start Guide](../quickstart.md)!
