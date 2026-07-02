#!/bin/bash
set -euo pipefail

echo "🔍 Validating SKILL.md files..."

errors=0

# name 合法正则（与 AGENTS.md 一致）：仅小写字母/数字/连字符，不能含 /
NAME_RE='^[a-z0-9]+(-[a-z0-9]+)*$'

for f in packages/*/SKILL.md; do
  [ -f "$f" ] || continue
  dir_name=$(basename "$(dirname "$f")")

  # 1) 开头分隔符
  if ! head -1 "$f" | grep -q '^---[[:space:]]*$'; then
    echo "  ❌ $dir_name: 第一行不是 frontmatter 开始分隔符 ---"
    errors=$((errors + 1))
    continue
  fi

  # 2) 结束分隔符（第一个 --- 之后出现的第一个 ---）
  closing=$(awk 'NR>1 && /^---[[:space:]]*$/{found=1; exit} END{print (found?1:0)}' "$f")
  if [ "$closing" != "1" ]; then
    echo "  ❌ $dir_name: 缺少 frontmatter 结束分隔符 ---"
    errors=$((errors + 1))
    continue
  fi

  # 提取 frontmatter 内容（不含首尾 ---）
  fm=$(awk 'NR==1{next} /^---[[:space:]]*$/{exit} {print}' "$f")

  # 3) name 字段：存在 / 正则 / 与目录名一致
  name_val=$(printf '%s\n' "$fm" | sed -n 's/^name:[[:space:]]*//p' | head -1 | sed 's/^"\(.*\)"$/\1/' | sed 's/[[:space:]]*$//')
  if [ -z "$name_val" ]; then
    echo "  ❌ $dir_name: frontmatter 缺少 name 字段"
    errors=$((errors + 1))
    continue
  fi
  if ! printf '%s' "$name_val" | grep -Eq "$NAME_RE"; then
    echo "  ❌ $dir_name: name '$name_val' 不符合正则 $NAME_RE（仅小写字母/数字/连字符，不能含 /）"
    errors=$((errors + 1))
    continue
  fi
  if [ "$dir_name" != "$name_val" ]; then
    echo "  ❌ $dir_name: name 与目录名不一致（frontmatter=$name_val）"
    errors=$((errors + 1))
    continue
  fi

  # 4) description 字段：必填
  desc_val=$(printf '%s\n' "$fm" | sed -n 's/^description:[[:space:]]*//p' | head -1)
  if [ -z "$desc_val" ]; then
    echo "  ❌ $dir_name: frontmatter 缺少 description 字段"
    errors=$((errors + 1))
    continue
  fi

  echo "  ✅ $dir_name"
done

if [ $errors -gt 0 ]; then
  echo ""
  echo "❌ Validation failed: $errors error(s)"
  exit 1
fi

echo ""
echo "✅ All SKILL.md files valid"
