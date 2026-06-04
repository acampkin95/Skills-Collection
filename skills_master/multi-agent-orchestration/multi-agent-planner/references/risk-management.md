# Risk Management Reference

Comprehensive guide to risk identification, assessment, mitigation, and monitoring for project planning.

## Table of Contents
1. [Risk Identification](#risk-identification)
2. [Risk Assessment Matrix](#risk-assessment-matrix)
3. [Mitigation Strategies](#mitigation-strategies)
4. [Contingency Planning](#contingency-planning)
5. [Risk Monitoring](#risk-monitoring)
6. [Common Risk Categories](#common-risk-categories)
7. [Risk Templates](#risk-templates)
8. [Best Practices](#best-practices)

---

## Risk Identification

### Risk Identification Techniques

| Technique | Description | Best For |
|-----------|-------------|----------|
| Brainstorming | Team ideation session | Early project phases |
| Delphi Method | Anonymous expert input | Complex technical risks |
| SWOT Analysis | Strengths, Weaknesses, Opportunities, Threats | Strategic planning |
| Interviewing | One-on-one discussions | Deep expertise capture |
| Checklist Review | Historical risk lists | Experienced teams |
| Root Cause Analysis | Problem追溯 | Recurring issues |

### Risk Identification Process

```
1. Gather Information
   ├─ Project documents (charter, requirements, plans)
   ├─ Stakeholder input
   ├─ Historical data
   └─ External research

2. Identify Potential Risks
   ├─ Technical risks
   ├─ Resource risks
   ├─ Schedule risks
   ├─ Scope risks
   ├─ External risks
   └─ Organizational risks

3. Document Risks
   ├─ Risk description
   ├─ Potential triggers
   ├─ Potential impacts
   └─ Initial categories
```

### Risk Categories

| Category | Description | Examples |
|----------|-------------|----------|
| Technical | Technology-related risks | Performance, integration, security |
| Resource | Personnel and skill gaps | Turnover, availability, hiring |
| Schedule | Timeline pressures | Delays, dependencies, blockers |
| Scope | Requirements changes | Scope creep, unclear requirements |
| External | Outside team control | Vendor delays, regulations, market |
| Organizational | Company-related | Budget cuts, priority changes |
| Quality | Defects and standards | Test coverage, compliance |
| Operational | Day-to-day operations | Support load, maintenance |

---

## Risk Assessment Matrix

### Risk Scoring Formula

```
Risk Score = Probability × Impact

Probability: 0.0 to 1.0 ( likelihood of occurrence )
Impact: 1-3 scale ( severity of consequence )
```

### Probability Levels

| Level | Range | Description |
|-------|-------|-------------|
| Very Low | 0.0-0.1 | Highly unlikely |
| Low | 0.1-0.3 | Unlikely but possible |
| Medium | 0.3-0.5 | Possible |
| High | 0.5-0.7 | Likely |
| Very High | 0.7-1.0 | Almost certain |

### Impact Levels

| Level | Score | Description |
|-------|-------|-------------|
| Very Low | 1 | Minimal impact, easily absorbed |
| Low | 2 | Minor impact, some disruption |
| Medium | 3 | Moderate impact, manageable |
| High | 4 | Significant impact, requires action |
| Very High | 5 | Severe impact, project-threatening |

### Risk Matrix

```
                    IMPACT
                  1    2    3    4    5
                ┌────┬────┬────┬────┬────┐
        0.9-1.0 │ M  │ H  │ H  │ C  │ C  │
      P         ├────┼────┼────┼────┼────┤
      r 0.7-0.9 │ M  │ M  │ H  │ H  │ C  │
      o         ├────┼────┼────┼────┼────┤
      b 0.5-0.7 │ L  │ M  │ M  │ H  │ H  │
      a         ├────┼────┼────┼────┼────┤
      b 0.3-0.5 │ L  │ L  │ M  │ M  │ H  │
      i         ├────┼────┼────┼────┼────┤
      l 0.1-0.3 │ L  │ L  │ L  │ M  │ M  │
      i         ├────┼────┼────┼────┼────┤
      t 0.0-0.1 │ L  │ L  │ L  │ L  │ M  │
      y         └────┴────┴────┴────┴────┘

      L = Low Risk    M = Medium Risk
      H = High Risk   C = Critical Risk
```

### Risk Priority Matrix

| Score | Priority | Response Time |
|-------|----------|---------------|
| < 0.6 | Low | Monitor monthly |
| 0.6-1.5 | Medium | Address in current sprint |
| 1.5-3.0 | High | Immediate attention |
| > 3.0 | Critical | Urgent, escalation required |

### Example Risk Assessments

| Risk | Probability | Impact | Score | Level | Priority |
|------|-------------|--------|-------|-------|----------|
| Key developer departure | 0.3 | 4 | 1.2 | Medium | 2 |
| Third-party API downtime | 0.5 | 3 | 1.5 | High | 1 |
| Requirements change mid-project | 0.6 | 3 | 1.8 | High | 1 |
| Performance targets not met | 0.4 | 4 | 1.6 | High | 1 |
| Minor UI bug | 0.7 | 1 | 0.7 | Low | 3 |

---

## Mitigation Strategies

### Risk Response Options

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| Avoid | Eliminate the risk source | Risk severity > threshold |
| Mitigate | Reduce probability or impact | Risk is manageable |
| Transfer | Shift risk to third party | Specialized handling exists |
| Accept | Acknowledge and monitor | Low impact or cost of response > risk |
| Contingency | Prepare response plan | When risk may still occur |

### Mitigation Strategy Template

```
RISK: [Risk Name]

Current State:
  Probability: [X]
  Impact: [Y]
  Score: [Z]

Mitigation Options:
  1. [Option A]
     - Pros: [ ]
     - Cons: [ ]
     - Cost: [ ]

  2. [Option B]
     - Pros: [ ]
     - Cons: [ ]
     - Cost: [ ]

Selected Strategy: [Option]
Action Items:
  - [Action 1]
  - [Action 2]

Owner: [Name]
Timeline: [Date]
Status: [In Progress|Complete]
```

### Common Mitigation Tactics

#### Technical Risks
| Risk | Mitigation |
|------|------------|
| Performance issues | Early profiling, architecture review |
| Security vulnerabilities | Security audits, penetration testing |
| Integration failures | Early integration testing, mocking |
| Technology obsolescence | Standards compliance, abstraction layers |

#### Resource Risks
| Risk | Mitigation |
|------|------------|
| Key person departure | Cross-training, documentation |
| Skill gaps | Training programs, hiring |
| Availability constraints | Resource buffer, schedule flexibility |
| Team overload | Workload balancing, prioritization |

#### Schedule Risks
| Risk | Mitigation |
|------|------------|
| Unrealistic deadlines | Buffer time, scope negotiation |
| Dependency delays | Parallel work, alternative paths |
| Requirements creep | Change control process |
| Rework | Quality gates, early validation |

---

## Contingency Planning

### Contingency vs. Mitigation

| Aspect | Mitigation | Contingency |
|--------|------------|-------------|
| Purpose | Prevent or reduce risk | Respond if risk occurs |
| Timing | Before risk materializes | After risk occurs |
| Cost | Investment in prevention | Cost of response |
| Ownership | Risk owner | Response team |

### Contingency Plan Template

```
RISK: [Risk Name]

Trigger Conditions:
  - [Condition 1]
  - [Condition 2]

Response Actions:
  Step 1: [Action]
  Step 2: [Action]
  Step 3: [Action]

Resources Required:
  - [Resource 1]
  - [Resource 2]

Communication Plan:
  - [Who to notify]
  - [How to notify]
  - [When to communicate]

Escalation Path:
  Level 1: [Team Lead]
  Level 2: [Project Manager]
  Level 3: [Executive]

Rollback Plan:
  [If contingency fails, how to recover]

Cost Estimate: [$X]
Timeline: [Y days]
Status: [Draft|Reviewed|Approved]
```

### Contingency Triggers

| Trigger Type | Examples |
|--------------|----------|
| Time-based | Deadline missed, milestone delayed |
| Metric-based | Defect count > threshold, performance < SLA |
| Event-based | Key resource leaves, vendor fails |
| Decision-based | Stakeholder request, scope change |

### Contingency Budget

| Risk Level | Recommended Budget |
|------------|-------------------|
| Low | 0-5% of project budget |
| Medium | 5-10% of project budget |
| High | 10-20% of project budget |
| Critical | 20-30% of project budget |

---

## Risk Monitoring

### Monitoring Techniques

| Technique | Frequency | Purpose |
|-----------|-----------|---------|
| Risk Register Review | Weekly | Track all risks |
| Burndown Charts | Sprint | Progress on mitigation |
| Milestone Reviews | Milestone | Assess milestone risks |
| Metrics Dashboard | Daily | Automated alerting |
| Retrospectives | Sprint | Identify new risks |

### Risk Register Structure

```yaml
risk_register:
  project: "Project Name"
  last_updated: "YYYY-MM-DD"
  risks:
    - id: "RISK-001"
      name: "Key Developer Departure"
      description: "Risk that a key developer leaves the project"
      category: "resource"
      probability: 0.3
      impact: 4
      score: 1.2
      level: "medium"
      status: "identified"
      mitigation: "Cross-train team members"
      contingency: "Hire replacement within 30 days"
      owner: "Project Manager"
      created: "YYYY-MM-DD"
      updated: "YYYY-MM-DD"
      last_reviewed: "YYYY-MM-DD"
      next_review: "YYYY-MM-DD"
      history:
        - date: "YYYY-MM-DD"
          action: "Initial identification"
          actor: "PM"
```

### Risk Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Open Risks | Number of active risks | Decreasing |
| Critical Risks | High-priority risks | Zero |
| Mitigation Rate | Risks successfully mitigated | > 80% |
| Contingency Used | Contingency plans invoked | Minimized |
| New Risks | Newly identified risks | Stable |

### Risk Reporting

```
Weekly Risk Report
==================

Date: 2024-01-15
Project: Example Project

SUMMARY:
- Total Risks: 12
- Critical: 1
- High: 3
- Medium: 5
- Low: 3

NEW RISKS (This Week):
1. RISK-013: API rate limiting concerns (High)
   - Discovered during load testing

CLOSED RISKS:
1. RISK-005: Hiring delay resolved
   - New developer started 2024-01-10

RISKS TO WATCH:
1. RISK-002: Q2 deadline pressure
   - Schedule review scheduled for 2024-01-20

UPCOMING REVIEWS:
- RISK-008: Vendor evaluation (2024-01-22)
- RISK-011: Security audit results (2024-01-25)
```

---

## Common Risk Categories

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Performance below SLA | Medium | High | Load testing, monitoring |
| Security vulnerability | Medium | Very High | Security review, pen testing |
| Integration complexity | High | Medium | Early integration, mocking |
| Technology incompatibility | Low | High | Proof of concept, standards |
| Data loss/corruption | Low | Very High | Backups, redundancy |

### Resource Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Key person departure | Medium | High | Documentation, backup |
| Skill gaps | Medium | Medium | Training, hiring |
| Availability constraints | High | Medium | Buffer, prioritization |
| Team conflict | Low | Medium | Team building, clear roles |
| Hiring delays | Medium | High | Early sourcing, contractors |

### Schedule Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Unrealistic deadlines | High | High | Negotiation, scope control |
| Dependency delays | Medium | High | Parallel work, alternatives |
| Requirements changes | High | Medium | Change control, freezing |
| Rework from bugs | Medium | Medium | Quality gates, testing |
| External approvals | Medium | High | Early engagement, tracking |

### External Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Vendor failure | Low | High | SLA, backup vendors |
| Regulatory changes | Low | Medium | Monitoring, compliance |
| Market changes | Low | Medium | Flexibility, MVP approach |
| Third-party outages | Medium | Medium | Fallbacks, monitoring |

---

## Risk Templates

### Individual Risk Template

```yaml
---
id: "RISK-XXX"
name: ""
category: ""
description: ""
cause: ""
effect: ""
probability: 0.0  # 0.0 to 1.0
impact: 1         # 1-5 scale
score: 0.0
level: ""         # low|medium|high|critical

triggers:
  - ""

indicators:
  - ""

mitigation:
  strategy: ""    # avoid|mitigate|transfer|accept
  actions:
    - ""
  owner: ""
  due_date: ""
  cost: 0

contingency:
  plan: ""
  triggers:
    - ""
  actions:
    - ""
  owner: ""
  resources: ""
  cost: 0

status: ""        # identified|mitigating|monitoring|occurred|closed
created: ""
updated: ""
closed: ""
reviewed: ""
next_review: ""
history:
  - date: ""
    action: ""
    actor: ""
    notes: ""
```

### Risk Register Template

```yaml
risk_register:
  metadata:
    project: ""
    version: ""
    created: ""
    last_updated: ""
    owner: ""

  summary:
    total_risks: 0
    critical: 0
    high: 0
    medium: 0
    low: 0
    closed: 0

  risks: []

  trends:
    - period: ""
      new_risks: 0
      closed_risks: 0
      net_change: 0

  reviews:
    - date: ""
      reviewer: ""
      findings: ""
      actions: ""
```

---

## Best Practices

### Do's

1. **Start Early**
   - Identify risks during project initiation
   - Update risk register throughout project

2. **Involve the Team**
   - All team members can identify risks
   - Diverse perspectives improve coverage

3. **Quantify When Possible**
   - Use numbers for probability and impact
   - Enables objective prioritization

4. **Update Regularly**
   - Review risks at defined intervals
   - Close risks that are no longer relevant

5. **Communicate Transparently**
   - Share risk status with stakeholders
   - Escalate critical risks promptly

### Don'ts

1. **Don't Create Huge Lists**
   - Focus on significant risks only
   - Limit to 15-20 active risks

2. **Don't Set and Forget**
   - Risks evolve throughout project
   - Regular review is essential

3. **Don't Over-react**
   - Not all risks require action
   - Accept low-impact risks

4. **Don't Ignore Warning Signs**
   - Early indicators matter
   - Monitor leading indicators

5. **Don't Blame Individuals**
   - Risk ownership ≠ blame
   - Create safe reporting environment

### Common Mistakes

| Mistake | Impact | Solution |
|---------|--------|----------|
| Identifying too many risks | Diluted focus | Prioritize top 10-15 |
| Not updating regularly | Stale information | Scheduled reviews |
| Lack of ownership | No accountability | Assign clear owners |
| No mitigation plans | Unprepared | Require mitigation for all |
| Ignoring low-probability risks | Surprise failures | Consider high-impact risks |
| Treating risks as certainties | Over-budgeting | Use probability-weighted impacts |

### Risk Management Checklist

- [ ] Risk management plan approved
- [ ] Risk register created
- [ ] Initial risk identification completed
- [ ] All risks assessed and scored
- [ ] Mitigation strategies defined
- [ ] Contingency plans created
- [ ] Risk owners assigned
- [ ] Review cadence established
- [ ] Risk reporting mechanism in place
- [ ] Stakeholder communication plan defined
- [ ] Risks reviewed at each phase gate
- [ ] Lessons learned documented
