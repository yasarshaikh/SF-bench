---
layout: default
title: SF-Bench Leaderboard - AI Model Rankings | Salesforce AI Benchmark Results
description: Current Salesforce AI benchmark results and rankings for AI coding agents. View performance rankings for Apex, LWC, Flow, and Lightning development tasks.
keywords: salesforce benchmark leaderboard, ai model rankings, salesforce ai performance, llm benchmark results, salesforce ai benchmark leaderboard, sf benchmark results
---

# SF-Bench Leaderboard

*Last updated: 2026-01-06 UTC*

> **Status**: SF-Bench is now running full evaluations with functional validation and weighted scoring (0-100 points). Results show realistic performance with functional validation enabled.

## Overall Rankings

<div id="leaderboard-controls" style="margin: 20px 0;">
  <label for="sort-by" style="margin-right: 10px;">Sort by:</label>
  <select id="sort-by" style="padding: 5px 10px; border: 1px solid #DDDBDA; border-radius: 4px;">
    <option value="overall">Overall Score</option>
    <option value="functional">Functional Score</option>
    <option value="model">Model Name</option>
    <option value="lwc">LWC Score</option>
    <option value="apex">Apex Score</option>
    <option value="flow">Flow Score</option>
  </select>
  <label for="sort-order" style="margin-left: 20px; margin-right: 10px;">Order:</label>
  <select id="sort-order" style="padding: 5px 10px; border: 1px solid #DDDBDA; border-radius: 4px;">
    <option value="desc">Descending</option>
    <option value="asc">Ascending</option>
  </select>
  <button id="export-csv" style="margin-left: 20px; padding: 5px 15px; background: #00A1E0; color: white; border: none; border-radius: 4px; cursor: pointer;">Export CSV</button>
</div>

<div id="leaderboard-container">
  <table id="leaderboard-table" style="width: 100%; border-collapse: collapse; margin: 20px 0;">
    <thead>
      <tr style="background: #F3F2F2; border-bottom: 2px solid #DDDBDA;">
        <th style="padding: 12px; text-align: left; cursor: pointer;" data-sort="rank">Rank</th>
        <th style="padding: 12px; text-align: left; cursor: pointer;" data-sort="model">Model</th>
        <th style="padding: 12px; text-align: center; cursor: pointer;" data-sort="overall">Overall</th>
        <th style="padding: 12px; text-align: center; cursor: pointer;" data-sort="functional">Functional</th>
        <th style="padding: 12px; text-align: center; cursor: pointer;" data-sort="lwc">LWC</th>
        <th style="padding: 12px; text-align: center; cursor: pointer;" data-sort="deploy">Deploy</th>
        <th style="padding: 12px; text-align: center; cursor: pointer;" data-sort="apex">Apex</th>
        <th style="padding: 12px; text-align: center; cursor: pointer;" data-sort="flow">Flow</th>
        <th style="padding: 12px; text-align: center;">Lightning</th>
        <th style="padding: 12px; text-align: center;">Experience</th>
        <th style="padding: 12px; text-align: center;">Architecture</th>
      </tr>
    </thead>
    <tbody id="leaderboard-body">
      <tr data-model="claude-sonnet-4.5" data-overall="41.67" data-functional="6.0" data-lwc="100" data-deploy="100" data-apex="100" data-flow="0">
        <td style="padding: 12px;">🥇</td>
        <td style="padding: 12px;"><strong>Claude Sonnet 4.5</strong></td>
        <td style="padding: 12px; text-align: center;"><strong>41.67%</strong></td>
        <td style="padding: 12px; text-align: center;"><strong>6.0%</strong></td>
        <td style="padding: 12px; text-align: center;">100%</td>
        <td style="padding: 12px; text-align: center;">100%</td>
        <td style="padding: 12px; text-align: center;">100%</td>
        <td style="padding: 12px; text-align: center;">0%*</td>
        <td style="padding: 12px; text-align: center;">0%</td>
        <td style="padding: 12px; text-align: center;">0%</td>
        <td style="padding: 12px; text-align: center;">0%</td>
      </tr>
      <tr data-model="gemini-2.5-flash" data-overall="25.0" data-functional="0" data-lwc="100" data-deploy="100" data-apex="0" data-flow="0">
        <td style="padding: 12px;">🥈</td>
        <td style="padding: 12px;"><strong>Gemini 2.5 Flash</strong></td>
        <td style="padding: 12px; text-align: center;"><strong>25.0%</strong></td>
        <td style="padding: 12px; text-align: center;">-</td>
        <td style="padding: 12px; text-align: center;">100%</td>
        <td style="padding: 12px; text-align: center;">100%</td>
        <td style="padding: 12px; text-align: center;">0%*</td>
        <td style="padding: 12px; text-align: center;">0%*</td>
        <td style="padding: 12px; text-align: center;">0%</td>
        <td style="padding: 12px; text-align: center;">0%</td>
        <td style="padding: 12px; text-align: center;">0%</td>
      </tr>
      <tr data-model="grok-4.1-fast" data-overall="4.0" data-functional="0" data-lwc="0" data-deploy="4.0" data-apex="14.3" data-flow="0">
        <td style="padding: 12px;">🥉</td>
        <td style="padding: 12px;"><strong>Grok 4.1 Fast</strong></td>
        <td style="padding: 12px; text-align: center;"><strong>4.0%</strong></td>
        <td style="padding: 12px; text-align: center;">-</td>
        <td style="padding: 12px; text-align: center;">0%</td>
        <td style="padding: 12px; text-align: center;">4.0%</td>
        <td style="padding: 12px; text-align: center;">14.3%</td>
        <td style="padding: 12px; text-align: center;">0%</td>
        <td style="padding: 12px; text-align: center;">0%</td>
        <td style="padding: 12px; text-align: center;">0%</td>
        <td style="padding: 12px; text-align: center;">0%</td>
      </tr>
    </tbody>
  </table>
