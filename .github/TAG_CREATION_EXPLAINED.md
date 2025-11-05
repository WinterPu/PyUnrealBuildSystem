# Tag 创建机制说明

## 问题发现

### 原始问题
运行工作流后，发现 **tag 没有被创建**。

### 根本原因

之前的实现依赖 `softprops/action-gh-release@v1` 来创建 tag，但这个 action 的行为是：

1. **如果 tag 不存在**：action 会尝试创建 tag
2. **但是**：在某些情况下，tag 可能不会被正确创建或推送
3. **问题**：没有明确的 tag 创建和推送步骤

## 解决方案

### 新增步骤：明确创建和推送 tag

在创建 Release 之前，添加了一个新的步骤来**明确创建和推送 tag**：

```yaml
- name: Create and push tag
  run: |
    echo "🏷️ Creating tag ${{ inputs.tag_name }}..."
    
    # Configure git
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    
    # Create annotated tag at current HEAD
    git tag -a "${{ inputs.tag_name }}" -m "Release ${{ inputs.tag_name }}"
    
    echo "✓ Tag created locally"
    
    # Push tag to remote
    git push origin "${{ inputs.tag_name }}"
    
    echo "✓ Tag pushed to remote"
    echo "🎯 Tag ${{ inputs.tag_name }} created at commit $(git rev-parse HEAD)"
```

## 工作流执行顺序

### 更新后的完整流程

```
1. ✅ Validate inputs（验证输入）
   └─ 检查 tag 名称格式

2. ✅ Checkout repository（检出代码）
   └─ 获取完整历史（fetch-depth: 0）

3. ✅ Check if tag exists（检查 tag 是否存在）
   ├─ 如果存在且 delete_existing=true → 删除
   └─ 如果存在且 delete_existing=false → 报错退出

4. ✅ Delete existing release and tag（可选）
   ├─ 删除远程 Release
   ├─ 删除远程 tag
   └─ 删除本地 tag

5. ✅ Generate changelog（生成 Changelog）
   ├─ 自动检测或使用指定的 tag 进行对比
   └─ 生成 commit 列表和统计信息

6. ✅ Download files（下载文件）
   └─ 从提供的 URL 下载文件

7. 🆕 Create and push tag（创建并推送 tag）⭐ 新增步骤
   ├─ 在当前 HEAD 创建 annotated tag
   ├─ 推送到远程仓库
   └─ 显示 tag 和 commit 信息

8. ✅ Create GitHub Release（创建 Release）
   ├─ 使用已创建的 tag
   ├─ 上传文件
   └─ 设置 draft/prerelease 状态

9. ✅ Create release summary（生成摘要）
   └─ 在 Actions Summary 显示详细信息

10. ✅ Cleanup（清理）
    └─ 删除临时文件
```

## Tag 创建详解

### Annotated Tag vs Lightweight Tag

工作流创建的是 **Annotated Tag**（带注释的标签）：

```bash
# Annotated tag（推荐）
git tag -a "v1.0.0" -m "Release v1.0.0"

# Lightweight tag（不推荐）
git tag "v1.0.0"
```

**为什么使用 Annotated Tag？**

| 特性 | Annotated Tag | Lightweight Tag |
|------|--------------|-----------------|
| 包含标签信息 | ✅ 是 | ❌ 否 |
| 包含标签者 | ✅ 是 | ❌ 否 |
| 包含日期 | ✅ 是 | ❌ 否 |
| 包含消息 | ✅ 是 | ❌ 否 |
| Git 对象 | ✅ 完整对象 | ❌ 引用 |
| 推荐用于发布 | ✅ 是 | ❌ 否 |

### Tag 创建在什么 Commit 上？

Tag 创建在 **`target_branch` 的当前 HEAD**：

```yaml
# 示例 1：在 main 分支的最新 commit
tag_name: v1.0.0
target_branch: main
# → Tag 指向 main 的 HEAD

# 示例 2：在 develop 分支的最新 commit
tag_name: v2.0.0-beta
target_branch: develop
# → Tag 指向 develop 的 HEAD
```

### 验证 Tag 是否创建成功

运行后，可以在以下位置验证：

#### 1. GitHub 网页界面
```
https://github.com/WinterPu/PyUnrealBuildSystem/tags
```

#### 2. 本地命令行
```bash
# 获取所有 tags
git fetch --tags

# 列出所有 tags
git tag -l

# 查看特定 tag 的详细信息
git show v1.0.0
```

