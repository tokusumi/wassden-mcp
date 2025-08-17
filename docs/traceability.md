# Traceability Management

wassden provides comprehensive traceability management that ensures full project coherence throughout the Spec-Driven Development lifecycle.

## 🎯 Overview

Maintains bidirectional relationships between:
- **Requirements** (REQ-XX) ↔ **Design Components** (**component-name**)
- **Test Requirements** (TR-XX) ↔ **Test Scenarios** (**test-scenario**)
- **Design Components** & **Test Scenarios** ↔ **Tasks** (TASK-XX-XX)
- **Task Dependencies** within the task hierarchy

## 🔗 Core Features

### 1. Traceability Matrix Generation (`get-traceability`)

Generates comprehensive mapping of all relationships in project specifications.

```bash
# Generate full traceability matrix
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden get-traceability

# Custom spec paths
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden get-traceability \
  --requirementsPath "my-specs/reqs.md" \
  --designPath "my-specs/design.md" \
  --tasksPath "my-specs/tasks.md"
```

**Output Example:**
```
=== Traceability Matrix ===

Requirements Coverage:
- REQ-01: ✅ Referenced in validator
- REQ-02: ✅ Referenced in prompt-generator

Test Requirements Coverage:
- TR-01: ✅ Referenced in test-input-validation
- TR-02: ✅ Referenced in test-prompt-generation

Design Components Coverage:
- validator: ✅ Referenced in TASK-01-01
- prompt-generator: ✅ Referenced in TASK-01-02

Test Scenarios Coverage:
- test-input-validation: ✅ Referenced in TASK-02-01
- test-prompt-generation: ✅ Referenced in TASK-02-02

Coverage Summary:
- Requirements → Design: 100% (2/2)
- Test Requirements → Design: 100% (2/2)
- Design Components → Tasks: 100% (2/2)
- Test Scenarios → Tasks: 100% (2/2)
- Overall Traceability: 100%
```

### 2. Change Impact Analysis (`analyze-changes`)

Analyzes specification changes and provides update guidance for dependent documents.

```bash
# Analyze impact of requirements changes
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden analyze-changes \
  --changedFile "specs/requirements.md" \
  --changeDescription "Added REQ-04 for user authentication"
```

**Output Example:**
```
# 変更影響分析レポート

## 変更内容
- ファイル: specs/requirements.md
- 変更: Added REQ-04 for user authentication

## 影響を受ける設計要素
- なし（この要件はまだ設計に反映されていません）

## 推奨アクション
1. **auth-service** コンポーネントを設計に追加
2. 認証フローの設計を文書化
3. 既存のユーザー管理との統合を検討

## 次のステップ
1. 影響を受ける文書を更新
2. 各文書の validate_* ツールで検証
3. `get_traceability` で全体の整合性を確認
```

## 📋 ID Pattern Specifications

### Requirements (REQ-XX)
- **Pattern**: `REQ-\d{2}` (exactly 2 digits)
- **Valid**: REQ-01, REQ-15, REQ-99
- **Invalid**: REQ-1, REQ-001, REQ-100

### Test Requirements (TR-XX)
- **Pattern**: `TR-\d{2}` (exactly 2 digits)
- **Valid**: TR-01, TR-15, TR-99
- **Invalid**: TR-1, TR-001, TR-100

### Design Components (**component-name**)
- **Pattern**: `**[a-zA-Z0-9_-]+**`
- **Valid**: `**auth-service**`, `**data_processor**`, `**APIGateway**`
- **Invalid**: `**invalid name**` (no spaces), `*single-asterisk*`

### Test Scenarios (**test-scenario**)
- **Pattern**: `**[a-zA-Z0-9_-]*test[a-zA-Z0-9_-]***`
- **Valid**: `**test-input-processing**`, `**user-login-test**`, `**test-api**`
- **Invalid**: `**validation**` (must contain "test"), `**test name**` (no spaces)

### Tasks (TASK-XX-XX-XX)
- **Pattern**: `TASK-\d{2}(?:-\d{2}){0,2}`
- **Valid**: TASK-01, TASK-01-01, TASK-01-01-01
- **Invalid**: TASK-1, TASK-01-1, TASK-01-01-01-01

## 🛠️ How It Works

### Relationship Building Logic

1. **Requirements → Design Mapping**
   - Find REQ-XX in design document
   - Extract **component** names within same content block
   - REQ-XX and **component** must be in proximity (first 500 chars)

2. **Test Requirements → Design Mapping**
   - Find TR-XX in design document's traceability section
   - Extract **test-scenario** names linked to each TR-XX
   - TR-XX and **test-scenario** must be explicitly mapped (TR-01 ⇔ **test-scenario**)

3. **Design → Tasks Mapping**
   - Find **component** and **test-scenario** references in tasks document
   - Extract TASK-XX IDs from sections mentioning the component or test scenario
   - Component/scenario names must exactly match between documents
   - Supports both regular components and test scenarios in DC field

4. **Task Dependencies**
   - Detect `依存: TASK-XX` declarations in task definitions
   - Validate no circular dependencies (DAG requirement)
   - Ensure all dependencies reference valid tasks

### Performance Characteristics
- **Response Time**: <10ms for typical projects (<1000 specs)
- **Memory Usage**: ~1KB per 100 specifications
- **Scalability**: Tested up to 5000 tasks

## 🌟 Practical Example

### MCP Tool Development Specifications

**requirements.md:**
```markdown
## 6. 機能要件（EARS）
- **REQ-01**: システムは、ユーザー入力を受信したとき、情報充足性を分析すること
- **REQ-02**: システムは、情報が十分なとき、requirements.md生成プロンプトを提供すること

## 7. テスト要件（Testing Requirements）
- **TR-01**: 入力処理の正常系・異常系テスト要件
- **TR-02**: プロンプト生成機能のテスト要件
```

