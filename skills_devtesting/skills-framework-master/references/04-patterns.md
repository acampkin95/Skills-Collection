# Common Skill Patterns

## Pattern 1: Sequential Workflow Orchestration

Use when users need multi-step processes in specific order.

```markdown
## Workflow: Onboard New Customer

### Step 1: Create Account
Call MCP tool: `create_customer`
Wait for: account confirmation

### Step 2: Setup Payment
Call MCP tool: `setup_payment_method`
Wait for: payment verification

### Step 3: Create Subscription
Call MCP tool: `create_subscription`
Parameters: plan_id, customer_id

### Step 4: Send Welcome Email
Call MCP tool: `send_email`
Template: welcome_email_template
```

Key techniques:
- Explicit step ordering
- Dependencies between steps
- Validation at each stage
- Rollback instructions for failures

## Pattern 2: Multi-MCP Coordination

Use when workflows span multiple services.

Example: Design-to-development handoff

```
Phase 1: Design Export (Figma MCP)
- Export assets
- Generate specs
- Create manifest

Phase 2: Asset Storage (Drive MCP)
- Create folder
- Upload assets
- Generate links

Phase 3: Task Creation (Linear MCP)
- Create tasks
- Attach links
- Assign team

Phase 4: Notification (Slack MCP)
- Post summary
- Include links
```

## Pattern 3: Iterative Refinement

Use when output quality improves with iteration.

```
Step 1: Generate initial draft
Step 2: Validation and quality check
Step 3: Refinement loop
  - Address issues
  - Regenerate sections
  - Re-validate
  - Repeat until quality threshold
Step 4: Finalization
```

Key techniques:
- Explicit quality criteria
- Iterative improvement
- Validation scripts
- Know when to stop

## Pattern 4: Context-Aware Tool Selection

Use when same outcome, different tools depending on context.

```
Decision Tree:
1. Check file type and size
2. Determine best storage:
   - Large files (>10MB): cloud storage
   - Collaborative docs: Notion
   - Code files: GitHub
   - Temp files: local
3. Execute storage call
4. Provide context to user
```

## Pattern 5: Domain-Specific Intelligence

Use when skill adds specialized knowledge beyond tool access.

Example: Payment processing with compliance

```
Before Processing:
- Check sanctions lists
- Verify jurisdiction allowances
- Assess risk level

During Processing:
- Apply fraud checks
- Process transaction (if compliant)
- Flag for review (if not)

After Processing:
- Log compliance checks
- Record decisions
- Generate audit report
```