#### 3. Actions 日志
查看工作流运行日志中的 "Create and push tag" 步骤：

```
🏷️ Creating tag v1.0.0...
✓ Tag created locally
✓ Tag pushed to remote
🎯 Tag v1.0.0 created at commit abc1234567890...
```

## Draft 和 Pre-release 对 Tag 的影响

### 重要说明

✅ **Tag 总是会被创建**，无论以下设置如何：

| 参数设置 | Tag 创建 | Tag 可见性 | Release 状态 | Release 可见性 |
|---------|---------|-----------|-------------|--------------|
| `prerelease: false`<br>`draft: false` | ✅ 创建 | 🌍 公开 | 正式发布 | 🌍 所有人可见 |
| `prerelease: true`<br>`draft: false` | ✅ 创建 | 🌍 公开 | 预发布 | 🌍 所有人可见 |
| `prerelease: false`<br>`draft: true` | ✅ 创建 | 🌍 公开 | 草稿 | 👥 仅协作者 |
| `prerelease: true`<br>`draft: true` | ✅ 创建 | 🌍 公开 | 预发布草稿 | 👥 仅协作者 |

### 关键理解

1. **Tag 是 Git 对象，创建后就是公开的**
   - 任何人都可以通过 `git fetch --tags` 获取
   - Tag 不受 GitHub Release 的 draft 状态影响

2. **Draft 只影响 Release 的可见性**
   - Release 为 draft 时，只有仓库协作者能看到
   - 但 Tag 仍然是公开的

3. **Pre-release 是 Release 的一个标记**
   - 不会作为"最新版本"展示
   - 在 Releases 页面有明显的标识

## 使用场景示例

### 场景 1: 标准发布流程

```yaml
tag_name: v1.0.0
target_branch: main
prerelease: false
draft: false
```

**执行过程：**
1. 在 main 分支的 HEAD 创建 tag `v1.0.0`
2. 推送 tag 到远程
3. 创建公开的正式 Release
4. 上传文件
5. 所有人可见

**结果：**
- ✅ Tag: `v1.0.0`（公开）
- ✅ Release: 正式版本（公开）
- ✅ 标记为"Latest Release"

### 场景 2: Beta 版本

```yaml
tag_name: v2.0.0-beta
target_branch: develop
prerelease: true
draft: false
```

**执行过程：**
1. 在 develop 分支的 HEAD 创建 tag `v2.0.0-beta`
2. 推送 tag 到远程
3. 创建预发布 Release
4. 上传文件

**结果：**
- ✅ Tag: `v2.0.0-beta`（公开）
- ✅ Release: 标记为"Pre-release"（公开）
- ⚠️ 不会作为"Latest Release"

### 场景 3: 需要审查的发布

```yaml
tag_name: v1.5.0
target_branch: main
prerelease: false
draft: true
```

**执行过程：**
1. 在 main 分支的 HEAD 创建 tag `v1.5.0`
2. 推送 tag 到远程（**公开可见**）
3. 创建草稿 Release（仅协作者可见）
4. 上传文件

**结果：**
- ✅ Tag: `v1.5.0`（**公开可见**）
- ⚠️ Release: 草稿状态（仅协作者）
- 📝 需要手动点击"Publish"才能公开

**注意：** 虽然 Release 是草稿，但 **Tag 已经公开**！

## 常见问题

### Q1: Tag 创建在哪个 commit？

**A:** Tag 创建在 `target_branch` 分支的 **当前最新 commit（HEAD）**。

工作流会先 checkout 指定分支，然后在 HEAD 创建 tag。

### Q2: 如何验证 Tag 创建成功？

**A:** 三种方式：

1. **GitHub 网页**：查看 Tags 页面
2. **Actions 日志**：查看 "Create and push tag" 步骤
3. **本地命令**：`git fetch --tags && git tag -l`

### Q3: Tag 已存在怎么办？

**A:** 有两种处理方式：

**方式 1：自动删除并重建**
```yaml
tag_name: v1.0.0
delete_existing: true  # 自动删除旧 tag
```

**方式 2：手动删除**
```bash
# 删除本地 tag
git tag -d v1.0.0

# 删除远程 tag
git push origin --delete v1.0.0
```

### Q4: Draft Release 的 Tag 是公开的吗？