**design.md:**
```markdown
## 2. コンポーネント設計
- **prompt-generator**: Agent向けプロンプト生成エンジン [REQ-02]
- **validator**: 生成物品質検証エンジン [REQ-01]

## 6. テスト戦略
- **test-input-validation**: 入力値検証のテストケース
- **test-prompt-generation**: プロンプト生成のテストケース

## 7. トレーサビリティ (必須)
- REQ-01 ⇔ **validator**
- REQ-02 ⇔ **prompt-generator**
- TR-01 ⇔ **test-input-validation**
- TR-02 ⇔ **test-prompt-generation**
```

**tasks.md:**
```markdown
## 2. タスク一覧
- [ ] **TASK-01-01**: Validator実装
  - **REQ**: [REQ-01]
  - **DC**: **validator**
  - **依存**: なし
  
- [ ] **TASK-01-02**: Prompt generator実装
  - **REQ**: [REQ-02]
  - **DC**: **prompt-generator**
  - **依存**: TASK-01-01
  
- [ ] **TASK-02-01**: 入力値検証テスト
  - **REQ**: [TR-01]
  - **DC**: **test-input-validation**
  - **依存**: TASK-01-01
  
- [ ] **TASK-02-02**: プロンプト生成テスト
  - **REQ**: [TR-02]
  - **DC**: **test-prompt-generation**
  - **依存**: TASK-01-02
```

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Empty Traceability Matrix
- **Check**: File paths are correct (default: `specs/*.md`)
- **Verify**: REQ-XX follows exact pattern (REQ-01 not REQ-1)
- **Ensure**: Files exist and are readable

#### Requirements Not Linked to Design
- **Format**: Use `REQ-01 is handled by **auth-service**`
- **Proximity**: REQ-XX and **component** must be in same paragraph
- **Naming**: Component names cannot contain spaces

#### Design Components Not Linked to Tasks
- **Reference**: Use exact component name `**auth-service**`
- **Placement**: Reference before task dependencies section
- **Format**: Include in task description text

#### Circular Task Dependencies
- **Find**: Run `validate-tasks` to identify cycles
- **Fix**: Remove circular `prerequisite:` declarations
- **Restructure**: Break large tasks into smaller units

#### Impact Analysis Shows No Changes
- **Include**: Specific REQ-XX/TASK-XX IDs in change description
- **Format**: Use exact patterns (REQ-01 not requirement 1)
- **Describe**: Mention component names explicitly for design changes

### Debug Commands

```bash
# Test pattern matching
echo "REQ-01 implemented by **auth-service**" | grep -oE "REQ-[0-9]{2}"

# Validate traceability matrix building
uv run python -c "
from wassden.lib import traceability
matrix = traceability.build_traceability_matrix(reqs, design, tasks)
print('Matrix:', matrix)
"

# Verbose impact analysis
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden analyze-changes \
  --changedFile "specs/requirements.md" \
  --changeDescription "Test REQ-01 modification" --verbose
```

## 📊 Best Practices

### Document Structure

#### Requirements Format
```markdown
## REQ-01: Feature Name
The system shall [requirement description].

**Acceptance Criteria:**
- Specific criterion 1
- Specific criterion 2
```

#### Design Format
```markdown
## System Component
REQ-01 is implemented by **component-name**.
The **component-name** handles [functionality].
```

#### Tasks Format
```markdown
## TASK-01: Task Title
Implement functionality for **component-name**.
- prerequisite: TASK-02
```

### Change Management Workflow

```bash
# 1. Baseline before changes
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden get-traceability > baseline.txt

# 2. Make specification changes
vim specs/requirements.md

# 3. Analyze impact
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden analyze-changes \
  --changedFile "specs/requirements.md" \
  --changeDescription "Modified REQ-01 for OAuth support"

# 4. Update dependent documents based on impact analysis
vim specs/design.md
vim specs/tasks.md

# 5. Validate all documents
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-requirements specs/requirements.md
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-design specs/design.md
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-tasks specs/tasks.md

# 6. Verify complete traceability
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden get-traceability
```

### CI/CD Integration

```yaml
# .github/workflows/validate-specs.yml
- name: Validate Traceability
  run: |
    uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-requirements specs/requirements.md
    uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-design specs/design.md
    uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-tasks specs/tasks.md
    uvx --from git+https://github.com/tokusumi/wassden-mcp wassden get-traceability | grep "100%"
```

## 🧪 Testing & Validation

### Test Coverage
- **Unit Tests**: `test_analyze_changes_detailed.py` - Impact analysis accuracy
- **Integration Tests**: `test_handlers_detailed.py` - End-to-end workflows
- **E2E Tests**: `test_mcp_server.py` - MCP protocol integration

### Key Test Scenarios
- New requirement addition → No existing design impact
- Existing requirement modification → Affected components detection
- Design changes → Task impact identification
- Multiple simultaneous changes → Combined impact analysis

### Quality Metrics
- **Accuracy**: 100% dependency detection for properly formatted specs
- **Performance**: <10ms response for <500 specs
- **Coverage**: >95% unit test coverage for traceability modules

## 📚 Related Documentation

- [Requirements Validation](validation/ears.md) - EARS format and ID validation
- [Design Validation](validation/tasks.md) - Design component structure
- [Tasks Validation](validation/traceability.md) - Task dependencies and DAG
- [CLI Reference](cli.md) - Command usage and troubleshooting

---

**Built for systematic spec-driven development with full traceability assurance** 🔗