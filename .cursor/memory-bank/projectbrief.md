# Project Brief: SF-Bench

## Overview

SF-Bench is the first comprehensive benchmark for evaluating AI coding agents on real-world Salesforce development tasks. The benchmark measures AI model performance across multiple Salesforce development modalities including Apex, Lightning Web Components (LWC), Flow automation, and declarative configurations.

## Core Objectives

1. **Objective Measurement**: Provide quantifiable, reproducible metrics for AI agent performance on Salesforce tasks
2. **Real Execution**: Execute all evaluations in real Salesforce scratch orgs with actual deployments and test execution
3. **Functional Validation**: Verify business outcomes, not just deployment success
4. **Multi-Modal Coverage**: Cover diverse Salesforce development patterns (Apex, LWC, Flow, declarative)

## Success Criteria

- Tasks execute in real Salesforce environments
- Results are reproducible across evaluation runs
- Scoring reflects production-readiness (bulkification, error handling, security)
- Benchmark scales to new tasks and models without code changes

## Scope Boundaries

### In Scope
- Apex development tasks (triggers, classes, tests)
- Lightning Web Component development
- Flow automation tasks
- Declarative configuration tasks
- Page layout modifications
- Deployment validation
- Functional validation via scratch org execution

### Out of Scope
- Salesforce administration tasks (user management, permissions)
- AppExchange package development
- ISV partner development patterns
- Marketing Cloud, Commerce Cloud, or other Salesforce clouds

## Target Audiences

1. **AI Researchers**: Benchmarking coding agent performance
2. **Salesforce Developers**: Evaluating AI tools for Salesforce development
3. **Enterprises**: Assessing AI readiness for Salesforce projects
4. **Tool Builders**: Comparing AI model capabilities

## Key Constraints

- Salesforce scratch org limits (daily creation limits, storage limits)
- Governor limits within Salesforce platform
- API rate limits for AI providers
- Real execution time for deployments and tests
