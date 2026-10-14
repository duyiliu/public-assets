# Dream Team · IP Asset Library

角色 IP 素材的统一存储位置：`duyiliu/public-assets/ip/dream-team/`。

## 结构

```text
ip/dream-team/
├── README.md
├── team/design/                     # 团队合照、组合设定
└── characters/
    ├── wukong/
    │   ├── design/                  # 三视图、表情、动作、配件等设计稿
    │   ├── source/                  # Blender 源工程 .blend、生成脚本
    │   ├── models/                  # 导出 .glb/.fbx/.ply
    │   ├── textures/                # 贴图及纹理
    │   └── preview/
    │       ├── mesh/index.html      # 已迁入：程序化网格预览
    │       └── splat/index.html     # 已迁入：表面高斯点采样实验
    ├── princess/design/             # 粉色公主
    └── pipi/design/                 # 熊猫 PiPi
```

## 已迁移
- [孙悟空网格预览](characters/wukong/preview/mesh/index.html)
- [孙悟空高斯点实验](characters/wukong/preview/splat/index.html)

两个页面仅为独立 HTML 预览，不能代替可编辑的 GLB 或 Blender 工程；高斯点实验不是完整的多视角训练 3DGS。

## 尚待上传
此前整理的 Dream Team ZIP 中的设计图片、GLB、PLY、Blender 工程素材包尚未验证上传到本仓库，**不要把目录规划当作已上传的素材**。

请按角色将二进制资产解压并上传对应文件夹。大尺寸 Blender 文件和纹理建议使用 Git LFS（需确认托管配额）。上传后检查文件可下载、可在 Blender 导入且网页展示正常。

## 约定
- 同一角色的设计稿、源工程、导出模型、预览放在同一个角色目录下。
- `source/` 保存可重建工程；`models/` 保存版本化交付模型。
- 预览文件不应与模型源数据混淆。
- 赛车项目 `neon-city-racing` 保留游戏相关代码，IP 素材归属于本仓库。