**A:** ✅ **是的！**

- Tag 是 Git 对象，一旦推送就是公开的
- Draft 只影响 Release 的可见性
- 如果不想公开 Tag，不要运行工作流

### Q5: 可以在旧的 commit 上创建 Tag 吗？

**A:** 当前工作流不支持。Tag 总是创建在分支的 HEAD。

如果需要在特定 commit 创建 tag，建议：
```bash
# 手动操作
git tag -a v1.0.0 <commit-hash> -m "Release v1.0.0"
git push origin v1.0.0
```

### Q6: Tag 命名有什么建议？

**A:** 推荐使用语义化版本：

```
v主版本.次版本.修订号[-预发布标识]

示例：
v1.0.0        - 正式版
v1.0.0-beta   - Beta 版
v1.0.0-rc.1   - Release Candidate
v1.0.0-alpha  - Alpha 版
v2.0.0-dev    - 开发版
```

### Q7: 删除 Tag 后能重新创建吗？

**A:** ✅ 可以

设置 `delete_existing: true` 会自动：
1. 删除远程 Release
2. 删除远程 Tag
3. 删除本地 Tag
4. 重新创建和推送

### Q8: Tag 的作者是谁？

**A:** Tag 的作者是 `github-actions[bot]`

工作流中配置：
```bash
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
```

可以在 GitHub 上看到 Tag 由 GitHub Actions 创建。

## 最佳实践

### ✅ 推荐做法

1. **使用语义化版本号**
   ```yaml
   tag_name: v1.2.3
   ```

2. **正式版本在 main 分支**
   ```yaml
   tag_name: v1.0.0
   target_branch: main
   ```

3. **测试版本在 develop 分支**
   ```yaml
   tag_name: v2.0.0-beta
   target_branch: develop
   prerelease: true
   ```

4. **重要版本使用 Draft 审查**
   ```yaml
   tag_name: v2.0.0
   draft: true  # 审查后再发布
   ```

### ❌ 避免的做法

1. **不要在草稿 Release 中使用正式版本号**
   ```yaml
   # 不推荐：Tag 公开但 Release 不公开
   tag_name: v1.0.0
   draft: true
   ```

2. **不要频繁删除和重建 Tag**
   ```yaml
   # Tag 是永久性的，不要随意修改
   delete_existing: true
   ```

3. **不要在错误的分支创建 Tag**
   ```yaml
   # 确保分支正确
   target_branch: main  # 检查是否是正确的分支
   ```

## 调试 Tag 创建问题

### 检查清单

如果 Tag 没有创建，检查：

1. ✅ **工作流是否成功执行**
   - 查看 Actions 日志
   - 检查是否有错误

2. ✅ **"Create and push tag" 步骤是否执行**
   - 查看该步骤的输出
   - 确认是否显示"Tag pushed to remote"

3. ✅ **是否有权限问题**
   - 检查 `permissions: contents: write` 是否设置
   - 这通常是自动的

4. ✅ **Tag 名称是否冲突**
   - 检查 Tag 是否已存在
   - 如果存在，设置 `delete_existing: true`

5. ✅ **网络问题**
   - GitHub Actions 的网络通常很稳定
   - 如果失败会在日志中显示

### 查看详细日志

在 Actions 页面：
```
1. 进入工作流运行
2. 点击 "Create and push tag" 步骤
3. 查看完整输出
4. 确认是否有错误信息
```

## 总结

### 关键要点

1. ✅ **Tag 现在明确创建**
   - 新增了专门的步骤来创建和推送 tag
   - 不再依赖 Release action 的隐式创建

2. ✅ **Tag 总是公开的**
   - 无论 draft 或 prerelease 设置如何
   - 一旦推送就可以被获取

3. ✅ **Tag 创建在 HEAD**
   - 基于 `target_branch` 的最新 commit
   - 确保 checkout 正确的分支

4. ✅ **可以验证创建**
   - 通过 Actions 日志
   - 通过 GitHub Tags 页面
   - 通过 git 命令

### 相关文档

- [Release 工作流使用指南](./RELEASE_WORKFLOW_GUIDE.md)
- [Tag 和 Changelog FAQ](./TAG_AND_CHANGELOG_FAQ.md)
- [配置示例](./EXAMPLES.md)

---

**有问题？** [提交 Issue](https://github.com/WinterPu/PyUnrealBuildSystem/issues)
