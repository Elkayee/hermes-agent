---
name: quan-ly-skills
description: Quan ly, tao moi va cap nhat cac ky nang (Skills) trong he thong AGY. Dung khi can nang cap quy trinh, cap nhat mo ta hoac bo sung huong dan moi cho bat ky skill nao.
---

# Huong Dan Ky Nang: Quan Ly Va Cap Nhat Skills

## Muc Dinh
Cung cap cong cu CLI va quy trinh chuan de kiem tra, tao moi va cap nhat noi dung cac Skill trong `.agents/skills/`.

## Quy Trinh Cap Nhat Skill Hien Co

Khi nguoi dung yeu cau sua doi hoac nang cap mot Skill:

1. **Xem danh sach va noi dung skill**:
   ```powershell
   python .agents/scripts/quan_ly_skills.py ls
   python .agents/scripts/quan_ly_skills.py xem <ten-skill>
   ```

2. **Cap nhat mo ta (description)**:
   ```powershell
   python .agents/scripts/quan_ly_skills.py cap-nhat <ten-skill> --mo-ta "Noi dung mo ta moi"
   ```

3. **Bo sung quy trinh moi vao cuoi skill**:
   ```powershell
   python .agents/scripts/quan_ly_skills.py cap-nhat <ten-skill> --them "Cac buoc bo sung..."
   ```

4. **Kiem tra ban sao luu an toan**:
   Moi lan cap nhat, he thong tu dong tao ban sao luu `SKILL.md.bak` trong thu muc cua skill do de phong loi.

### Cap Nhat / Bo Sung Quy Trinh:
Luu y: Luon chay bo harness kiem thu sau khi sua skill.