</div>

*\* Flow tasks failed due to platform limitations (Flow package dependencies not available in Developer Edition scratch orgs). This is a Salesforce platform constraint, not a tool issue.*

<script>
(function() {
  const table = document.getElementById('leaderboard-table');
  const tbody = document.getElementById('leaderboard-body');
  const sortBy = document.getElementById('sort-by');
  const sortOrder = document.getElementById('sort-order');
  const exportBtn = document.getElementById('export-csv');
  
  let currentSort = { column: 'overall', order: 'desc' };
  
  function parseValue(value) {
    if (value === '-' || value === '') return -1;
    return parseFloat(value) || 0;
  }
  
  function sortTable() {
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const column = sortBy.value;
    const order = sortOrder.value === 'desc' ? -1 : 1;
    
    rows.sort((a, b) => {
      let aVal = a.getAttribute(`data-${column}`);
      let bVal = b.getAttribute(`data-${column}`);
      
      if (column === 'model') {
        // String sort
        return aVal.localeCompare(bVal) * order;
      } else {
        // Numeric sort
        aVal = parseValue(aVal);
        bVal = parseValue(bVal);
        return (aVal - bVal) * order;
      }
    });
    
    // Update rank column
    rows.forEach((row, index) => {
      const rankCell = row.querySelector('td:first-child');
      if (index === 0) rankCell.textContent = '🥇';
      else if (index === 1) rankCell.textContent = '🥈';
      else if (index === 2) rankCell.textContent = '🥉';
      else rankCell.textContent = index + 1;
      tbody.appendChild(row);
    });
  }
  
  function exportToCSV() {
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
    
    let csv = headers.join(',') + '\\n';
    
    rows.forEach(row => {
      const cells = Array.from(row.querySelectorAll('td'));
      const values = cells.map(cell => {
        let text = cell.textContent.trim();
        // Escape commas and quotes
        if (text.includes(',') || text.includes('"')) {
          text = '"' + text.replace(/"/g, '""') + '"';
        }
        return text;
      });
      csv += values.join(',') + '\\n';
    });
    
    // Download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sf-bench-leaderboard.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  }
  
  // Event listeners
  sortBy.addEventListener('change', sortTable);
  sortOrder.addEventListener('change', sortTable);
  exportBtn.addEventListener('click', exportToCSV);
  
  // Make headers clickable
  table.querySelectorAll('thead th[data-sort]').forEach(th => {
    th.style.cursor = 'pointer';
    th.addEventListener('click', () => {
      sortBy.value = th.getAttribute('data-sort');
      sortTable();
    });
  });
  
  // Initial sort
  sortTable();
})();
</script>

### Known Issues

**Claude Opus 4.5 (RouteLLM) - 2025-12-29**: 0% pass rate - All tasks failed due to patch application issues. This evaluation was completed with the previous patch application system. Re-evaluation recommended with improved patch handling.

**Grok 4.1 Fast (RouteLLM) - 2026-01-06**: Evaluation completed with full robustness (passed+failed=100%, error=0%). **4.0% pass rate (1/25 tasks)**. All 5 Flow tasks failed due to platform limitations (Flow package dependencies not available in Developer Edition scratch orgs). Patch application failures correctly categorized as model issues (FAIL), not tool errors. Evaluation is robust and complete.

> **Note**: Functional Score (0-100) is calculated using weighted validation: Deploy(10%) + Unit Tests(20%) + Functional(50%) + Bulk(10%) + No Tweaks(10%). See [VALIDATION_METHODOLOGY.md](./VALIDATION_METHODOLOGY.html) for details.

## Detailed Results

### Gemini 2.5 Flash (Run: 2025-12-28)

| Segment | Tasks | Passed | Pass Rate | Notes |
|---------|:-----:|:------:|:---------:|-------|
| **LWC** | 2 | 2 | ✅ 100% | Jest tests passed (local validation) |
| **Deploy** | 1 | 1 | ✅ 100% | Metadata deployment succeeded |
| Apex | 2 | 0 | ❌ 0% | Scratch org creation issues |
| Flow | 2 | 0 | ❌ 0% | Scratch org creation issues |
| Lightning Pages | 1 | 0 | ❌ 0% | Outcome validation failed |
| Page Layouts | 1 | 0 | ❌ 0% | Scratch org creation issues |
| Experience Cloud | 1 | 0 | ❌ 0% | Outcome validation failed |
| Architecture | 1 | 0 | ❌ 0% | Outcome validation failed |
| Agentforce | 1 | 0 | ❌ 0% | Scratch org creation issues |
| **Total** | **12** | **3** | **25.0%** | Deployment-only validation |

**Validation Mode**: Deployment-only (functional validation pending systematic testing)

### Claude Sonnet 4.5 (Run: 2025-12-28)

| Segment | Tasks | Passed | Pass Rate | Functional Score | Notes |
|---------|:-----:|:------:|:---------:|:----------------:|-------|
| **LWC** | 2 | 2 | ✅ 100% | 10.0% | Jest tests passed, bulk tests passed |
| **Deploy** | 1 | 1 | ✅ 100% | 10.0% | Metadata deployment succeeded |
| **Apex** | 2 | 2 | ✅ 100% | 0.0% | Deployment passed, functional tests failed |
| Flow | 2 | 0 | ❌ 0% | - | Scratch org creation failed |
| Lightning Pages | 1 | 0 | ❌ 0% | - | Outcome validation failed |
| Page Layouts | 1 | 0 | ❌ 0% | - | Deployment failed |
| Experience Cloud | 1 | 0 | ❌ 0% | - | Outcome validation failed |
| Architecture | 1 | 0 | ❌ 0% | - | Outcome validation failed |
| Agentforce | 1 | 0 | ❌ 0% | - | Outcome validation failed |
| **Total** | **12** | **5** | **41.67%** | **6.0%** | **Functional validation enabled** |

**Validation Mode**: Functional validation with weighted scoring (0-100 points)
**Average Functional Score**: 6.0% (out of 100)
- Deploy: 10% ✅
- Unit Tests: 20% ❌
- Functional: 50% ❌ (core requirement)
- Bulk: 10% ✅
- No Tweaks: 10% ❌

## Current Status

SF-Bench is now running full evaluations with functional validation:

1. ✅ **Atomic Testing**: Each component tested individually (completed)
2. ✅ **E2E Validation**: Single model, single task end-to-end test (completed)
3. ✅ **Full Evaluation**: Complete benchmark run with functional validation (completed)

### Recent Evaluations

**Grok 4.1 Fast (RouteLLM) - 2026-01-06**
- **Result**: 4.0% pass rate (1/25 tasks passed, 24 failed, 0 errors)
- **Robustness**: ✅ **PASS** - All tasks evaluated (passed+failed=100%, error=0%)
- **Status**: Final evaluation with all reliability fixes applied:
  - ✅ Platform limitations correctly categorized as FAIL (not ERROR)
  - ✅ Patch application failures correctly categorized as model issues (FAIL)
  - ✅ All Flow tasks failed due to platform constraints (Flow package dependencies)
  - ✅ No tool errors - evaluation is robust and production-ready
- **Breakdown**: 1 Apex task passed (apex-platform-events-001), 24 tasks failed (19 patch failures, 5 platform limitations)
- **Note**: Re-evaluation recommended with improved error handling

**Claude Opus 4.5 (RouteLLM) - 2025-12-29**
- **Result**: 0% pass rate (0/12 tasks)
- **Issue**: Patch application failures with previous patch system
- **Status**: Re-evaluation recommended with improved multi-strategy patch application

## Evaluation Methodology

SF-Bench uses a **multi-level validation approach**:

1. **Syntax Validation**: Code compiles without errors
2. **Deployment Validation**: Metadata deploys successfully
3. **Unit Test Validation**: Apex unit tests pass
4. **Functional Validation**: Actual business outcomes verified (bulk operations, negative cases)
5. **Production-Ready**: Security, error handling, governor limits

See [VALIDATION_METHODOLOGY.md](./VALIDATION_METHODOLOGY.html) for details.

---

## How to Submit Results

1. Run SF-Bench on your model
2. [Submit results via issue](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)
3. Results will be verified and added to leaderboard

See [CONTRIBUTING.md](../CONTRIBUTING.html) for details.
