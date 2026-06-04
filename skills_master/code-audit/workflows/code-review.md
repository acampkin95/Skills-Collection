# Code Review Audit Workflow

<required_reading>
Before starting, read:
- `references/code-review-checklist.md` — Comprehensive code quality checklist
- `references/architecture-patterns.md` — Recognized design patterns and anti-patterns
- `references/code-smells.md` — Common code quality issues and detection methods
</required_reading>

<process>
## Phase 1: Code Quality Analysis

### Step 1: Automated Code Quality Scanning
**Static Analysis Tools:**
- **SonarQube/SonarCloud**: Multi-language code quality and security
- **CodeClimate**: Maintainability and technical debt analysis
- **ESLint/JSHint**: JavaScript code quality and style
- **Pylint/Flake8**: Python code quality and PEP 8 compliance
- **RuboCop**: Ruby style guide and best practices
- **SpotBugs/PMD**: Java static analysis

**Quality Metrics to Measure:**
- Cyclomatic complexity
- Code duplication percentage
- Lines of code per function/class
- Technical debt ratio
- Test coverage percentage
- Maintainability index

### Step 2: Code Structure and Organization
**Review Areas:**
- Directory and file organization
- Naming conventions consistency
- Module and package structure
- Separation of concerns
- Single responsibility principle adherence
- DRY (Don't Repeat Yourself) principle compliance

**Structure Checklist:**
- ✅ Clear, descriptive naming for variables, functions, and classes
- ✅ Consistent code formatting and style
- ✅ Logical grouping of related functionality
- ✅ Appropriate abstraction levels
- ✅ Minimal code duplication
- ✅ Clear module dependencies and interfaces

## Phase 2: Architecture and Design Review

### Step 1: Design Pattern Analysis
**Common Patterns to Identify:**
- **Creational**: Singleton, Factory, Builder
- **Structural**: Adapter, Decorator, Facade
- **Behavioral**: Observer, Strategy, Command
- **Architectural**: MVC, MVP, MVVM, Clean Architecture

**Anti-Pattern Detection:**
- God objects (overly large classes)
- Spaghetti code (complex, tangled dependencies)
- Shotgun surgery (scattered, coupled changes)
- Dead code (unused methods and variables)
- Magic numbers and hardcoded values

### Step 2: Architecture Compliance
**Review Areas:**
- Layer separation and boundaries
- Dependency direction and inversion
- Interface segregation
- Component cohesion and coupling
- Data flow and state management
- Error handling consistency

**Architecture Checklist:**
- ✅ Clear separation between business logic and infrastructure
- ✅ Proper dependency injection and inversion of control
- ✅ Consistent error handling and logging
- ✅ Appropriate use of design patterns
- ✅ Maintainable and testable code structure
- ✅ Performance considerations in design decisions

## Phase 3: Code Quality Deep Dive

### Step 1: Function and Method Review
**Quality Criteria:**
- Function length (prefer < 20 lines)
- Parameter count (prefer < 5 parameters)
- Return value consistency
- Side effect management
- Pure functions where appropriate
- Clear function contracts

**Method Analysis:**
- Does each method have a single, clear responsibility?
- Are method names descriptive and accurate?
- Are parameters and return types appropriate?
- Is error handling comprehensive and consistent?
- Are edge cases properly handled?

### Step 2: Data Structure and Algorithm Review
**Review Areas:**
- Appropriate data structure selection
- Algorithm efficiency (time and space complexity)
- Memory management practices
- Concurrency and thread safety
- Database query optimization
- Caching strategy effectiveness

**Performance Considerations:**
- Big O notation analysis for critical algorithms
- Memory leak potential identification
- Database N+1 query problems
- Unnecessary computations or network calls
- Appropriate use of caching and memoization

## Phase 4: Testing and Documentation Review

### Step 1: Test Coverage and Quality
**Test Analysis:**
- Unit test coverage percentage
- Integration test completeness
- End-to-end test scenarios
- Test case quality and clarity
- Mock and stub usage appropriateness
- Test data management

**Test Quality Checklist:**
- ✅ Critical business logic is thoroughly tested
- ✅ Edge cases and error conditions are covered
- ✅ Tests are isolated and independent
- ✅ Test names clearly describe what they're testing
- ✅ Tests are maintainable and not brittle
- ✅ Appropriate balance of unit, integration, and e2e tests

### Step 2: Documentation and Comments
**Documentation Review:**
- README completeness and accuracy
- API documentation quality
- Inline comment appropriateness
- Architecture documentation
- Deployment and configuration guides
- Changelog maintenance

**Comment Quality Guidelines:**
- Comments explain "why" not "what"
- Code is self-documenting through clear naming
- Complex algorithms have explanatory comments
- TODO comments are tracked and addressed
- Outdated comments are removed or updated

## Phase 5: Maintainability and Technical Debt

### Step 1: Technical Debt Assessment
**Debt Categories:**
- **Code debt**: Poor code quality, complex implementations
- **Design debt**: Architectural shortcuts, violation of principles
- **Test debt**: Missing or inadequate tests
- **Documentation debt**: Missing or outdated documentation
- **Infrastructure debt**: Outdated tools, environments, or processes

**Debt Prioritization Matrix:**
- **High Impact, Easy Fix**: Quick wins for immediate improvement
- **High Impact, Hard Fix**: Critical items for planned refactoring
- **Low Impact, Easy Fix**: Maintenance tasks for code quality
- **Low Impact, Hard Fix**: Monitor but lower priority

### Step 2: Refactoring Recommendations
**Refactoring Opportunities:**
- Extract method/class for complex functions
- Rename variables/methods for clarity
- Eliminate code duplication
- Simplify conditional logic
- Remove dead code and unused dependencies
- Improve error handling and logging

## Phase 6: Security and Performance Review

### Step 1: Security Code Review
**Security Considerations:**
- Input validation and sanitization
- Output encoding and XSS prevention
- SQL injection prevention
- Authentication and authorization checks
- Secure coding practices
- Sensitive data handling

### Step 2: Performance Analysis
**Performance Areas:**
- Database query efficiency
- Algorithm complexity
- Memory usage patterns
- Network request optimization
- Caching implementation
- Resource cleanup and disposal

## Phase 7: Report Generation and Recommendations

### Step 1: Findings Categorization
**Issue Severity Levels:**
- **Critical**: Security vulnerabilities, system instability
- **High**: Performance issues, major design flaws
- **Medium**: Code quality issues, maintainability concerns
- **Low**: Style issues, minor optimizations

### Step 2: Improvement Roadmap
**Report Structure:**
1. **Executive Summary**
   - Overall code quality assessment
   - Key findings and recommendations
   - Technical debt evaluation

2. **Detailed Analysis**
   - Code quality metrics and trends
   - Specific issues with location and context
   - Security and performance findings
   - Architecture and design review results

3. **Action Plan**
   - Prioritized list of improvements
   - Effort estimates and timelines
   - Risk assessment for each recommendation
   - Quick wins vs. long-term improvements

4. **Best Practices Recommendations**
   - Coding standards and guidelines
   - Process improvements
   - Tool recommendations
   - Training and knowledge sharing suggestions
</process>

<success_criteria>
Code review audit is complete when:
- All automated quality scans have been executed and analyzed
- Manual code review has been conducted across all critical areas
- Architecture and design patterns have been evaluated
- Test coverage and quality have been assessed
- Technical debt has been identified and categorized
- Security and performance considerations have been reviewed
- Comprehensive findings report has been generated
- Actionable improvement roadmap has been created
- Recommendations are prioritized by impact and effort
- Follow-up process is established for tracking improvements
</success_criteria>