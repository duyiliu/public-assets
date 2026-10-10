# GT Racing — 3D assets

原创黑红 GT 赛车模型，程序化网格，约 2.17 万个三角面和 18 种材质。可在 Blender、Unity、Three.js 中导入。

- [模型（GLB）](./gt_racecar_3d.glb)
- [交互预览（HTML）](./gt_racecar_viewer.html)
- [生成脚本（Python）](./gt_racecar_generator.py)

生成方式：

```sh
python -m pip install numpy trimesh pillow
python gt_racecar_generator.py
```

提交 `gt_racecar_generator.py` 后，仓库的 GitHub Actions 构建工作流会重新生成并提交 `gt_racecar_3d.glb`。
